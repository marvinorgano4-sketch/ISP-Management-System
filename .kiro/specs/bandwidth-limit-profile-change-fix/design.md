# Bandwidth Limit Profile Change Fix - Bugfix Design

## Overview

This bugfix addresses two critical issues preventing bandwidth limit changes from working: (1) Mikrotik API connection failures that affect all router operations, and (2) incorrect assumptions about PPP profile naming that cause profile assignment to fail. The fix will implement proper connection handling with retry logic, add profile discovery to retrieve available profiles from the router, and implement flexible profile matching that handles various naming conventions. This ensures bandwidth limits can be successfully applied while preserving all existing functionality for other Mikrotik operations.

## Glossary

- **Bug_Condition (C)**: The condition that triggers the bug - when attempting to set bandwidth limits or when API connection fails
- **Property (P)**: The desired behavior - successful API connection and correct profile assignment based on available profiles
- **Preservation**: Existing Mikrotik operations (create user, delete user, get sessions, disconnect) that must remain unchanged
- **set_bandwidth_limit()**: The method in `services/mikrotik_service.py` that changes a user's PPP profile to apply bandwidth limits
- **PPP Profile**: A Mikrotik configuration object that defines bandwidth limits, queue settings, and other parameters for PPPoE users
- **Profile Discovery**: The process of querying Mikrotik to retrieve the list of available PPP profiles before attempting assignment
- **Profile Matching**: The algorithm that maps requested speeds (e.g., 5 Mbps) to available profile names (e.g., "5MBPS", "5Mbps", "5M")
- **RouterOsApiPool**: The library class used to establish connections to Mikrotik routers via the API
- **plaintext_login**: Connection parameter that enables compatibility with RouterOS v7

## Bug Details

### Fault Condition

The bug manifests in two scenarios: (1) when the billing system attempts any Mikrotik API operation and the connection fails or times out, preventing all router interactions, or (2) when `set_bandwidth_limit()` is called with valid speeds but constructs a profile name that doesn't exist in the router, causing the profile assignment to fail.

**Formal Specification:**
```
FUNCTION isBugCondition(input)
  INPUT: input of type BandwidthLimitRequest OR MikrotikOperation
  OUTPUT: boolean
  
  IF input is MikrotikOperation THEN
    RETURN connectionFails(input.host, input.credentials)
           OR connectionTimesOut(input.host, input.port)
  END IF
  
  IF input is BandwidthLimitRequest THEN
    RETURN input.username EXISTS in Mikrotik
           AND constructedProfileName(input.download_bps) NOT IN availableProfiles()
           AND NOT connectionFails()
  END IF
END FUNCTION

FUNCTION constructedProfileName(download_bps)
  download_mbps := download_bps / 1000000
  RETURN "{download_mbps}MBPS"
END FUNCTION
```

### Examples

- **API Connection Failure**: Administrator tries to add client "juan_dela_cruz" → System attempts to create PPPoE user → Connection to 192.168.88.1:8728 times out → Error: "Failed to connect to Mikrotik" → User not created
- **Profile Mismatch**: Administrator sets 5 Mbps limit for user "maria_santos" → System constructs profile name "5MBPS" → Mikrotik has profiles named "5Mbps", "10Mbps", "15Mbps" → Profile "5MBPS" not found → Error: "Profile not found" → Bandwidth limit not applied
- **Asymmetric Speed Ignored**: Administrator sets 10 Mbps download / 5 Mbps upload → System only uses download speed → Constructs "10MBPS" → Upload speed preference is lost
- **Edge Case - No Matching Profile**: Administrator sets 7 Mbps limit → System constructs "7MBPS" → Available profiles are "5Mbps", "10Mbps", "15Mbps" → No profile matches 7 Mbps → Should return clear error listing available profiles

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Creating PPPoE users with `create_pppoe_user()` must continue to work exactly as before
- Deleting PPPoE users with `delete_pppoe_user()` must continue to work exactly as before
- Retrieving active sessions with `get_active_pppoe_users()` must continue to work exactly as before
- Disconnecting sessions with `disconnect_pppoe_session()` must continue to work exactly as before
- Getting bandwidth statistics with `get_session_bandwidth()` must continue to work exactly as before
- Context manager behavior (`__enter__` and `__exit__`) must remain unchanged
- Error handling for non-existent users must continue to raise ValueError
- Logging behavior for successful operations must remain unchanged

**Scope:**
All Mikrotik operations that do NOT involve setting bandwidth limits or establishing initial connections should be completely unaffected by this fix. This includes:
- User creation and deletion operations
- Session monitoring and disconnection
- Bandwidth statistics retrieval
- All other PPP secret management operations

## Hypothesized Root Cause

Based on the bug description and code analysis, the most likely issues are:

1. **Connection Configuration Issues**: The `connect()` method may be using incorrect parameters for RouterOS v7
   - The `plaintext_login=True` parameter is present but connection still fails
   - Port 8728 may not be accessible or API service may not be enabled
   - Network connectivity between billing system and router may be blocked
   - Credentials may be incorrect or API user may lack permissions

2. **Missing Connection Retry Logic**: The connection attempt has no retry mechanism
   - Single connection failure causes immediate exception
   - Transient network issues cause permanent failures
   - No exponential backoff or retry strategy

3. **Hardcoded Profile Name Construction**: The `set_bandwidth_limit()` method constructs profile names as "{speed}MBPS" without checking what profiles actually exist
   - Assumes all profiles follow exact "XMBPS" naming convention
   - Doesn't query `/ppp/profile` to discover available profiles
   - No fallback or fuzzy matching for different naming conventions

4. **Case Sensitivity Issues**: Profile name matching may be case-sensitive
   - Mikrotik profile names could be "5Mbps" but code constructs "5MBPS"
   - No normalization or case-insensitive comparison

5. **Missing Profile Validation**: No verification that the constructed profile name exists before attempting assignment
   - Fails at assignment time rather than validation time
   - No helpful error message listing available profiles

## Correctness Properties

Property 1: Fault Condition - API Connection Success

_For any_ Mikrotik operation where the router is accessible and credentials are valid, the fixed `connect()` method SHALL successfully establish an API connection within the retry limit, enabling all subsequent Mikrotik operations to execute correctly.

**Validates: Requirements 2.1, 2.2**

Property 2: Fault Condition - Profile Discovery and Matching

_For any_ bandwidth limit request where the PPPoE user exists and a matching profile is available in Mikrotik, the fixed `set_bandwidth_limit()` method SHALL discover available profiles, match the requested speed to an existing profile using flexible matching, and successfully assign that profile to the user.

**Validates: Requirements 2.5, 2.6, 2.7, 2.8, 2.9**

Property 3: Preservation - Existing Mikrotik Operations

_For any_ Mikrotik operation that is NOT `set_bandwidth_limit()` or `connect()` (such as create_pppoe_user, delete_pppoe_user, get_active_pppoe_users, disconnect_pppoe_session), the fixed code SHALL produce exactly the same behavior as the original code, preserving all existing functionality for user management, session monitoring, and statistics retrieval.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8**

## Fix Implementation

### Changes Required

Assuming our root cause analysis is correct:

**File**: `services/mikrotik_service.py`

**Function**: `connect()`

**Specific Changes**:
1. **Add Connection Retry Logic**: Implement exponential backoff retry mechanism
   - Add `max_retries` parameter (default: 3)
   - Add `retry_delay` parameter (default: 2 seconds)
   - Implement retry loop with exponential backoff
   - Log each retry attempt with details

2. **Improve Error Messages**: Provide specific connection failure details
   - Distinguish between network errors, authentication errors, and timeout errors
   - Include router host/port in error messages
   - Suggest troubleshooting steps in error messages

3. **Add Connection Validation**: Verify connection is actually working after establishment
   - Test connection with simple API call (e.g., `/system/identity`)
   - Ensure API object is functional before returning success

**Function**: `set_bandwidth_limit()`

**Specific Changes**:
1. **Add Profile Discovery**: Query Mikrotik for available PPP profiles
   - Add new method `get_ppp_profiles()` to retrieve all profiles from `/ppp/profile`
   - Cache profiles for performance (optional)
   - Return list of profile dictionaries with name and rate-limit information

2. **Implement Flexible Profile Matching**: Match requested speeds to available profiles
   - Add new method `find_matching_profile(download_mbps, upload_mbps, profiles)` 
   - Support multiple naming conventions: "XMBPS", "XMbps", "XM", "Xmbps", "X_MBPS"
   - Implement case-insensitive matching
   - Parse profile rate-limit strings to extract actual speeds
   - Match based on download speed primarily, consider upload speed if specified

3. **Add Profile Validation**: Verify profile exists before assignment
   - Call `get_ppp_profiles()` before constructing profile name
   - Call `find_matching_profile()` to get actual profile name
   - If no match found, raise ValueError with list of available profiles

4. **Improve Error Messages**: Provide actionable feedback when profile not found
   - List all available profiles in error message
   - Show requested speeds vs available speeds
   - Suggest closest matching profile if available

5. **Add Logging**: Log profile discovery and matching process
   - Log available profiles found
   - Log matching algorithm results
   - Log successful profile assignment with actual profile name used

### New Methods to Add

**Method**: `get_ppp_profiles()`
```python
def get_ppp_profiles(self) -> list[dict]:
    """
    Retrieve all PPP profiles from Mikrotik.
    
    Returns:
        list[dict]: List of profile dictionaries with name and rate-limit info
    """
```

**Method**: `find_matching_profile(download_mbps, upload_mbps, profiles)`
```python
def find_matching_profile(self, download_mbps: int, upload_mbps: int, 
                         profiles: list[dict]) -> Optional[str]:
    """
    Find a profile that matches the requested speeds.
    
    Args:
        download_mbps: Requested download speed in Mbps
        upload_mbps: Requested upload speed in Mbps
        profiles: List of available profile dictionaries
        
    Returns:
        str: Matching profile name, or None if no match found
    """
```

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate the bug on unfixed code, then verify the fix works correctly and preserves existing behavior.

### Exploratory Fault Condition Checking

**Goal**: Surface counterexamples that demonstrate the bug BEFORE implementing the fix. Confirm or refute the root cause analysis. If we refute, we will need to re-hypothesize.

**Test Plan**: Write tests that attempt to connect to Mikrotik and set bandwidth limits using the UNFIXED code. Run these tests to observe failures and understand the root cause.

**Test Cases**:
1. **Connection Failure Test**: Attempt to connect to Mikrotik with correct credentials (will fail on unfixed code if connection issues exist)
2. **Profile Mismatch Test**: Call `set_bandwidth_limit("test_user", 5000000, 5000000)` when profile "5MBPS" doesn't exist but "5Mbps" does (will fail on unfixed code)
3. **Profile Discovery Test**: Try to retrieve list of PPP profiles (method doesn't exist in unfixed code)
4. **Case Sensitivity Test**: Create profile "5Mbps" in Mikrotik, call `set_bandwidth_limit()` with 5 Mbps (will fail if case-sensitive matching is the issue)

**Expected Counterexamples**:
- Connection attempts fail with timeout or authentication errors
- Profile assignment fails with "Profile not found" or similar error
- No method exists to discover available profiles
- Possible causes: incorrect connection parameters, missing retry logic, hardcoded profile names, case-sensitive matching

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds, the fixed function produces the expected behavior.

**Pseudocode:**
```
FOR ALL input WHERE isBugCondition(input) DO
  IF input is MikrotikOperation THEN
    result := connect_fixed(input.host, input.credentials)
    ASSERT result.connected = true
    ASSERT result.api_functional = true
  END IF
  
  IF input is BandwidthLimitRequest THEN
    profiles := get_ppp_profiles_fixed()
    matching_profile := find_matching_profile_fixed(input.download_mbps, input.upload_mbps, profiles)
    result := set_bandwidth_limit_fixed(input.username, input.download_bps, input.upload_bps)
    ASSERT result.success = true
    ASSERT result.profile_assigned = matching_profile
  END IF
END FOR
```

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold, the fixed function produces the same result as the original function.

**Pseudocode:**
```
FOR ALL input WHERE NOT isBugCondition(input) DO
  IF input is CreateUserOperation THEN
    ASSERT create_pppoe_user_original(input) = create_pppoe_user_fixed(input)
  END IF
  
  IF input is DeleteUserOperation THEN
    ASSERT delete_pppoe_user_original(input) = delete_pppoe_user_fixed(input)
  END IF
  
  IF input is GetSessionsOperation THEN
    ASSERT get_active_pppoe_users_original() = get_active_pppoe_users_fixed()
  END IF
  
  IF input is DisconnectOperation THEN
    ASSERT disconnect_pppoe_session_original(input) = disconnect_pppoe_session_fixed(input)
  END IF
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many test cases automatically across the input domain
- It catches edge cases that manual unit tests might miss
- It provides strong guarantees that behavior is unchanged for all non-buggy inputs

**Test Plan**: Observe behavior on UNFIXED code first for user creation, deletion, session retrieval, and disconnection operations, then write property-based tests capturing that behavior.

**Test Cases**:
1. **User Creation Preservation**: Observe that `create_pppoe_user()` works correctly on unfixed code, then write test to verify this continues after fix
2. **User Deletion Preservation**: Observe that `delete_pppoe_user()` works correctly on unfixed code, then write test to verify this continues after fix
3. **Session Retrieval Preservation**: Observe that `get_active_pppoe_users()` works correctly on unfixed code, then write test to verify this continues after fix
4. **Disconnection Preservation**: Observe that `disconnect_pppoe_session()` works correctly on unfixed code, then write test to verify this continues after fix

### Unit Tests

- Test `connect()` with valid credentials and verify successful connection
- Test `connect()` with invalid credentials and verify appropriate error
- Test `connect()` with unreachable host and verify retry logic executes
- Test `get_ppp_profiles()` returns list of profiles with correct structure
- Test `find_matching_profile()` with exact match (e.g., "5MBPS" profile exists)
- Test `find_matching_profile()` with case-insensitive match (e.g., "5Mbps" vs "5MBPS")
- Test `find_matching_profile()` with different naming conventions (e.g., "5M", "5_MBPS")
- Test `find_matching_profile()` with no match returns None
- Test `set_bandwidth_limit()` with matching profile succeeds
- Test `set_bandwidth_limit()` with no matching profile raises ValueError with available profiles
- Test `set_bandwidth_limit()` with non-existent user raises ValueError

### Property-Based Tests

- Generate random valid credentials and verify connection succeeds or fails appropriately
- Generate random profile lists and requested speeds, verify matching algorithm finds correct profile or returns None
- Generate random PPPoE usernames and verify user creation/deletion operations work identically before and after fix
- Generate random session data and verify session retrieval operations work identically before and after fix

### Integration Tests

- Test full flow: connect → get profiles → find match → set bandwidth limit → verify user has new profile
- Test full flow with connection retry: simulate transient network failure → verify retry succeeds → complete bandwidth limit change
- Test full flow with no matching profile: connect → get profiles → attempt to set non-existent speed → verify error message lists available profiles
- Test that other operations (create user, delete user, get sessions) continue to work after implementing bandwidth limit fix
- Test switching between different bandwidth limits for same user multiple times
- Test setting bandwidth limits for multiple users in sequence
