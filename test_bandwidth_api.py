"""Test script to check bandwidth API"""
from services.mikrotik_service import MikrotikService
from services.bandwidth_service import BandwidthService
from config import Config

print("Testing Mikrotik Bandwidth Monitoring...")
print("=" * 50)

try:
    # Test Mikrotik connection
    print("\n1. Testing Mikrotik connection...")
    mikrotik = MikrotikService(
        host=Config.MIKROTIK_HOST,
        username=Config.MIKROTIK_USER,
        password=Config.MIKROTIK_PASSWORD
    )
    mikrotik.connect()
    print("✓ Connected to Mikrotik successfully")
    
    # Test getting active sessions
    print("\n2. Getting active PPPoE sessions...")
    active_users = mikrotik.get_active_pppoe_users()
    print(f"✓ Found {len(active_users)} active sessions")
    
    if active_users:
        print("\nActive sessions:")
        for user in active_users[:5]:  # Show first 5
            print(f"  - {user['name']}: {user['address']} (uptime: {user['uptime']})")
    
    # Test getting bandwidth data
    print("\n3. Getting bandwidth data for all sessions...")
    bandwidth_data = mikrotik.get_all_sessions_bandwidth()
    print(f"✓ Retrieved bandwidth data for {len(bandwidth_data)} sessions")
    
    if bandwidth_data:
        print("\nBandwidth data (first 5 sessions):")
        for data in bandwidth_data[:5]:
            print(f"  - {data['username']}:")
            print(f"      RX: {data['rx_mbps']:.2f} Mbps ({data['rx_bytes_per_sec']} bytes/sec)")
            print(f"      TX: {data['tx_mbps']:.2f} Mbps ({data['tx_bytes_per_sec']} bytes/sec)")
    
    # Test BandwidthService
    print("\n4. Testing BandwidthService.get_total_bandwidth()...")
    total = BandwidthService.get_total_bandwidth()
    print(f"✓ Total bandwidth calculated:")
    print(f"  - Total RX: {total['total_rx_mbps']:.2f} Mbps")
    print(f"  - Total TX: {total['total_tx_mbps']:.2f} Mbps")
    print(f"  - Active sessions: {total['active_sessions']}")
    print(f"  - RX Congestion: {total['congestion_status_rx']}")
    print(f"  - TX Congestion: {total['congestion_status_tx']}")
    
    mikrotik.disconnect()
    print("\n✓ All tests passed!")
    
except Exception as e:
    print(f"\n✗ Error: {str(e)}")
    import traceback
    traceback.print_exc()
