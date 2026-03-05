"""Bandwidth monitoring service for ISP network management"""
from datetime import datetime
from typing import Optional, Dict, List
from models.client import Client
from services.mikrotik_service import MikrotikService
from config import Config


class BandwidthService:
    """Service for bandwidth monitoring and aggregation"""
    
    # In-memory cache for bandwidth data
    _bandwidth_cache = {
        'data': None,
        'timestamp': None,
        'ttl': 5  # seconds
    }
    
    @staticmethod
    def _is_cache_valid() -> bool:
        """
        Check if cached bandwidth data is still valid.
        
        Returns:
            bool: True if cache is valid, False otherwise
        """
        if BandwidthService._bandwidth_cache['data'] is None:
            return False
        
        if BandwidthService._bandwidth_cache['timestamp'] is None:
            return False
        
        elapsed = (datetime.utcnow() - BandwidthService._bandwidth_cache['timestamp']).total_seconds()
        return elapsed < BandwidthService._bandwidth_cache['ttl']
    
    @staticmethod
    def _clear_cache():
        """Clear the bandwidth cache"""
        BandwidthService._bandwidth_cache['data'] = None
        BandwidthService._bandwidth_cache['timestamp'] = None
    
    @staticmethod
    def _store_in_cache(data: List[Dict]):
        """
        Store bandwidth data in cache.
        
        Args:
            data: List of bandwidth data dictionaries
        """
        BandwidthService._bandwidth_cache['data'] = data
        BandwidthService._bandwidth_cache['timestamp'] = datetime.utcnow()
    
    @staticmethod
    def _get_from_cache() -> Optional[List[Dict]]:
        """
        Get bandwidth data from cache if valid.
        
        Returns:
            List of bandwidth data or None if cache invalid
        """
        try:
            if BandwidthService._is_cache_valid():
                data = BandwidthService._bandwidth_cache['data']
                # Validate structure
                if isinstance(data, list):
                    return data
                else:
                    BandwidthService._clear_cache()
        except Exception:
            BandwidthService._clear_cache()
        
        return None

    @staticmethod
    def convert_bytes_to_mbps(bytes_per_sec: int) -> float:
        """
        Convert bandwidth from bytes per second to Mbps.
        
        Formula: mbps = (bytes_per_sec * 8) / (1024 * 1024)
        
        Args:
            bytes_per_sec: Bandwidth in bytes per second
            
        Returns:
            float: Bandwidth in Mbps (megabits per second)
        """
        if bytes_per_sec < 0:
            return 0.0
        
        # Convert bytes to bits (multiply by 8)
        # Convert to megabits (divide by 1024 * 1024)
        mbps = (bytes_per_sec * 8) / (1024 * 1024)
        
        # Round to 2 decimal places
        return round(mbps, 2)

    @staticmethod
    def get_client_bandwidth(client_id: int) -> dict:
        """
        Get bandwidth data for a specific client.
        
        Args:
            client_id: Client database ID
            
        Returns:
            dict: {
                'client_id': int,
                'pppoe_username': str,
                'is_online': bool,
                'rx_mbps': float,
                'tx_mbps': float,
                'last_updated': datetime
            }
        """
        from extensions import db
        
        # Query client from database by ID
        client = db.session.get(Client, client_id)
        
        if not client:
            raise ValueError(f"Client with ID {client_id} not found")
        
        # Get PPPoE username from client record
        pppoe_username = client.pppoe_username
        
        # Initialize result with offline status
        result = {
            'client_id': client_id,
            'pppoe_username': pppoe_username,
            'is_online': False,
            'rx_mbps': 0.0,
            'tx_mbps': 0.0,
            'last_updated': datetime.utcnow()
        }
        
        try:
            # Fetch bandwidth data from MikrotikService
            mikrotik = MikrotikService(
                host=Config.MIKROTIK_HOST,
                username=Config.MIKROTIK_USER,
                password=Config.MIKROTIK_PASSWORD
            )
            
            bandwidth_data = mikrotik.get_session_bandwidth(pppoe_username)
            
            # Return formatted bandwidth data with online status
            if bandwidth_data:
                result['is_online'] = True
                result['rx_mbps'] = bandwidth_data['rx_mbps']
                result['tx_mbps'] = bandwidth_data['tx_mbps']
        
        except Exception as e:
            # Log error but return offline status instead of raising
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error fetching bandwidth for client {client_id}: {str(e)}")
        
        return result

    @staticmethod
    def get_all_bandwidth() -> List[Dict]:
        """
        Get bandwidth data for all clients.
        Uses caching to minimize Mikrotik API calls.
        
        Returns:
            list[dict]: List of bandwidth data per client
        """
        from extensions import db
        
        # Check cache validity first
        cached_data = BandwidthService._get_from_cache()
        if cached_data is not None:
            return cached_data
        
        # If cache miss, fetch from MikrotikService
        try:
            mikrotik = MikrotikService(
                host=Config.MIKROTIK_HOST,
                username=Config.MIKROTIK_USER,
                password=Config.MIKROTIK_PASSWORD
            )
            
            # Fetch all sessions bandwidth
            sessions_bandwidth = mikrotik.get_all_sessions_bandwidth()
            
            # Create a mapping of username to bandwidth data
            bandwidth_map = {
                session['username']: session
                for session in sessions_bandwidth
            }
            
            # Match sessions to database clients
            clients = Client.query.all()
            result = []
            
            for client in clients:
                bandwidth_data = bandwidth_map.get(client.pppoe_username)
                
                if bandwidth_data:
                    # Client is online
                    result.append({
                        'client_id': client.id,
                        'pppoe_username': client.pppoe_username,
                        'full_name': client.full_name,
                        'is_online': True,
                        'rx_mbps': bandwidth_data['rx_mbps'],
                        'tx_mbps': bandwidth_data['tx_mbps']
                    })
                else:
                    # Client is offline
                    result.append({
                        'client_id': client.id,
                        'pppoe_username': client.pppoe_username,
                        'full_name': client.full_name,
                        'is_online': False,
                        'rx_mbps': 0.0,
                        'tx_mbps': 0.0
                    })
            
            # Store results in cache
            BandwidthService._store_in_cache(result)
            
            return result
        
        except Exception as e:
            # Log error and return empty list
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error fetching all bandwidth data: {str(e)}")
            return []

    @staticmethod
    def calculate_congestion_status(current: float, threshold: float) -> str:
        """
        Calculate congestion status based on threshold.
        
        Args:
            current: Current bandwidth usage in Mbps
            threshold: Configured threshold in Mbps
            
        Returns:
            str: 'normal' (<80%), 'warning' (80-100%), 'critical' (>100%)
        """
        if threshold <= 0:
            return 'normal'
        
        # Calculate percentage of threshold
        percentage = (current / threshold) * 100
        
        # Return 'normal' if < 80%
        if percentage < 80:
            return 'normal'
        # Return 'warning' if 80-100%
        elif percentage <= 100:
            return 'warning'
        # Return 'critical' if > 100%
        else:
            return 'critical'

    @staticmethod
    def get_total_bandwidth() -> dict:
        """
        Get aggregated total bandwidth for ISP.
        
        Returns:
            dict: {
                'total_rx_mbps': float,
                'total_tx_mbps': float,
                'active_sessions': int,
                'threshold_rx': float,
                'threshold_tx': float,
                'congestion_status_rx': str,
                'congestion_status_tx': str
            }
        """
        # Get all bandwidth data
        all_bandwidth = BandwidthService.get_all_bandwidth()
        
        # Sum RX values for total RX
        total_rx = sum(
            client['rx_mbps']
            for client in all_bandwidth
            if client['is_online']
        )
        
        # Sum TX values for total TX
        total_tx = sum(
            client['tx_mbps']
            for client in all_bandwidth
            if client['is_online']
        )
        
        # Count active sessions
        active_sessions = sum(
            1 for client in all_bandwidth
            if client['is_online']
        )
        
        # Get thresholds from config
        threshold_rx = Config.BANDWIDTH_THRESHOLD_RX
        threshold_tx = Config.BANDWIDTH_THRESHOLD_TX
        
        # Calculate congestion status for RX and TX
        congestion_status_rx = BandwidthService.calculate_congestion_status(
            total_rx, threshold_rx
        )
        congestion_status_tx = BandwidthService.calculate_congestion_status(
            total_tx, threshold_tx
        )
        
        # Return aggregated data with thresholds
        return {
            'total_rx_mbps': round(total_rx, 2),
            'total_tx_mbps': round(total_tx, 2),
            'active_sessions': active_sessions,
            'threshold_rx': threshold_rx,
            'threshold_tx': threshold_tx,
            'congestion_status_rx': congestion_status_rx,
            'congestion_status_tx': congestion_status_tx
        }
