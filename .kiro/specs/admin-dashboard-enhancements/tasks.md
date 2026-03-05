# Implementation Plan: Admin Dashboard Enhancements

## Overview

This implementation plan adds three key capabilities to the ISP Billing System admin dashboard: inline plan editing, real-time bandwidth monitoring, and quick client disconnect functionality. The implementation follows a backend-first approach, building the service layer and API endpoints before integrating with the frontend components.

## Tasks

- [x] 1. Set up bandwidth monitoring infrastructure
  - [x] 1.1 Create BandwidthService with caching mechanism
    - Implement in-memory cache with 5-second TTL
    - Add cache validation and clearing methods
    - Implement `_is_cache_valid()` helper method
    - _Requirements: 5.6_
  
  - [x] 1.2 Implement bandwidth unit conversion utility
    - Create `convert_bytes_to_mbps()` function
    - Handle conversion from bytes per second to Mbps
    - _Requirements: 5.4_
  
  - [ ]* 1.3 Write property test for bandwidth unit conversion
    - **Property 11: Bandwidth Unit Conversion Accuracy**
    - **Validates: Requirements 5.4**
  
  - [x] 1.4 Add bandwidth threshold configuration
    - Add `BANDWIDTH_THRESHOLD_RX` to config.py
    - Add `BANDWIDTH_THRESHOLD_TX` to config.py
    - Add `BANDWIDTH_CACHE_TTL` to config.py
    - Add `BANDWIDTH_UPDATE_INTERVAL` to config.py
    - _Requirements: 3.8_

- [x] 2. Extend MikrotikService with bandwidth and disconnect methods
  - [x] 2.1 Implement `get_session_bandwidth()` method
    - Query Mikrotik API for specific PPPoE session
    - Extract RX and TX bytes per second
    - Convert to Mbps using utility function
    - Handle connection errors gracefully
    - _Requirements: 5.1, 5.2, 5.3_
  
  - [x] 2.2 Implement `get_all_sessions_bandwidth()` method
    - Use batch query to fetch all active sessions
    - Extract bandwidth data for each session
    - Match PPPoE usernames to database clients
    - _Requirements: 5.1, 5.7, 7.1_
  
  - [ ]* 2.3 Write property test for bandwidth data completeness
    - **Property 4: Bandwidth Data Completeness**
    - **Validates: Requirements 2.2, 2.3, 5.2, 5.3**
  
  - [x] 2.4 Implement `disconnect_pppoe_session()` method
    - Find active session by username
    - Terminate PPPoE session via Mikrotik API
    - Return success/failure status
    - Handle errors (session not found, connection timeout)
    - _Requirements: 4.4_
  
  - [ ]* 2.5 Write unit tests for MikrotikService extensions
    - Test connection error handling
    - Test session not found scenarios
    - Test successful disconnect operation

- [x] 3. Implement BandwidthService core methods
  - [x] 3.1 Implement `get_client_bandwidth()` method
    - Query client from database by ID
    - Get PPPoE username from client record
    - Fetch bandwidth data from MikrotikService
    - Return formatted bandwidth data with online status
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  
  - [x] 3.2 Implement `get_all_bandwidth()` method
    - Check cache validity first
    - If cache miss, fetch from MikrotikService
    - Match sessions to database clients
    - Store results in cache
    - Return list of bandwidth data per client
    - _Requirements: 2.1, 5.6_
  
  - [ ]* 3.3 Write property test for cache behavior
    - **Property 12: Cache Prevents Redundant API Calls**
    - **Validates: Requirements 5.6**
  
  - [x] 3.4 Implement `calculate_congestion_status()` method
    - Calculate percentage of threshold
    - Return 'normal' if < 80%
    - Return 'warning' if 80-100%
    - Return 'critical' if > 100%
    - _Requirements: 3.6, 3.7_
  
  - [ ]* 3.5 Write property test for congestion status
    - **Property 6: Congestion Status Correctness**
    - **Validates: Requirements 3.6, 3.7**
  
  - [x] 3.6 Implement `get_total_bandwidth()` method
    - Get all bandwidth data
    - Sum RX values for total RX
    - Sum TX values for total TX
    - Calculate congestion status for RX and TX
    - Return aggregated data with thresholds
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  
  - [ ]* 3.7 Write property test for total bandwidth calculation
    - **Property 5: Total Bandwidth Calculation Accuracy**
    - **Validates: Requirements 3.1, 3.2**

- [x] 4. Checkpoint - Ensure service layer tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Create bandwidth monitoring API endpoints
  - [x] 5.1 Create new routes file `routes/bandwidth.py`
    - Set up Flask blueprint for bandwidth routes
    - Add authentication decorator requirement
    - _Requirements: 6.6_
  
  - [x] 5.2 Implement GET `/api/bandwidth/all` endpoint
    - Call `BandwidthService.get_all_bandwidth()`
    - Handle Mikrotik connection errors
    - Return JSON response with bandwidth data
    - Include timestamp in response
    - _Requirements: 2.1, 6.1, 6.4_
  
  - [x] 5.3 Implement GET `/api/bandwidth/total` endpoint
    - Call `BandwidthService.get_total_bandwidth()`
    - Return aggregated bandwidth with congestion status
    - Include thresholds in response
    - _Requirements: 3.1, 3.2, 3.5_
  
  - [ ]* 5.4 Write unit tests for bandwidth API endpoints
    - Test successful responses
    - Test Mikrotik connection error handling
    - Test JSON response format

- [x] 6. Create client management API endpoints
  - [x] 6.1 Implement PATCH `/api/clients/{id}/plan` endpoint
    - Validate request data (plan_name, plan_amount)
    - Check plan_name is not empty and <= 100 chars
    - Check plan_amount is positive number
    - Call ClientService to update client
    - Return updated client data
    - _Requirements: 1.2, 1.3_
  
  - [ ]* 6.2 Write property test for plan update persistence
    - **Property 1: Plan Update Persistence**
    - **Validates: Requirements 1.2**
  
  - [ ]* 6.3 Write property test for invalid plan rejection
    - **Property 2: Invalid Plan Rejection**
    - **Validates: Requirements 1.3**
  
  - [x] 6.4 Implement POST `/api/clients/{id}/disconnect` endpoint
    - Get client from database
    - Check if client has active session
    - Call `MikrotikService.disconnect_pppoe_session()`
    - Return success message or error
    - _Requirements: 4.4, 4.5_
  
  - [ ]* 6.5 Write property test for disconnect status update
    - **Property 9: Successful Disconnect Updates Status**
    - **Validates: Requirements 4.5, 4.8**
  
  - [ ]* 6.6 Write unit tests for client API endpoints
    - Test plan validation errors
    - Test disconnect with offline client
    - Test disconnect with Mikrotik errors

- [x] 7. Register new API routes in application
  - [x] 7.1 Import bandwidth blueprint in `app.py`
    - Add import statement for bandwidth routes
    - Register blueprint with `/api` prefix
  
  - [x] 7.2 Update client routes if needed
    - Ensure client routes support new endpoints
    - Add any missing authentication checks

- [x] 8. Checkpoint - Ensure API tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Implement frontend bandwidth monitoring component
  - [x] 9.1 Create `static/js/bandwidth-monitor.js`
    - Implement BandwidthMonitor class
    - Add `start()` and `stop()` methods for polling
    - Implement `fetchBandwidthData()` for client bandwidth
    - Implement `fetchTotalBandwidth()` for ISP totals
    - Set update interval to 10 seconds
    - _Requirements: 2.5, 3.5_
  
  - [x] 9.2 Implement client row update method
    - Add `updateClientRow()` to update specific table rows
    - Display RX and TX values in Mbps
    - Show "Offline" status for inactive clients
    - _Requirements: 2.2, 2.3, 2.4_
  
  - [x] 9.3 Implement total bandwidth display method
    - Add `updateTotalDisplay()` for dashboard totals
    - Display total RX and TX
    - Show active session count
    - _Requirements: 3.3, 3.4_
  
  - [x] 9.4 Implement congestion indicator display
    - Add `showCongestionIndicator()` method
    - Show green for 'normal' status
    - Show yellow for 'warning' status
    - Show red for 'critical' status
    - _Requirements: 3.6, 3.7_
  
  - [x] 9.5 Add error handling and loading states
    - Display loading indicator during fetch
    - Show error banner if Mikrotik connection fails
    - Handle timeout warnings (> 5 seconds)
    - _Requirements: 6.1, 6.4, 7.5_

- [x] 10. Implement frontend inline plan editor component
  - [x] 10.1 Create `static/js/plan-editor.js`
    - Implement InlinePlanEditor class
    - Add constructor with clientId, fieldName, currentValue
    - Store original value for cancellation
    - _Requirements: 1.1_
  
  - [x] 10.2 Implement edit activation method
    - Add `activate()` to convert display to input field
    - Show save and cancel buttons
    - Focus on input field
    - _Requirements: 1.1_
  
  - [x] 10.3 Implement validation method
    - Add `validate()` for client-side validation
    - Check plan_name is not empty
    - Check plan_amount is positive number
    - Show inline error messages
    - _Requirements: 1.3_
  
  - [x] 10.4 Implement save method
    - Add `async save()` to send PATCH request
    - Validate before sending
    - Handle success response
    - Update display with new value
    - Show success message
    - _Requirements: 1.2, 1.4_
  
  - [x] 10.5 Implement cancel method
    - Add `cancel()` to restore original value
    - Hide input field and buttons
    - Return to display mode
    - _Requirements: 1.5_
  
  - [ ]* 10.6 Write property test for edit cancellation
    - **Property 3: Edit Cancellation Restores Original**
    - **Validates: Requirements 1.5**
  
  - [x] 10.7 Add error display methods
    - Implement `showError()` for validation errors
    - Implement `showSuccess()` for successful saves
    - Auto-dismiss success message after 3 seconds
    - _Requirements: 6.2, 6.5_

- [x] 11. Implement frontend disconnect button component
  - [x] 11.1 Create `static/js/disconnect-button.js`
    - Implement DisconnectButton class
    - Add constructor with clientId and username
    - _Requirements: 4.1_
  
  - [x] 11.2 Implement confirmation dialog
    - Add `showConfirmation()` method
    - Display client name in confirmation message
    - Handle confirm and cancel actions
    - _Requirements: 4.3_
  
  - [x] 11.3 Implement disconnect method
    - Add `async disconnect()` to send POST request
    - Show confirmation dialog first
    - Handle success response
    - Update client status display
    - _Requirements: 4.4, 4.5_
  
  - [x] 11.4 Implement status update method
    - Add `updateClientStatus()` to change display
    - Hide disconnect button after successful disconnect
    - Update bandwidth display to "Offline"
    - _Requirements: 4.8_
  
  - [ ]* 11.5 Write property test for disconnect button visibility
    - **Property 8: Disconnect Button Visibility**
    - **Validates: Requirements 4.1, 4.2**
  
  - [x] 11.6 Add error handling
    - Display error message if disconnect fails
    - Show troubleshooting hints
    - Keep button visible on failure
    - _Requirements: 4.6, 6.3_

- [x] 12. Checkpoint - Ensure frontend components work
  - Ensure all tests pass, ask the user if questions arise.

- [x] 13. Update dashboard template with bandwidth display
  - [x] 13.1 Add total bandwidth display section to `templates/dashboard.html`
    - Add container for total RX/TX display
    - Add congestion indicator elements
    - Add active sessions count display
    - _Requirements: 3.3, 3.4, 3.5_
  
  - [x] 13.2 Include bandwidth monitor JavaScript
    - Add script tag for bandwidth-monitor.js
    - Initialize BandwidthMonitor on page load
    - Start polling when dashboard loads
    - _Requirements: 2.5, 3.5_
  
  - [x] 13.3 Add CSS styles for congestion indicators
    - Style normal indicator (green)
    - Style warning indicator (yellow)
    - Style critical indicator (red)
    - Add loading spinner styles
    - _Requirements: 3.6, 3.7_

- [x] 14. Update client list template with inline editing and disconnect
  - [x] 14.1 Modify client list table in `templates/clients/list.html`
    - Add bandwidth columns (RX Mbps, TX Mbps)
    - Make plan_name and plan_amount fields clickable
    - Add data attributes for client IDs
    - _Requirements: 1.1, 2.2, 2.3_
  
  - [x] 14.2 Add disconnect button column
    - Add button for online clients only
    - Use conditional rendering based on status
    - Add appropriate styling
    - _Requirements: 4.1, 4.2_
  
  - [x] 14.3 Include JavaScript components
    - Add script tags for plan-editor.js
    - Add script tags for disconnect-button.js
    - Add script tags for bandwidth-monitor.js
    - Initialize components on page load
    - _Requirements: 1.1, 2.1, 4.1_
  
  - [x] 14.4 Add event listeners for inline editing
    - Attach click handlers to plan fields
    - Initialize InlinePlanEditor on click
    - Handle save and cancel events
    - _Requirements: 1.1, 1.2, 1.5_
  
  - [x] 14.5 Add event listeners for disconnect buttons
    - Attach click handlers to disconnect buttons
    - Initialize DisconnectButton on click
    - Handle confirmation and status updates
    - _Requirements: 4.3, 4.4_

- [x] 15. Update client detail page with bandwidth and disconnect
  - [x] 15.1 Add bandwidth display to `templates/clients/detail.html`
    - Show current RX and TX if online
    - Show "Offline" status if not connected
    - _Requirements: 2.6_
  
  - [x] 15.2 Add disconnect button to detail page
    - Show button only if client is online
    - Use same DisconnectButton component
    - _Requirements: 4.7_

- [x] 16. Implement performance optimizations
  - [x] 16.1 Add pagination to client list
    - Implement pagination if client count > 50
    - Show 50 clients per page
    - Add page navigation controls
    - _Requirements: 7.2_
  
  - [ ]* 16.2 Write property test for pagination trigger
    - **Property 15: Pagination Triggers at Threshold**
    - **Validates: Requirements 7.2**
  
  - [x] 16.3 Implement lazy loading for bandwidth data
    - Load bandwidth only for visible clients on current page
    - Skip bandwidth fetch for other pages
    - _Requirements: 7.4_
  
  - [ ]* 16.4 Write property test for lazy loading
    - **Property 16: Lazy Loading for Visible Clients Only**
    - **Validates: Requirements 7.4**
  
  - [x] 16.5 Add asynchronous request handling
    - Use async/await for all API calls
    - Prevent UI blocking during data fetch
    - _Requirements: 7.3_
  
  - [x] 16.6 Implement concurrent request limiting
    - Limit to 5 concurrent Mikrotik API requests
    - Queue additional requests
    - _Requirements: 7.6_
  
  - [ ]* 16.7 Write property test for concurrent request limiting
    - **Property 17: Concurrent Request Limiting**
    - **Validates: Requirements 7.6**

- [x] 17. Add comprehensive error handling
  - [x] 17.1 Implement error banner component
    - Create reusable error banner for dashboard
    - Support different severity levels (error, warning, info)
    - Add auto-dismiss for non-critical errors
    - Add manual dismiss button for critical errors
    - _Requirements: 6.1, 6.4_
  
  - [x] 17.2 Add timeout warning display
    - Show warning after 5 seconds of waiting
    - Provide manual refresh option
    - _Requirements: 7.5_
  
  - [x] 17.3 Implement access denied handling
    - Check user permissions before operations
    - Display "Access Denied" message if unauthorized
    - _Requirements: 6.6_
  
  - [ ]* 17.4 Write property test for error handling
    - **Property 10: Failed Operations Return Errors**
    - **Validates: Requirements 4.6, 6.2, 6.3**

- [x] 18. Write integration tests
  - [ ]* 18.1 Write integration test for bandwidth monitoring flow
    - Test end-to-end bandwidth fetch and display
    - Mock Mikrotik API responses
    - Verify cache behavior
  
  - [ ]* 18.2 Write integration test for plan editing flow
    - Test complete edit, validate, save flow
    - Verify database updates
    - Test error scenarios
  
  - [ ]* 18.3 Write integration test for disconnect flow
    - Test complete disconnect operation
    - Verify Mikrotik API call
    - Verify status updates

- [x] 19. Final checkpoint - Complete testing and verification
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- The implementation follows a backend-first approach: services → API → frontend
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties across all inputs
- Unit tests validate specific examples and edge cases
- All bandwidth values are displayed in Mbps for consistency
- Cache TTL is set to 5 seconds to balance freshness and performance
- Frontend polling interval is 10 seconds for real-time feel without overwhelming the router
