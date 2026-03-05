"""
Preservation Property Tests for Bandwidth Limit Profile Change Fix

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8**

**Property 2: Preservation** - Existing Mikrotik Operations

IMPORTANTE: Ang mga test na ito ay sumusunod sa observation-first methodology.
I-observe muna ang behavior sa UNFIXED code para sa non-buggy inputs,
pagkatapos gumawa ng property-based tests na kumukuha ng observed behavior.

LAYUNIN: Siguraduhing ang existing Mikrotik operations ay patuloy na gumagana
nang tama pagkatapos ng fix implementation.

INAASAHANG RESULTA: Ang mga test ay PUMASA sa unfixed code (baseline behavior)
at dapat PUMASA pa rin pagkatapos ng fix (walang regressions).

Test Cases:
- Test 2a: User Creation Preservation
- Test 2b: User Deletion Preservation
- Test 2c: Session Retrieval Preservation
- Test 2d: Disconnection Preservation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from services.mikrotik_service import MikrotikService
from routeros_api.exceptions import RouterOsApiConnectionError, RouterOsApiCommunicationError
from hypothesis import given, strategies as st, settings, assume


class TestPreservationProperties:
    """
    Preservation Property Tests
    
    **Property 2: Preservation** - Existing Mikrotik Operations
    
    Ang mga test na ito ay nag-verify na ang existing Mikrotik operations
    ay gumagana pa rin nang tama pagkatapos ng fix implementation.
    
    INAASAHANG RESULTA: Ang mga test ay PUMASA (baseline behavior ay preserved)
    """
    
    @given(
        username=st.text(min_size=3, max_size=50, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'), 
            whitelist_characters='_-'
        )),
        password=st.text(min_size=6, max_size=50),
        profile=st.sampled_from(['default', '5Mbps', '10Mbps', '15Mbps', '20Mbps'])
    )
    @settings(max_examples=20, deadline=None)
    def test_2a_user_creation_preservation(self, username, password, profile):
        """
        Test 2a: User Creation Preservation
        
        **Validates: Requirements 3.6**
        
        Para sa lahat ng valid user data, ang create_pppoe_user() ay dapat
        gumana tulad ng dati - successfully creating users in Mikrotik.
        
        Observation: Sa unfixed code, ang create_pppoe_user() ay:
        - Tumatanggap ng username, password, at profile
        - Gumagamit ng /ppp/secret resource
        - Tumatawag ng resource.add() na may tamang parameters
        - Nagbabalik ng True kung successful
        - Nag-log ng success message
        """
        # Filter out invalid usernames
        assume(len(username.strip()) >= 3)
        assume(not username.startswith('-'))
        assume(not username.endswith('-'))
        
        service = MikrotikService(
            host='192.168.10.5',
            username='admin',
            password='adminTaboo'
        )
        
        # Mock the API connection
        mock_api = MagicMock()
        service._api = mock_api
        
        # Mock PPP secrets resource
        mock_secrets = MagicMock()
        mock_api.get_resource.return_value = mock_secrets
        
        # Mock successful user creation
        mock_secrets.add.return_value = True
        
        # Call the method
        result = service.create_pppoe_user(username, password, profile)
        
        # Verify preservation of behavior
        assert result is True, "create_pppoe_user should return True on success"
        
        # Verify the method called the correct resource
        mock_api.get_resource.assert_called_once_with('/ppp/secret')
        
        # Verify the method called add with correct parameters
        mock_secrets.add.assert_called_once_with(
            name=username,
            password=password,
            service='pppoe',
            profile=profile
        )
    
    @given(
        username=st.text(min_size=3, max_size=50, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            whitelist_characters='_-'
        ))
    )
    @settings(max_examples=20, deadline=None)
    def test_2b_user_deletion_preservation(self, username):
        """
        Test 2b: User Deletion Preservation
        
        **Validates: Requirements 3.7**
        
        Para sa lahat ng existing users, ang delete_pppoe_user() ay dapat
        gumana tulad ng dati - successfully deleting users from Mikrotik.
        
        Observation: Sa unfixed code, ang delete_pppoe_user() ay:
        - Tumatanggap ng username
        - Gumagamit ng /ppp/secret resource
        - Tumatawag ng resource.get() para hanapin ang user
        - Tumatawag ng resource.remove() kung nahanap ang user
        - Nagbabalik ng True kung successful, False kung hindi nahanap
        - Nag-log ng appropriate message
        """
        # Filter out invalid usernames
        assume(len(username.strip()) >= 3)
        
        service = MikrotikService(
            host='192.168.10.5',
            username='admin',
            password='adminTaboo'
        )
        
        # Mock the API connection
        mock_api = MagicMock()
        service._api = mock_api
        
        # Mock PPP secrets resource
        mock_secrets = MagicMock()
        mock_api.get_resource.return_value = mock_secrets
        
        # Mock user exists
        mock_secrets.get.return_value = [
            {'id': '*1', 'name': username, 'profile': 'default'}
        ]
        
        # Mock successful deletion
        mock_secrets.remove.return_value = True
        
        # Call the method
        result = service.delete_pppoe_user(username)
        
        # Verify preservation of behavior
        assert result is True, "delete_pppoe_user should return True when user exists"
        
        # Verify the method called the correct resource
        mock_api.get_resource.assert_called_once_with('/ppp/secret')
        
        # Verify the method searched for the user
        mock_secrets.get.assert_called_once_with(name=username)
        
        # Verify the method called remove
        mock_secrets.remove.assert_called_once()
    
    @given(
        num_users=st.integers(min_value=0, max_value=10)
    )
    @settings(max_examples=15, deadline=None)
    def test_2c_session_retrieval_preservation(self, num_users):
        """
        Test 2c: Session Retrieval Preservation
        
        **Validates: Requirements 3.8**
        
        Ang get_active_pppoe_users() ay dapat magbalik ng parehong data
        tulad ng dati - accurate session information.
        
        Observation: Sa unfixed code, ang get_active_pppoe_users() ay:
        - Gumagamit ng /ppp/active resource
        - Tumatawag ng resource.get() para kunin ang active sessions
        - Nag-format ng response na may: name, address, service, uptime, caller_id
        - Nagbabalik ng list ng dicts
        - Nag-log ng bilang ng users na nakuha
        """
        service = MikrotikService(
            host='192.168.10.5',
            username='admin',
            password='adminTaboo'
        )
        
        # Mock the API connection
        mock_api = MagicMock()
        service._api = mock_api
        
        # Mock PPP active resource
        mock_active = MagicMock()
        mock_api.get_resource.return_value = mock_active
        
        # Generate mock active users
        mock_users = []
        for i in range(num_users):
            mock_users.append({
                'name': f'user{i}',
                'address': f'10.0.0.{i+1}',
                'service': 'pppoe',
                'uptime': f'{i}h',
                'caller-id': f'00:11:22:33:44:{i:02x}'
            })
        
        mock_active.get.return_value = mock_users
        
        # Call the method
        result = service.get_active_pppoe_users()
        
        # Verify preservation of behavior
        assert isinstance(result, list), "get_active_pppoe_users should return a list"
        assert len(result) == num_users, f"Should return {num_users} users"
        
        # Verify the method called the correct resource
        mock_api.get_resource.assert_called_once_with('/ppp/active')
        
        # Verify the method called get
        mock_active.get.assert_called_once()
        
        # Verify the response format
        for i, user in enumerate(result):
            assert 'name' in user, "Each user should have 'name' field"
            assert 'address' in user, "Each user should have 'address' field"
            assert 'service' in user, "Each user should have 'service' field"
            assert 'uptime' in user, "Each user should have 'uptime' field"
            assert 'caller_id' in user, "Each user should have 'caller_id' field"
            assert user['name'] == f'user{i}', f"User name should be 'user{i}'"
    
    @given(
        username=st.text(min_size=3, max_size=50, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            whitelist_characters='_-'
        ))
    )
    @settings(max_examples=20, deadline=None)
    def test_2d_disconnection_preservation(self, username):
        """
        Test 2d: Disconnection Preservation
        
        **Validates: Requirements 3.8**
        
        Para sa lahat ng active sessions, ang disconnect_pppoe_session() ay
        dapat gumana tulad ng dati - successfully terminating sessions.
        
        Observation: Sa unfixed code, ang disconnect_pppoe_session() ay:
        - Tumatanggap ng username
        - Gumagamit ng /ppp/active resource
        - Tumatawag ng resource.get() para hanapin ang active session
        - Tumatawag ng resource.remove() kung nahanap ang session
        - Nagbabalik ng True kung successful
        - Nag-raise ng ValueError kung hindi nahanap ang user o hindi online
        - Nag-log ng success message
        """
        # Filter out invalid usernames
        assume(len(username.strip()) >= 3)
        
        service = MikrotikService(
            host='192.168.10.5',
            username='admin',
            password='adminTaboo'
        )
        
        # Mock the API connection
        mock_api = MagicMock()
        service._api = mock_api
        
        # Mock PPP active resource
        mock_active = MagicMock()
        mock_api.get_resource.return_value = mock_active
        
        # Mock user is online
        mock_active.get.return_value = [
            {
                '.id': '*1',
                'name': username,
                'address': '10.0.0.1',
                'service': 'pppoe'
            }
        ]
        
        # Mock successful disconnection
        mock_active.remove.return_value = True
        
        # Call the method
        result = service.disconnect_pppoe_session(username)
        
        # Verify preservation of behavior
        assert result is True, "disconnect_pppoe_session should return True on success"
        
        # Verify the method called the correct resource
        mock_api.get_resource.assert_called_once_with('/ppp/active')
        
        # Verify the method searched for the active session
        mock_active.get.assert_called_once()
        
        # Verify the method called remove with the session ID
        mock_active.remove.assert_called_once_with(id='*1')
    
    @given(
        username=st.text(min_size=3, max_size=50, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            whitelist_characters='_-'
        ))
    )
    @settings(max_examples=15, deadline=None)
    def test_2e_disconnection_error_handling_preservation(self, username):
        """
        Test 2e: Disconnection Error Handling Preservation
        
        **Validates: Requirements 3.1**
        
        Kapag ang user ay hindi online, ang disconnect_pppoe_session() ay
        dapat mag-raise ng ValueError tulad ng dati.
        
        Observation: Sa unfixed code, kapag ang user ay hindi nahanap sa
        active sessions, ang method ay nag-raise ng ValueError na may
        message na nagsasabing ang user ay hindi online.
        """
        # Filter out invalid usernames
        assume(len(username.strip()) >= 3)
        
        service = MikrotikService(
            host='192.168.10.5',
            username='admin',
            password='adminTaboo'
        )
        
        # Mock the API connection
        mock_api = MagicMock()
        service._api = mock_api
        
        # Mock PPP active resource
        mock_active = MagicMock()
        mock_api.get_resource.return_value = mock_active
        
        # Mock user is NOT online (empty list)
        mock_active.get.return_value = []
        
        # Call the method and expect ValueError
        with pytest.raises(ValueError) as exc_info:
            service.disconnect_pppoe_session(username)
        
        # Verify the error message format is preserved
        error_message = str(exc_info.value)
        assert username in error_message, "Error message should contain username"
        assert "not online" in error_message.lower() or "not found" in error_message.lower(), \
            "Error message should indicate user is not online or not found"
    
    @given(
        username=st.text(min_size=3, max_size=50, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            whitelist_characters='_-'
        ))
    )
    @settings(max_examples=15, deadline=None)
    def test_2f_get_session_bandwidth_preservation(self, username):
        """
        Test 2f: Get Session Bandwidth Preservation
        
        **Validates: Requirements 3.8**
        
        Ang get_session_bandwidth() ay dapat magbalik ng bandwidth data
        tulad ng dati - accurate bandwidth statistics.
        
        Observation: Sa unfixed code, ang get_session_bandwidth() ay:
        - Tumatanggap ng username
        - Gumagamit ng /ppp/active resource
        - Tumatawag ng resource.get() para kunin ang active sessions
        - Kumukuha ng rx-rate at tx-rate mula sa session data
        - Nag-convert ng bytes to Mbps
        - Nagbabalik ng dict na may: username, rx_bytes_per_sec, tx_bytes_per_sec, rx_mbps, tx_mbps
        - Nagbabalik ng None kung hindi nahanap ang user
        """
        # Filter out invalid usernames
        assume(len(username.strip()) >= 3)
        
        service = MikrotikService(
            host='192.168.10.5',
            username='admin',
            password='adminTaboo'
        )
        
        # Mock the API connection
        mock_api = MagicMock()
        service._api = mock_api
        
        # Mock PPP active resource
        mock_active = MagicMock()
        mock_api.get_resource.return_value = mock_active
        
        # Mock user is online with bandwidth data
        mock_active.get.return_value = [
            {
                'name': username,
                'address': '10.0.0.1',
                'service': 'pppoe',
                'rx-rate': '5000000',  # 5 Mbps in bytes
                'tx-rate': '2000000'   # 2 Mbps in bytes
            }
        ]
        
        # Call the method
        result = service.get_session_bandwidth(username)
        
        # Verify preservation of behavior
        assert result is not None, "get_session_bandwidth should return data when user is online"
        assert isinstance(result, dict), "Result should be a dictionary"
        
        # Verify the response format
        assert 'username' in result, "Result should have 'username' field"
        assert 'rx_bytes_per_sec' in result, "Result should have 'rx_bytes_per_sec' field"
        assert 'tx_bytes_per_sec' in result, "Result should have 'tx_bytes_per_sec' field"
        assert 'rx_mbps' in result, "Result should have 'rx_mbps' field"
        assert 'tx_mbps' in result, "Result should have 'tx_mbps' field"
        
        # Verify the values
        assert result['username'] == username, "Username should match"
        assert result['rx_bytes_per_sec'] == 5000000, "RX bytes should match"
        assert result['tx_bytes_per_sec'] == 2000000, "TX bytes should match"
        
        # Verify the method called the correct resource
        mock_api.get_resource.assert_called_once_with('/ppp/active')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
