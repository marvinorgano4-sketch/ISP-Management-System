"""Test Mikrotik Connection"""
import sys
from config import Config
from services.mikrotik_service import MikrotikService
from routeros_api.exceptions import RouterOsApiConnectionError

def test_connection():
    """Test connection to Mikrotik router"""
    print("=" * 60)
    print("Mikrotik Connection Test")
    print("=" * 60)
    print()
    
    # Get configuration
    host = Config.MIKROTIK_HOST
    user = Config.MIKROTIK_USER
    password = Config.MIKROTIK_PASSWORD
    
    print(f"Configuration:")
    print(f"  Host: {host}")
    print(f"  User: {user}")
    print(f"  Password: {'*' * len(password)}")
    print(f"  Port: 8728 (API)")
    print()
    
    # Test connection
    print("Testing connection...")
    print()
    
    try:
        mikrotik = MikrotikService(host, user, password)
        mikrotik.connect()
        print("✓ Connection successful!")
        print()
        
        # Try to get active users
        print("Fetching active PPPoE users...")
        users = mikrotik.get_active_pppoe_users()
        print(f"✓ Found {len(users)} active users")
        print()
        
        if users:
            print("Active users:")
            for user in users:
                print(f"  - {user['name']}: {user['address']} (uptime: {user['uptime']})")
        else:
            print("  No active users found")
        
        print()
        mikrotik.disconnect()
        print("✓ Disconnected successfully")
        print()
        print("=" * 60)
        print("TEST PASSED - Mikrotik connection is working!")
        print("=" * 60)
        return True
        
    except RouterOsApiConnectionError as e:
        print("✗ Connection failed!")
        print()
        print(f"Error: {str(e)}")
        print()
        print("Possible causes:")
        print("  1. Mikrotik API is not enabled")
        print("     Solution: Enable API in Mikrotik")
        print("     Winbox → IP → Services → Enable 'api'")
        print()
        print("  2. Wrong IP address")
        print(f"     Current: {host}")
        print("     Solution: Verify Mikrotik IP address")
        print()
        print("  3. Wrong username or password")
        print(f"     Current user: {user}")
        print("     Solution: Verify credentials in Mikrotik")
        print()
        print("  4. Firewall blocking port 8728")
        print("     Solution: Allow port 8728 in Mikrotik firewall")
        print()
        print("=" * 60)
        print("TEST FAILED - Cannot connect to Mikrotik")
        print("=" * 60)
        return False
        
    except Exception as e:
        print("✗ Unexpected error!")
        print()
        print(f"Error: {str(e)}")
        print()
        print("=" * 60)
        print("TEST FAILED - Unexpected error")
        print("=" * 60)
        return False

if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)
