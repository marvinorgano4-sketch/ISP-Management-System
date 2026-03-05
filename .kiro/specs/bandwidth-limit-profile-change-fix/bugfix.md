# Bugfix Requirements Document

## Introduction

The bandwidth limit feature fails when attempting to set bandwidth limits for PPPoE users through the web interface. When users click "Apply Limit" in the bandwidth modal, the system attempts to change the user's PPP profile to match the requested speed (e.g., "5MBPS", "10MBPS") but fails with errors. Additionally, the system has broader Mikrotik API communication issues that affect multiple features including adding clients and retrieving connection status.

The bug has two components:
1. **API Communication Issue**: The billing system is not properly communicating with the Mikrotik router, causing failures across multiple operations
2. **Profile Matching Issue**: The `set_bandwidth_limit()` method in `services/mikrotik_service.py` makes incorrect assumptions about profile naming and doesn't verify profile existence before attempting assignment

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN the billing system attempts to communicate with the Mikrotik API THEN the connection fails or times out, preventing any Mikrotik operations from completing

1.2 WHEN an administrator tries to add a new client THEN the system fails to create the PPPoE user in Mikrotik due to API communication errors

1.3 WHEN viewing a client's detail page THEN the connection status section fails to retrieve online/offline status from Mikrotik

1.4 WHEN an administrator sets a bandwidth limit through the web interface THEN the system attempts to change the PPPoE user's profile to a profile name constructed as "{speed}MBPS" without verifying the profile exists

1.5 WHEN the constructed profile name doesn't match any existing profile in Mikrotik THEN the system fails with an error and the bandwidth limit is not applied

1.6 WHEN the administrator sets asymmetric speeds (different download/upload) THEN the system ignores the upload speed and only uses the download speed to determine the profile name

1.7 WHEN any Mikrotik operation fails THEN the system returns generic error messages without indicating the root cause or available options

### Expected Behavior (Correct)

2.1 WHEN the billing system starts up or attempts Mikrotik operations THEN the system SHALL successfully establish and maintain a connection to the Mikrotik API using the configured credentials

2.2 WHEN the Mikrotik API connection fails THEN the system SHALL provide clear error messages indicating connection issues, credential problems, or network connectivity issues

2.3 WHEN an administrator adds a new client THEN the system SHALL successfully create the PPPoE user in Mikrotik with the specified username, password, and profile

2.4 WHEN viewing a client's detail page THEN the system SHALL successfully retrieve and display the connection status (online/offline) from Mikrotik

2.5 WHEN an administrator sets a bandwidth limit through the web interface THEN the system SHALL retrieve the list of available PPP profiles from Mikrotik before attempting assignment

2.6 WHEN the system needs to determine which profile to use THEN the system SHALL match the requested speeds against available profiles using a flexible matching algorithm that handles different naming conventions (e.g., "5MBPS", "5Mbps", "5M", "5mbps")

2.7 WHEN no exact profile match is found for the requested speeds THEN the system SHALL return a clear error message indicating which profiles are available

2.8 WHEN a matching profile is found THEN the system SHALL successfully change the user's profile and apply the bandwidth limit

2.9 WHEN the profile change is successful THEN the system SHALL return a success message confirming the new bandwidth limit

### Unchanged Behavior (Regression Prevention)

3.1 WHEN the PPPoE username provided doesn't exist THEN the system SHALL CONTINUE TO raise a ValueError with message "PPPoE user '{username}' not found"

3.2 WHEN the Mikrotik API connection fails after multiple retry attempts THEN the system SHALL CONTINUE TO raise an Exception with appropriate error details

3.3 WHEN the bandwidth limit is successfully applied THEN the system SHALL CONTINUE TO log the operation with username, profile name, and speeds

3.4 WHEN the API endpoint receives invalid input (missing fields, invalid values) THEN the system SHALL CONTINUE TO return a 400 error with appropriate validation messages

3.5 WHEN the user is not authenticated THEN the system SHALL CONTINUE TO require login before allowing bandwidth limit changes

3.6 WHEN creating a new PPPoE user with valid credentials THEN the system SHALL CONTINUE TO successfully create the user in Mikrotik

3.7 WHEN deleting a client THEN the system SHALL CONTINUE TO remove the PPPoE user from Mikrotik

3.8 WHEN retrieving active PPPoE sessions THEN the system SHALL CONTINUE TO return accurate session information including IP addresses and uptime
