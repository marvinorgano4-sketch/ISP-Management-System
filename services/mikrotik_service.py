"""Mikrotik RouterOS API integration service"""
import logging
import time
from typing import Optional
from routeros_api import RouterOsApiPool
from routeros_api.exceptions import RouterOsApiConnectionError, RouterOsApiCommunicationError

logger = logging.getLogger(__name__)


class MikrotikService:
    """Service for interacting with Mikrotik RouterOS API"""
    
    def __init__(self, host: str, username: str, password: str, port: int = 8728):
        """
        Initialize Mikrotik service with connection credentials.
        
        Args:
            host: Mikrotik router IP address or hostname
            username: RouterOS API username
            password: RouterOS API password
            port: RouterOS API port (default: 8728)
        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self._connection = None
        self._api = None
    
    def connect(self, max_retries: int = 3, retry_delay: int = 2) -> bool:
        """
        Establish connection to Mikrotik router with retry logic.
        
        Args:
            max_retries: Maximum number of connection attempts (default: 3)
            retry_delay: Initial delay between retries in seconds (default: 2)
        
        Returns:
            bool: True if connection successful, False otherwise
        
        Raises:
            RouterOsApiConnectionError: If connection fails after all retries
        """
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            try:
                if self._connection is None:
                    logger.info(f"Attempting to connect to Mikrotik at {self.host}:{self.port} (attempt {attempt}/{max_retries})")
                    
                    self._connection = RouterOsApiPool(
                        self.host,
                        username=self.username,
                        password=self.password,
                        port=self.port,
                        plaintext_login=True
                    )
                    self._api = self._connection.get_api()
                    
                    # Validate connection by testing with a simple API call
                    try:
                        identity_resource = self._api.get_resource('/system/identity')
                        identity = identity_resource.get()
                        router_name = identity[0].get('name', 'Unknown') if identity else 'Unknown'
                        logger.info(f"Successfully connected to Mikrotik '{router_name}' at {self.host}:{self.port}")
                    except Exception as validation_error:
                        logger.warning(f"Connection established but validation failed: {str(validation_error)}")
                        # Connection is established even if validation fails
                    
                return True
                
            except RouterOsApiConnectionError as e:
                last_error = e
                error_msg = str(e).lower()
                
                # Determine error type for better messaging
                if 'authentication' in error_msg or 'login' in error_msg or 'password' in error_msg:
                    error_type = "Authentication failed"
                    suggestion = "Please verify the username and password are correct and the user has API access permissions"
                elif 'timeout' in error_msg or 'timed out' in error_msg:
                    error_type = "Connection timeout"
                    suggestion = "Please check network connectivity and ensure the Mikrotik router is reachable"
                elif 'refused' in error_msg or 'connection refused' in error_msg:
                    error_type = "Connection refused"
                    suggestion = "Please ensure the API service is enabled on the Mikrotik router and port {self.port} is accessible"
                else:
                    error_type = "Connection error"
                    suggestion = "Please check router configuration and network connectivity"
                
                logger.error(f"Connection attempt {attempt}/{max_retries} failed: {error_type} - {str(e)}")
                
                # Don't retry on authentication errors
                if 'authentication' in error_msg or 'login' in error_msg or 'password' in error_msg:
                    logger.error(f"Authentication error detected - not retrying. {suggestion}")
                    raise RouterOsApiConnectionError(
                        f"Failed to connect to Mikrotik at {self.host}:{self.port} - {error_type}. {suggestion}"
                    )
                
                # Retry with exponential backoff for other errors
                if attempt < max_retries:
                    delay = retry_delay * (2 ** (attempt - 1))  # Exponential backoff: 2s, 4s, 8s
                    logger.info(f"Retrying in {delay} seconds... ({suggestion})")
                    time.sleep(delay)
                else:
                    logger.error(f"All {max_retries} connection attempts failed. {suggestion}")
                    raise RouterOsApiConnectionError(
                        f"Failed to connect to Mikrotik at {self.host}:{self.port} after {max_retries} attempts - {error_type}. {suggestion}"
                    )
                    
            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error on connection attempt {attempt}/{max_retries}: {str(e)}")
                
                if attempt < max_retries:
                    delay = retry_delay * (2 ** (attempt - 1))
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(f"All {max_retries} connection attempts failed due to unexpected errors")
                    raise RouterOsApiConnectionError(
                        f"Failed to connect to Mikrotik at {self.host}:{self.port}: {str(e)}"
                    )
        
        # Should not reach here, but just in case
        if last_error:
            raise last_error
        return False

    def disconnect(self) -> None:
        """Close connection to Mikrotik router."""
        try:
            if self._connection is not None:
                self._connection.disconnect()
                self._connection = None
                self._api = None
                logger.info(f"Disconnected from Mikrotik at {self.host}")
        except Exception as e:
            logger.error(f"Error disconnecting from Mikrotik: {str(e)}")
    
    def get_active_pppoe_users(self) -> list[dict]:
        """
        Retrieve list of active PPPoE users from Mikrotik.
        
        Returns:
            list[dict]: List of active PPPoE users with connection details.
                Each dict contains: name, address, service, uptime, caller_id
        
        Raises:
            RouterOsApiConnectionError: If not connected or connection fails
            RouterOsApiCommunicationError: If API communication fails
        """
        try:
            if self._api is None:
                self.connect()
            
            # Query active PPPoE sessions
            resource = self._api.get_resource('/ppp/active')
            active_users = resource.get()
            
            # Format the response
            users = []
            for user in active_users:
                users.append({
                    'name': user.get('name', ''),
                    'address': user.get('address', ''),
                    'service': user.get('service', ''),
                    'uptime': user.get('uptime', ''),
                    'caller_id': user.get('caller-id', '')
                })
            
            logger.info(f"Retrieved {len(users)} active PPPoE users from Mikrotik")
            return users
            
        except RouterOsApiConnectionError as e:
            logger.error(f"Connection error while fetching active users: {str(e)}")
            raise
        except RouterOsApiCommunicationError as e:
            logger.error(f"Communication error while fetching active users: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching active users: {str(e)}")
            raise RouterOsApiCommunicationError(f"Failed to fetch active users: {str(e)}")

    def get_user_by_name(self, username: str) -> Optional[dict]:
        """
        Get specific PPPoE user by username.
        
        Args:
            username: PPPoE username to search for
        
        Returns:
            dict: User connection details if found, None otherwise.
                Contains: name, address, service, uptime, caller_id
        
        Raises:
            RouterOsApiConnectionError: If not connected or connection fails
            RouterOsApiCommunicationError: If API communication fails
        """
        try:
            if self._api is None:
                self.connect()
            
            # Query active PPPoE sessions
            resource = self._api.get_resource('/ppp/active')
            active_users = resource.get()
            
            # Search for specific user
            for user in active_users:
                if user.get('name', '') == username:
                    return {
                        'name': user.get('name', ''),
                        'address': user.get('address', ''),
                        'service': user.get('service', ''),
                        'uptime': user.get('uptime', ''),
                        'caller_id': user.get('caller-id', '')
                    }
            
            logger.info(f"User '{username}' not found in active PPPoE sessions")
            return None
            
        except RouterOsApiConnectionError as e:
            logger.error(f"Connection error while fetching user '{username}': {str(e)}")
            raise
        except RouterOsApiCommunicationError as e:
            logger.error(f"Communication error while fetching user '{username}': {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching user '{username}': {str(e)}")
            raise RouterOsApiCommunicationError(f"Failed to fetch user: {str(e)}")
    
    def is_user_online(self, username: str) -> bool:
        """
        Check if a specific PPPoE user is currently online.
        
        Args:
            username: PPPoE username to check
        
        Returns:
            bool: True if user is online, False otherwise
        
        Raises:
            RouterOsApiConnectionError: If not connected or connection fails
            RouterOsApiCommunicationError: If API communication fails
        """
        try:
            user = self.get_user_by_name(username)
            is_online = user is not None
            logger.info(f"User '{username}' online status: {is_online}")
            return is_online
            
        except (RouterOsApiConnectionError, RouterOsApiCommunicationError) as e:
            logger.error(f"Error checking online status for '{username}': {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error checking online status: {str(e)}")
            raise RouterOsApiCommunicationError(f"Failed to check online status: {str(e)}")
    def create_pppoe_user(self, username: str, password: str, profile: str = 'default') -> bool:
        """
        Create a new PPPoE user in Mikrotik.

        Args:
            username: PPPoE username
            password: PPPoE password
            profile: PPPoE profile name (default: 'default')

        Returns:
            bool: True if user created successfully, False otherwise

        Raises:
            RouterOsApiConnectionError: If not connected or connection fails
            RouterOsApiCommunicationError: If API communication fails
        """
        try:
            if self._api is None:
                self.connect()

            # Get PPP secrets resource
            resource = self._api.get_resource('/ppp/secret')

            # Create new PPPoE user
            resource.add(
                name=username,
                password=password,
                service='pppoe',
                profile=profile
            )

            logger.info(f"Successfully created PPPoE user '{username}' in Mikrotik")
            return True

        except RouterOsApiConnectionError as e:
            logger.error(f"Connection error while creating user '{username}': {str(e)}")
            raise
        except RouterOsApiCommunicationError as e:
            logger.error(f"Communication error while creating user '{username}': {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating user '{username}': {str(e)}")
            raise RouterOsApiCommunicationError(f"Failed to create user: {str(e)}")

    def update_pppoe_user_profile(self, username: str, profile: str) -> bool:
        """
        Update the profile of an existing PPPoE user in Mikrotik.

        Args:
            username: PPPoE username
            profile: New PPPoE profile name

        Returns:
            bool: True if profile updated successfully, False otherwise

        Raises:
            RouterOsApiConnectionError: If not connected or connection fails
            RouterOsApiCommunicationError: If API communication fails
        """
        try:
            if self._api is None:
                self.connect()

            # Get PPP secrets resource
            resource = self._api.get_resource('/ppp/secret')

            # Find the user
            users = resource.get(name=username)

            if not users:
                logger.error(f"User '{username}' not found in Mikrotik")
                raise ValueError(f"User '{username}' not found")

            # Update the profile
            user_id = users[0]['id']
            resource.set(id=user_id, profile=profile)

            logger.info(f"Successfully updated profile for PPPoE user '{username}' to '{profile}'")
            return True

        except RouterOsApiConnectionError as e:
            logger.error(f"Connection error while updating profile for user '{username}': {str(e)}")
            raise
        except RouterOsApiCommunicationError as e:
            logger.error(f"Communication error while updating profile for user '{username}': {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating profile for user '{username}': {str(e)}")
            raise RouterOsApiCommunicationError(f"Failed to update profile: {str(e)}")


    def delete_pppoe_user(self, username: str) -> bool:
        """
        Delete a PPPoE user from Mikrotik.

        Args:
            username: PPPoE username to delete

        Returns:
            bool: True if user deleted successfully, False if user not found

        Raises:
            RouterOsApiConnectionError: If not connected or connection fails
            RouterOsApiCommunicationError: If API communication fails
        """
        try:
            if self._api is None:
                self.connect()

            # Get PPP secrets resource
            resource = self._api.get_resource('/ppp/secret')

            # Find the user
            users = resource.get(name=username)

            if not users:
                logger.warning(f"PPPoE user '{username}' not found in Mikrotik")
                return False

            # Delete the user (use the .id field)
            for user in users:
                resource.remove(id=user['id'])
                logger.info(f"Successfully deleted PPPoE user '{username}' from Mikrotik")

            return True

        except RouterOsApiConnectionError as e:
            logger.error(f"Connection error while deleting user '{username}': {str(e)}")
            raise
        except RouterOsApiCommunicationError as e:
            logger.error(f"Communication error while deleting user '{username}': {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting user '{username}': {str(e)}")
            raise RouterOsApiCommunicationError(f"Failed to delete user: {str(e)}")

    def get_all_pppoe_secrets(self) -> list[dict]:
        """
        Retrieve all PPPoE secrets (user accounts) from Mikrotik.

        Returns:
            list[dict]: List of PPPoE secrets with user details.
                Each dict contains: name, password, service, profile

        Raises:
            RouterOsApiConnectionError: If not connected or connection fails
            RouterOsApiCommunicationError: If API communication fails
        """
        try:
            if self._api is None:
                self.connect()

            # Query PPP secrets
            resource = self._api.get_resource('/ppp/secret')
            secrets = resource.get()

            # Format the response
            users = []
            for secret in secrets:
                users.append({
                    'name': secret.get('name', ''),
                    'service': secret.get('service', ''),
                    'profile': secret.get('profile', '')
                })

            logger.info(f"Retrieved {len(users)} PPPoE secrets from Mikrotik")
            return users

        except RouterOsApiConnectionError as e:
            logger.error(f"Connection error while fetching PPPoE secrets: {str(e)}")
            raise
        except RouterOsApiCommunicationError as e:
            logger.error(f"Communication error while fetching PPPoE secrets: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching PPPoE secrets: {str(e)}")
            raise RouterOsApiCommunicationError(f"Failed to fetch PPPoE secrets: {str(e)}")

    def get_ppp_profiles(self) -> list[dict]:
        """
        Retrieve all PPP profiles from Mikrotik.

        Returns:
            list[dict]: List of profile dictionaries with name and rate-limit information.
                Each dict contains: name, rate_limit (raw string from Mikrotik)

        Raises:
            RouterOsApiConnectionError: If not connected or connection fails
            RouterOsApiCommunicationError: If API communication fails
        """
        try:
            if self._api is None:
                self.connect()

            # Query PPP profiles
            resource = self._api.get_resource('/ppp/profile')
            profiles = resource.get()

            # Format the response
            profile_list = []
            for profile in profiles:
                profile_list.append({
                    'name': profile.get('name', ''),
                    'rate_limit': profile.get('rate-limit', '')
                })

            logger.info(f"Retrieved {len(profile_list)} PPP profiles from Mikrotik")
            return profile_list

        except RouterOsApiConnectionError as e:
            logger.error(f"Connection error while fetching PPP profiles: {str(e)}")
            raise
        except RouterOsApiCommunicationError as e:
            logger.error(f"Communication error while fetching PPP profiles: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching PPP profiles: {str(e)}")
            raise RouterOsApiCommunicationError(f"Failed to fetch PPP profiles: {str(e)}")

    def find_matching_profile(self, download_mbps: int, upload_mbps: int, profiles: list[dict]) -> Optional[str]:
        """
        Find a profile that matches the requested speeds using flexible matching.

        Supports multiple naming conventions:
        - "XMBPS", "XMbps", "XM", "Xmbps", "X_MBPS" (case-insensitive)
        - Parses rate-limit strings to extract actual speeds
        - Matches based on download speed primarily
        - Considers upload speed if specified in the profile

        Args:
            download_mbps: Requested download speed in Mbps
            upload_mbps: Requested upload speed in Mbps
            profiles: List of available profile dictionaries from get_ppp_profiles()

        Returns:
            str: Matching profile name, or None if no match found
        """
        import re

        logger.info(f"Searching for profile matching {download_mbps}M download / {upload_mbps}M upload")
        logger.debug(f"Available profiles: {[p['name'] for p in profiles]}")

        # First, try to find profiles by parsing rate-limit strings
        for profile in profiles:
            profile_name = profile.get('name', '')
            rate_limit = profile.get('rate_limit', '')

            if not rate_limit:
                # Try to extract speed from profile name if no rate-limit is set
                # Support patterns like: "5MBPS", "5Mbps", "5M", "5mbps", "5_MBPS"
                name_pattern = r'(\d+)\s*[_-]?\s*m(?:bps)?'
                match = re.search(name_pattern, profile_name, re.IGNORECASE)

                if match:
                    profile_speed = int(match.group(1))
                    if profile_speed == download_mbps:
                        logger.info(f"Found matching profile by name: {profile_name} (speed: {profile_speed}M)")
                        return profile_name
                continue

            # Parse rate-limit string format: "download/upload" or "download"
            # Examples: "5M/5M", "10M/2M", "5000000/5000000"
            try:
                # Split by forward slash to get download/upload
                parts = rate_limit.split('/')
                if len(parts) >= 1:
                    download_str = parts[0].strip()
                    upload_str = parts[1].strip() if len(parts) > 1 else None

                    # Parse download speed
                    profile_download_mbps = self._parse_speed_to_mbps(download_str)

                    # Check if download speed matches
                    if profile_download_mbps == download_mbps:
                        # If upload speed is specified in both request and profile, check it too
                        if upload_str and upload_mbps:
                            profile_upload_mbps = self._parse_speed_to_mbps(upload_str)
                            if profile_upload_mbps == upload_mbps:
                                logger.info(f"Found matching profile: {profile_name} ({download_mbps}M/{upload_mbps}M)")
                                return profile_name
                        else:
                            # Upload not specified or not required to match
                            logger.info(f"Found matching profile: {profile_name} (download: {download_mbps}M)")
                            return profile_name
            except (ValueError, IndexError) as e:
                logger.debug(f"Could not parse rate-limit for profile {profile_name}: {rate_limit} - {e}")
                continue

        # If no match found by rate-limit, try fuzzy matching on profile names
        # Support common naming patterns: "5MBPS", "5Mbps", "5M", etc.
        for profile in profiles:
            profile_name = profile.get('name', '')

            # Try various naming patterns (case-insensitive)
            patterns = [
                f"{download_mbps}MBPS",
                f"{download_mbps}Mbps",
                f"{download_mbps}M",
                f"{download_mbps}mbps",
                f"{download_mbps}_MBPS",
                f"{download_mbps}-MBPS",
                f"{download_mbps} MBPS",
            ]

            for pattern in patterns:
                if profile_name.lower() == pattern.lower():
                    logger.info(f"Found matching profile by name pattern: {profile_name}")
                    return profile_name

        logger.warning(f"No matching profile found for {download_mbps}M/{upload_mbps}M")
        logger.info(f"Available profiles: {', '.join([p['name'] for p in profiles])}")
        return None

    def _parse_speed_to_mbps(self, speed_str: str) -> int:
        """
        Parse a speed string to Mbps.

        Supports formats:
        - "5M" -> 5
        - "5000k" -> 5
        - "5000000" (bps) -> 5

        Args:
            speed_str: Speed string from Mikrotik

        Returns:
            int: Speed in Mbps

        Raises:
            ValueError: If speed string cannot be parsed
        """
        import re

        speed_str = speed_str.strip().upper()

        # Match number with optional unit
        match = re.match(r'(\d+(?:\.\d+)?)\s*([MKmk])?', speed_str)
        if not match:
            raise ValueError(f"Cannot parse speed string: {speed_str}")

        value = float(match.group(1))
        unit = match.group(2)

        if unit == 'M':
            return int(value)
        elif unit == 'K':
            return int(value / 1000)
        else:
            # Assume bps (bits per second)
            return int(value / 1000000)


    
    def __enter__(self):
        """Context manager entry - establish connection."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connection."""
        self.disconnect()
        return False

    def get_session_bandwidth(self, username: str) -> Optional[dict]:
        """
        Get bandwidth data for specific PPPoE session.
        
        Args:
            username: PPPoE username
            
        Returns:
            dict: {
                'username': str,
                'rx_bytes_per_sec': int,
                'tx_bytes_per_sec': int,
                'rx_mbps': float,
                'tx_mbps': float
            } or None if user not online
        
        Raises:
            RouterOsApiConnectionError: If connection fails
            RouterOsApiCommunicationError: If API call fails
        """
        try:
            if self._api is None:
                self.connect()
            
            # Import conversion utility
            from services.bandwidth_service import BandwidthService
            
            # Query active PPPoE sessions with interface stats
            resource = self._api.get_resource('/ppp/active')
            active_users = resource.get()
            
            # Find the specific user
            for user in active_users:
                if user.get('name', '') == username:
                    # Get RX/TX rates (bytes per second)
                    rx_bytes = int(user.get('rx-rate', 0))
                    tx_bytes = int(user.get('tx-rate', 0))
                    
                    # Convert to Mbps
                    rx_mbps = BandwidthService.convert_bytes_to_mbps(rx_bytes)
                    tx_mbps = BandwidthService.convert_bytes_to_mbps(tx_bytes)
                    
                    return {
                        'username': username,
                        'rx_bytes_per_sec': rx_bytes,
                        'tx_bytes_per_sec': tx_bytes,
                        'rx_mbps': rx_mbps,
                        'tx_mbps': tx_mbps
                    }
            
            logger.info(f"User '{username}' not found in active sessions")
            return None
            
        except RouterOsApiConnectionError as e:
            logger.error(f"Connection error while fetching bandwidth for '{username}': {str(e)}")
            raise
        except RouterOsApiCommunicationError as e:
            logger.error(f"Communication error while fetching bandwidth for '{username}': {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching bandwidth for '{username}': {str(e)}")
            raise RouterOsApiCommunicationError(f"Failed to fetch bandwidth: {str(e)}")
    
    def get_all_sessions_bandwidth(self) -> list[dict]:
        """
        Get bandwidth data for all active PPPoE sessions.
        Uses batch query for efficiency.
        
        Returns:
            list[dict]: Bandwidth data for all sessions
        """
        try:
            if self._api is None:
                self.connect()
            
            # Import conversion utility
            from services.bandwidth_service import BandwidthService
            
            # Query all active PPPoE sessions
            resource = self._api.get_resource('/ppp/active')
            active_users = resource.get()
            
            # Process all sessions
            bandwidth_data = []
            for user in active_users:
                username = user.get('name', '')
                rx_bytes = int(user.get('rx-rate', 0))
                tx_bytes = int(user.get('tx-rate', 0))
                
                # Convert to Mbps
                rx_mbps = BandwidthService.convert_bytes_to_mbps(rx_bytes)
                tx_mbps = BandwidthService.convert_bytes_to_mbps(tx_bytes)
                
                bandwidth_data.append({
                    'username': username,
                    'rx_bytes_per_sec': rx_bytes,
                    'tx_bytes_per_sec': tx_bytes,
                    'rx_mbps': rx_mbps,
                    'tx_mbps': tx_mbps
                })
            
            logger.info(f"Retrieved bandwidth data for {len(bandwidth_data)} active sessions")
            return bandwidth_data
            
        except RouterOsApiConnectionError as e:
            logger.error(f"Connection error while fetching all bandwidth data: {str(e)}")
            raise
        except RouterOsApiCommunicationError as e:
            logger.error(f"Communication error while fetching all bandwidth data: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching all bandwidth data: {str(e)}")
            raise RouterOsApiCommunicationError(f"Failed to fetch bandwidth data: {str(e)}")
    
    def disconnect_pppoe_session(self, username: str) -> bool:
        """
        Terminate active PPPoE session for user.
        
        Args:
            username: PPPoE username to disconnect
            
        Returns:
            bool: True if disconnected successfully
            
        Raises:
            RouterOsApiConnectionError: If connection fails
            RouterOsApiCommunicationError: If API call fails
            ValueError: If user not found or not online
        """
        try:
            if self._api is None:
                self.connect()
            
            # Get active sessions resource
            resource = self._api.get_resource('/ppp/active')
            active_users = resource.get()
            
            # Find the user's active session
            session_id = None
            for user in active_users:
                if user.get('name', '') == username:
                    session_id = user.get('.id')
                    break
            
            if session_id is None:
                raise ValueError(f"User '{username}' is not online or session not found")
            
            # Terminate the session
            resource.remove(id=session_id)
            
            logger.info(f"Successfully disconnected PPPoE session for user '{username}'")
            return True
            
        except ValueError as e:
            logger.warning(str(e))
            raise
        except RouterOsApiConnectionError as e:
            logger.error(f"Connection error while disconnecting '{username}': {str(e)}")
            raise
        except RouterOsApiCommunicationError as e:
            logger.error(f"Communication error while disconnecting '{username}': {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error disconnecting '{username}': {str(e)}")
            raise RouterOsApiCommunicationError(f"Failed to disconnect session: {str(e)}")

    def set_bandwidth_limit(self, username: str, download_bps: int, upload_bps: int) -> bool:
        """
        Set bandwidth limit for a PPPoE user by changing their profile.

        Uses profile discovery to find matching profiles from Mikrotik and applies
        flexible matching to handle different naming conventions.

        Args:
            username: PPPoE username
            download_bps: Download limit in bits per second
            upload_bps: Upload limit in bits per second

        Returns:
            bool: True if limit set successfully

        Raises:
            ValueError: If user not found or no matching profile available
            Exception: If API call fails
        """
        try:
            if self._api is None:
                self.connect()

            # Convert to Mbps
            download_mbps = int(download_bps / 1000000)
            upload_mbps = int(upload_bps / 1000000)

            logger.info(f"Setting bandwidth limit for '{username}': {download_mbps}M/{upload_mbps}M")

            # Get PPP secrets resource
            secrets_resource = self._api.get_resource('/ppp/secret')

            # Find the user by name first (preserve existing error handling)
            users = secrets_resource.get(name=username)

            if not users:
                raise ValueError(f"PPPoE user '{username}' not found")

            user = users[0]
            user_id = user.get('.id')

            # Discover available profiles from Mikrotik
            logger.info(f"Discovering available PPP profiles for user '{username}'")
            profiles = self.get_ppp_profiles()

            if not profiles:
                raise ValueError("No PPP profiles found in Mikrotik. Please create profiles first.")

            # Find matching profile using flexible matching
            logger.info(f"Searching for profile matching {download_mbps}M/{upload_mbps}M speeds")
            profile_name = self.find_matching_profile(download_mbps, upload_mbps, profiles)

            if profile_name is None:
                # No matching profile found - provide helpful error with available options
                available_profiles = []
                for profile in profiles:
                    rate_limit = profile.get('rate_limit', 'not set')
                    available_profiles.append(f"  - {profile['name']} (rate-limit: {rate_limit})")

                available_list = '\n'.join(available_profiles)
                error_msg = (
                    f"No matching profile found for {download_mbps}M/{upload_mbps}M speeds. "
                    f"Available profiles:\n{available_list}\n"
                    f"Please create a profile with matching speeds or adjust the requested bandwidth."
                )
                logger.warning(error_msg)
                raise ValueError(error_msg)

            # Update the user's profile with the matched profile
            logger.info(f"Assigning profile '{profile_name}' to user '{username}'")
            secrets_resource.set(**{'.id': user_id, 'profile': profile_name})

            logger.info(f"Successfully changed profile for '{username}' to '{profile_name}' ({download_mbps}/{upload_mbps} Mbps)")
            return True

        except ValueError as e:
            # Preserve existing ValueError handling (for non-existent users and profile mismatches)
            logger.warning(str(e))
            raise
        except Exception as e:
            logger.error(f"Error setting bandwidth limit for '{username}': {str(e)}")
            raise


