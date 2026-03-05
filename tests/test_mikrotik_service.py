"""Unit tests for MikrotikService"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from services.mikrotik_service import MikrotikService
from routeros_api.exceptions import RouterOsApiConnectionError, RouterOsApiCommunicationError


class TestMikrotikService:
    """Test cases for MikrotikService"""
    
    def test_init(self):
        """Test MikrotikService initialization"""
        service = MikrotikService(
            host='10.114.215.133',
            username='admin',
            password='adminTaboo'
        )
        
        assert service.host == '10.114.215.133'
        assert service.username == 'admin'
        assert service.password == 'adminTaboo'
        assert service.port == 8728
        assert service._connection is None
        assert service._api is None
    
    @patch('services.mikrotik_service.RouterOsApiPool')
    def test_connect_success(self, mock_pool):
        """Test successful connection to Mikrotik"""
        mock_connection = Mock()
        mock_api = Mock()
        mock_connection.get_api.return_value = mock_api
        mock_pool.return_value = mock_connection
        
        service = MikrotikService('10.114.215.133', 'admin', 'adminTaboo')
        result = service.connect()
        
        assert result is True
        assert service._connection is not None
        assert service._api is not None
        mock_pool.assert_called_once_with(
            '10.114.215.133',
            username='admin',
            password='adminTaboo',
            port=8728,
            plaintext_login=True
        )
    
    @patch('services.mikrotik_service.RouterOsApiPool')
    def test_connect_failure(self, mock_pool):
        """Test connection failure to Mikrotik"""
        mock_pool.side_effect = RouterOsApiConnectionError('Connection failed')
        
        service = MikrotikService('10.114.215.133', 'admin', 'wrong_password')
        
        with pytest.raises(RouterOsApiConnectionError):
            service.connect()

    @patch('services.mikrotik_service.RouterOsApiPool')
    def test_disconnect(self, mock_pool):
        """Test disconnection from Mikrotik"""
        mock_connection = Mock()
        mock_api = Mock()
        mock_connection.get_api.return_value = mock_api
        mock_pool.return_value = mock_connection
        
        service = MikrotikService('10.114.215.133', 'admin', 'adminTaboo')
        service.connect()
        service.disconnect()
        
        mock_connection.disconnect.assert_called_once()
        assert service._connection is None
        assert service._api is None
    
    @patch('services.mikrotik_service.RouterOsApiPool')
    def test_get_active_pppoe_users_success(self, mock_pool):
        """Test retrieving active PPPoE users"""
        # Setup mock
        mock_connection = Mock()
        mock_api = Mock()
        mock_resource = Mock()
        
        mock_users = [
            {
                'name': 'user1',
                'address': '192.168.1.10',
                'service': 'pppoe-service1',
                'uptime': '1h30m',
                'caller-id': '00:11:22:33:44:55'
            },
            {
                'name': 'user2',
                'address': '192.168.1.11',
                'service': 'pppoe-service1',
                'uptime': '2h15m',
                'caller-id': '00:11:22:33:44:66'
            }
        ]
        
        mock_resource.get.return_value = mock_users
        mock_api.get_resource.return_value = mock_resource
        mock_connection.get_api.return_value = mock_api
        mock_pool.return_value = mock_connection
        
        service = MikrotikService('10.114.215.133', 'admin', 'adminTaboo')
        users = service.get_active_pppoe_users()
        
        assert len(users) == 2
        assert users[0]['name'] == 'user1'
        assert users[0]['address'] == '192.168.1.10'
        assert users[0]['uptime'] == '1h30m'
        assert users[1]['name'] == 'user2'
        mock_api.get_resource.assert_called_with('/ppp/active')

    @patch('services.mikrotik_service.RouterOsApiPool')
    def test_get_active_pppoe_users_empty(self, mock_pool):
        """Test retrieving active PPPoE users when none are online"""
        mock_connection = Mock()
        mock_api = Mock()
        mock_resource = Mock()
        
        mock_resource.get.return_value = []
        mock_api.get_resource.return_value = mock_resource
        mock_connection.get_api.return_value = mock_api
        mock_pool.return_value = mock_connection
        
        service = MikrotikService('10.114.215.133', 'admin', 'adminTaboo')
        users = service.get_active_pppoe_users()
        
        assert len(users) == 0
        assert users == []
    
    @patch('services.mikrotik_service.RouterOsApiPool')
    def test_get_user_by_name_found(self, mock_pool):
        """Test getting specific user by name when user is online"""
        mock_connection = Mock()
        mock_api = Mock()
        mock_resource = Mock()
        
        mock_users = [
            {
                'name': 'user1',
                'address': '192.168.1.10',
                'service': 'pppoe-service1',
                'uptime': '1h30m',
                'caller-id': '00:11:22:33:44:55'
            },
            {
                'name': 'user2',
                'address': '192.168.1.11',
                'service': 'pppoe-service1',
                'uptime': '2h15m',
                'caller-id': '00:11:22:33:44:66'
            }
        ]
        
        mock_resource.get.return_value = mock_users
        mock_api.get_resource.return_value = mock_resource
        mock_connection.get_api.return_value = mock_api
        mock_pool.return_value = mock_connection
        
        service = MikrotikService('10.114.215.133', 'admin', 'adminTaboo')
        user = service.get_user_by_name('user1')
        
        assert user is not None
        assert user['name'] == 'user1'
        assert user['address'] == '192.168.1.10'
        assert user['uptime'] == '1h30m'
    
    @patch('services.mikrotik_service.RouterOsApiPool')
    def test_get_user_by_name_not_found(self, mock_pool):
        """Test getting specific user by name when user is offline"""
        mock_connection = Mock()
        mock_api = Mock()
        mock_resource = Mock()
        
        mock_resource.get.return_value = []
        mock_api.get_resource.return_value = mock_resource
        mock_connection.get_api.return_value = mock_api
        mock_pool.return_value = mock_connection
        
        service = MikrotikService('10.114.215.133', 'admin', 'adminTaboo')
        user = service.get_user_by_name('nonexistent_user')
        
        assert user is None

    @patch('services.mikrotik_service.RouterOsApiPool')
    def test_is_user_online_true(self, mock_pool):
        """Test checking if user is online when user is connected"""
        mock_connection = Mock()
        mock_api = Mock()
        mock_resource = Mock()
        
        mock_users = [
            {
                'name': 'user1',
                'address': '192.168.1.10',
                'service': 'pppoe-service1',
                'uptime': '1h30m',
                'caller-id': '00:11:22:33:44:55'
            }
        ]
        
        mock_resource.get.return_value = mock_users
        mock_api.get_resource.return_value = mock_resource
        mock_connection.get_api.return_value = mock_api
        mock_pool.return_value = mock_connection
        
        service = MikrotikService('10.114.215.133', 'admin', 'adminTaboo')
        is_online = service.is_user_online('user1')
        
        assert is_online is True
    
    @patch('services.mikrotik_service.RouterOsApiPool')
    def test_is_user_online_false(self, mock_pool):
        """Test checking if user is online when user is disconnected"""
        mock_connection = Mock()
        mock_api = Mock()
        mock_resource = Mock()
        
        mock_resource.get.return_value = []
        mock_api.get_resource.return_value = mock_resource
        mock_connection.get_api.return_value = mock_api
        mock_pool.return_value = mock_connection
        
        service = MikrotikService('10.114.215.133', 'admin', 'adminTaboo')
        is_online = service.is_user_online('offline_user')
        
        assert is_online is False
    
    @patch('services.mikrotik_service.RouterOsApiPool')
    def test_context_manager(self, mock_pool):
        """Test using MikrotikService as context manager"""
        mock_connection = Mock()
        mock_api = Mock()
        mock_connection.get_api.return_value = mock_api
        mock_pool.return_value = mock_connection
        
        with MikrotikService('10.114.215.133', 'admin', 'adminTaboo') as service:
            assert service._connection is not None
            assert service._api is not None
        
        mock_connection.disconnect.assert_called_once()
    
    @patch('services.mikrotik_service.RouterOsApiPool')
    def test_connection_error_handling(self, mock_pool):
        """Test error handling for connection failures"""
        mock_connection = Mock()
        mock_api = Mock()
        mock_resource = Mock()
        
        mock_resource.get.side_effect = RouterOsApiCommunicationError('Communication failed', 'Original error')
        mock_api.get_resource.return_value = mock_resource
        mock_connection.get_api.return_value = mock_api
        mock_pool.return_value = mock_connection
        
        service = MikrotikService('10.114.215.133', 'admin', 'adminTaboo')
        
        with pytest.raises(RouterOsApiCommunicationError):
            service.get_active_pppoe_users()

    @patch('services.mikrotik_service.RouterOsApiPool')
    @patch('services.mikrotik_service.time.sleep')
    def test_connect_with_retry_success_on_second_attempt(self, mock_sleep, mock_pool):
        """Test connection succeeds on second retry attempt"""
        mock_connection = Mock()
        mock_api = Mock()
        mock_identity_resource = Mock()
        mock_identity_resource.get.return_value = [{'name': 'TestRouter'}]
        mock_api.get_resource.return_value = mock_identity_resource
        mock_connection.get_api.return_value = mock_api
        
        # First call fails, second succeeds
        mock_pool.side_effect = [
            RouterOsApiConnectionError('Connection timeout'),
            mock_connection
        ]
        
        service = MikrotikService('10.114.215.133', 'admin', 'adminTaboo')
        result = service.connect(max_retries=3, retry_delay=2)
        
        assert result is True
        assert service._connection is not None
        assert service._api is not None
        # Should have slept once (after first failure)
        mock_sleep.assert_called_once_with(2)
        # Should have tried twice
        assert mock_pool.call_count == 2
    
    @patch('services.mikrotik_service.RouterOsApiPool')
    @patch('services.mikrotik_service.time.sleep')
    def test_connect_with_retry_exponential_backoff(self, mock_sleep, mock_pool):
        """Test exponential backoff delays between retries"""
        mock_connection = Mock()
        mock_api = Mock()
        mock_identity_resource = Mock()
        mock_identity_resource.get.return_value = [{'name': 'TestRouter'}]
        mock_api.get_resource.return_value = mock_identity_resource
        mock_connection.get_api.return_value = mock_api
        
        # First two calls fail, third succeeds
        mock_pool.side_effect = [
            RouterOsApiConnectionError('Connection timeout'),
            RouterOsApiConnectionError('Connection timeout'),
            mock_connection
        ]
        
        service = MikrotikService('10.114.215.133', 'admin', 'adminTaboo')
        result = service.connect(max_retries=3, retry_delay=2)
        
        assert result is True
        # Should have slept twice with exponential backoff: 2s, 4s
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(2)  # First retry delay
        mock_sleep.assert_any_call(4)  # Second retry delay (2 * 2^1)
    
    @patch('services.mikrotik_service.RouterOsApiPool')
    @patch('services.mikrotik_service.time.sleep')
    def test_connect_with_retry_all_attempts_fail(self, mock_sleep, mock_pool):
        """Test connection fails after all retry attempts exhausted"""
        mock_pool.side_effect = RouterOsApiConnectionError('Connection timeout')
        
        service = MikrotikService('10.114.215.133', 'admin', 'adminTaboo')
        
        with pytest.raises(RouterOsApiConnectionError) as exc_info:
            service.connect(max_retries=3, retry_delay=2)
        
        # Should have tried 3 times
        assert mock_pool.call_count == 3
        # Should have slept twice (after first and second failures)
        assert mock_sleep.call_count == 2
        # Error message should mention number of attempts
        assert 'after 3 attempts' in str(exc_info.value)
    
    @patch('services.mikrotik_service.RouterOsApiPool')
    @patch('services.mikrotik_service.time.sleep')
    def test_connect_with_retry_authentication_error_no_retry(self, mock_sleep, mock_pool):
        """Test authentication errors don't trigger retries"""
        mock_pool.side_effect = RouterOsApiConnectionError('Authentication failed')
        
        service = MikrotikService('10.114.215.133', 'admin', 'wrong_password')
        
        with pytest.raises(RouterOsApiConnectionError) as exc_info:
            service.connect(max_retries=3, retry_delay=2)
        
        # Should have tried only once (no retries for auth errors)
        assert mock_pool.call_count == 1
        # Should not have slept
        mock_sleep.assert_not_called()
        # Error message should mention authentication
        assert 'Authentication failed' in str(exc_info.value)
    
    @patch('services.mikrotik_service.RouterOsApiPool')
    def test_connect_with_validation_success(self, mock_pool):
        """Test connection validation with system identity check"""
        mock_connection = Mock()
        mock_api = Mock()
        mock_identity_resource = Mock()
        mock_identity_resource.get.return_value = [{'name': 'MyRouter'}]
        mock_api.get_resource.return_value = mock_identity_resource
        mock_connection.get_api.return_value = mock_api
        mock_pool.return_value = mock_connection
        
        service = MikrotikService('10.114.215.133', 'admin', 'adminTaboo')
        result = service.connect()
        
        assert result is True
        # Should have called get_resource to validate connection
        mock_api.get_resource.assert_called_with('/system/identity')
        mock_identity_resource.get.assert_called_once()
    
    @patch('services.mikrotik_service.RouterOsApiPool')
    def test_connect_with_validation_failure_still_connects(self, mock_pool):
        """Test connection succeeds even if validation fails"""
        mock_connection = Mock()
        mock_api = Mock()
        mock_identity_resource = Mock()
        mock_identity_resource.get.side_effect = Exception('Validation error')
        mock_api.get_resource.return_value = mock_identity_resource
        mock_connection.get_api.return_value = mock_api
        mock_pool.return_value = mock_connection
        
        service = MikrotikService('10.114.215.133', 'admin', 'adminTaboo')
        result = service.connect()
        
        # Should still return True even if validation fails
        assert result is True
        assert service._connection is not None
        assert service._api is not None

    @patch('services.mikrotik_service.RouterOsApiPool')
    def test_get_ppp_profiles_success(self, mock_pool):
        """Test retrieving PPP profiles from Mikrotik"""
        mock_connection = Mock()
        mock_api = Mock()
        mock_resource = Mock()
        
        mock_profiles = [
            {
                'name': '5Mbps',
                'rate-limit': '5M/5M'
            },
            {
                'name': '10Mbps',
                'rate-limit': '10M/10M'
            },
            {
                'name': 'default',
                'rate-limit': ''
            }
        ]
        
        mock_resource.get.return_value = mock_profiles
        mock_api.get_resource.return_value = mock_resource
        mock_connection.get_api.return_value = mock_api
        mock_pool.return_value = mock_connection
        
        service = MikrotikService('10.114.215.133', 'admin', 'adminTaboo')
        profiles = service.get_ppp_profiles()
        
        assert len(profiles) == 3
        assert profiles[0]['name'] == '5Mbps'
        assert profiles[0]['rate_limit'] == '5M/5M'
        assert profiles[1]['name'] == '10Mbps'
        assert profiles[1]['rate_limit'] == '10M/10M'
        assert profiles[2]['name'] == 'default'
        assert profiles[2]['rate_limit'] == ''
        mock_api.get_resource.assert_called_with('/ppp/profile')
    
    @patch('services.mikrotik_service.RouterOsApiPool')
    def test_get_ppp_profiles_empty(self, mock_pool):
        """Test retrieving PPP profiles when none exist"""
        mock_connection = Mock()
        mock_api = Mock()
        mock_resource = Mock()
        
        mock_resource.get.return_value = []
        mock_api.get_resource.return_value = mock_resource
        mock_connection.get_api.return_value = mock_api
        mock_pool.return_value = mock_connection
        
        service = MikrotikService('10.114.215.133', 'admin', 'adminTaboo')
        profiles = service.get_ppp_profiles()
        
        assert len(profiles) == 0
        assert profiles == []
    
    @patch('services.mikrotik_service.RouterOsApiPool')
    def test_get_ppp_profiles_connection_error(self, mock_pool):
        """Test error handling when connection fails during profile retrieval"""
        mock_connection = Mock()
        mock_api = Mock()
        mock_resource = Mock()
        
        mock_resource.get.side_effect = RouterOsApiConnectionError('Connection failed')
        mock_api.get_resource.return_value = mock_resource
        mock_connection.get_api.return_value = mock_api
        mock_pool.return_value = mock_connection
        
        service = MikrotikService('10.114.215.133', 'admin', 'adminTaboo')
        
        with pytest.raises(RouterOsApiConnectionError):
            service.get_ppp_profiles()
    
    @patch('services.mikrotik_service.RouterOsApiPool')
    def test_get_ppp_profiles_communication_error(self, mock_pool):
        """Test error handling when API communication fails during profile retrieval"""
        mock_connection = Mock()
        mock_api = Mock()
        mock_resource = Mock()
        
        mock_resource.get.side_effect = RouterOsApiCommunicationError('Communication failed', 'Original error')
        mock_api.get_resource.return_value = mock_resource
        mock_connection.get_api.return_value = mock_api
        mock_pool.return_value = mock_connection
        
        service = MikrotikService('10.114.215.133', 'admin', 'adminTaboo')
        
        with pytest.raises(RouterOsApiCommunicationError):
            service.get_ppp_profiles()
