"""Bandwidth monitoring API routes"""
from flask import Blueprint, jsonify, request
from flask_login import login_required
from services.bandwidth_service import BandwidthService
from services.mikrotik_service import MikrotikService
from datetime import datetime
from extensions import csrf

# Create blueprint for bandwidth routes
bandwidth_bp = Blueprint('bandwidth', __name__, url_prefix='/api/bandwidth')


@bandwidth_bp.route('/all', methods=['GET'])
@login_required
def get_all_bandwidth():
    """
    Get bandwidth data for all clients.
    
    Returns JSON with bandwidth data including RX/TX rates and online status.
    
    Requirements: 2.1, 6.1, 6.4
    """
    try:
        bandwidth_data = BandwidthService.get_all_bandwidth()
        
        return jsonify({
            'success': True,
            'data': bandwidth_data,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@bandwidth_bp.route('/total', methods=['GET'])
@login_required
def get_total_bandwidth():
    """
    Get aggregated total bandwidth with congestion status.
    
    Returns JSON with total RX/TX, active sessions, and congestion indicators.
    
    Requirements: 3.1, 3.2, 3.5
    """
    try:
        total_data = BandwidthService.get_total_bandwidth()
        
        return jsonify({
            'success': True,
            'data': total_data,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@bandwidth_bp.route('/set-limit', methods=['POST'])
@login_required
@csrf.exempt
def set_bandwidth_limit():
    """
    Set bandwidth limit for a specific client.
    
    Expects JSON with:
    - client_id: Client ID
    - pppoe_username: PPPoE username
    - download_limit: Download limit in Mbps
    - upload_limit: Upload limit in Mbps
    
    Returns JSON with success status.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        client_id = data.get('client_id')
        pppoe_username = data.get('pppoe_username')
        download_limit = data.get('download_limit')
        upload_limit = data.get('upload_limit')
        
        if not all([client_id, pppoe_username, download_limit, upload_limit]):
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400
        
        # Convert Mbps to bps for Mikrotik (Mikrotik uses bits per second)
        download_bps = int(float(download_limit) * 1000000)
        upload_bps = int(float(upload_limit) * 1000000)
        
        # Get Mikrotik configuration from environment
        from config import Config
        
        # Create Mikrotik service instance and set bandwidth limit
        mikrotik = MikrotikService(
            host=Config.MIKROTIK_HOST,
            username=Config.MIKROTIK_USER,
            password=Config.MIKROTIK_PASSWORD,
            port=8728
        )
        
        with mikrotik:
            success = mikrotik.set_bandwidth_limit(
                pppoe_username, 
                download_bps, 
                upload_bps
            )
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Bandwidth limit set to {download_limit}/{upload_limit} Mbps',
                'data': {
                    'client_id': client_id,
                    'pppoe_username': pppoe_username,
                    'download_mbps': download_limit,
                    'upload_mbps': upload_limit
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to set bandwidth limit in Mikrotik'
            }), 500
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
