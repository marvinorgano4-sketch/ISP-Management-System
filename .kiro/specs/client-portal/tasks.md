# Implementation Plan: Client Portal

## Overview

This implementation plan creates a self-service web portal for ISP clients to manage their accounts, view billing information, make GCash payments, and monitor connection status. The implementation extends the existing Flask application with a separate client authentication system, new routes, services, and mobile-responsive templates.

## Tasks

- [x] 1. Extend Client model and create database migration
  - Add password_hash field (String(255), nullable=False)
  - Add last_login field (DateTime, nullable=True)
  - Add set_password() method using bcrypt
  - Add check_password() method using bcrypt
  - Create Alembic migration script
  - Generate default passwords for existing clients (PPPoE username as initial password)
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ]* 1.1 Write property test for password hashing security
  - **Property 6: Password Storage Security**
  - **Validates: Requirements 2.2, 2.4**

- [x] 2. Implement ClientAuthService for authentication
  - [x] 2.1 Create services/client_auth_service.py with authentication methods
    - Implement authenticate_client(pppoe_username, password) method
    - Implement create_client_session(client) method
    - Implement destroy_client_session() method
    - Implement get_current_client() method
    - Implement require_client_login decorator
    - _Requirements: 1.2, 1.3, 1.4, 1.5, 1.6_
  
  - [ ]* 2.2 Write property tests for authentication
    - **Property 1: Valid Client Authentication ay Lumilikha ng Session**
    - **Validates: Requirements 1.2**
  
  - [ ]* 2.3 Write property test for invalid credentials
    - **Property 2: Invalid Credentials ay Tumatanggi ng Access**
    - **Validates: Requirements 1.3**
  
  - [ ]* 2.4 Write property test for session persistence
    - **Property 3: Session Persistence sa Maraming Requests**
    - **Validates: Requirements 1.4**
  
  - [ ]* 2.5 Write unit tests for session management
    - Test session creation and destruction
    - Test session timeout behavior
    - Test require_client_login decorator
    - _Requirements: 1.4, 1.5, 1.6_

- [x] 3. Implement ClientDashboardService for dashboard data
  - [x] 3.1 Create services/client_dashboard_service.py with dashboard methods
    - Implement get_dashboard_data(client_id) method
    - Implement calculate_remaining_days(client_id) method
    - Implement get_total_unpaid_balance(client_id) method
    - Implement get_connection_status(pppoe_username) method
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_
  
  - [ ]* 3.2 Write property test for remaining days calculation
    - **Property 8: Remaining Days Calculation Accuracy**
    - **Validates: Requirements 3.5**
  
  - [ ]* 3.3 Write property test for dashboard data completeness
    - **Property 7: Dashboard Data Completeness**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
  
  - [ ]* 3.4 Write unit tests for dashboard service
    - Test dashboard data aggregation with mock data
    - Test unpaid balance calculation with multiple bills
    - Test connection status display with online/offline states
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.6, 3.7_

- [x] 4. Implement GCashPaymentService for payment links
  - [x] 4.1 Create services/gcash_payment_service.py with payment methods
    - Define GCASH_NUMBER = "09495502589"
    - Define GCASH_NAME = "Jean Kimberlyn L"
    - Implement generate_payment_link(billing_id) method
    - Implement generate_reference_number(client_id, billing_id) method
    - _Requirements: 5.2, 5.3, 5.4, 5.5, 5.6_
  
  - [ ]* 4.2 Write property test for payment link completeness
    - **Property 14: GCash Payment Link Completeness**
    - **Validates: Requirements 5.2, 5.3, 5.4, 5.5, 5.6**
  
  - [ ]* 4.3 Write property test for reference number uniqueness
    - **Property 15: GCash Payment Link Reference Uniqueness**
    - **Validates: Requirements 5.6**
  
  - [ ]* 4.4 Write unit tests for GCash service
    - Test payment link generation with valid billing record
    - Test reference number format
    - Test error handling for paid bills
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

- [x] 5. Checkpoint - Ensure all service tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Create client portal base template
  - [x] 6.1 Create templates/client_base.html with client-specific layout
    - Create base HTML structure with Bootstrap
    - Add client-specific navigation (Dashboard, Bills, Payments)
    - Add mobile-responsive navbar with hamburger menu
    - Add logout button
    - Exclude admin functionality links
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 7. Create client portal templates
  - [x] 7.1 Create templates/client_login.html
    - Create login form with username and password fields
    - Add CSRF token
    - Add error message display
    - Make mobile-responsive
    - _Requirements: 1.1, 1.3, 9.4_
  
  - [x] 7.2 Create templates/client_dashboard.html
    - Create account summary cards (Remaining Days, Unpaid Balance, Connection Status, Plan Details)
    - Add connection status indicator with visual badges
    - Add quick action buttons (View Bills, View Payments)
    - Use responsive grid layout (1 column mobile, 2 columns tablet, 4 columns desktop)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.6, 3.7, 8.1, 8.2, 8.3_
  
  - [x] 7.3 Create templates/client_bills.html
    - Create table of billing records with status badges
    - Add "Pay Now" button for unpaid bills
    - Add status filters (All, Unpaid, Paid, Overdue)
    - Make table mobile-responsive (stacked cards on mobile)
    - _Requirements: 4.1, 4.2, 4.3, 5.1, 8.4, 8.5_
  
  - [x] 7.4 Create templates/client_bill_detail.html
    - Display full billing record details
    - Show charge breakdown
    - Show billing period information
    - Add "Pay Now" button if unpaid
    - _Requirements: 4.5, 5.1_
  
  - [x] 7.5 Create templates/client_payments.html
    - Create table of payment records
    - Add payment method badges
    - Add links to view receipts
    - Make table mobile-responsive
    - Sort by date descending
    - _Requirements: 6.1, 6.2, 6.3, 7.1, 8.4, 8.5_
  
  - [x] 7.6 Create templates/client_payment_detail.html
    - Display payment details
    - Show associated billing record information
    - Add link to receipt if available
    - _Requirements: 6.5, 7.1_

- [x] 8. Create client portal routes
  - [x] 8.1 Create routes/client_portal.py with client blueprint
    - Create client_portal_bp blueprint
    - Implement GET /client/login route (render login page)
    - Implement POST /client/login route (process login)
    - Implement GET /client/logout route (logout and redirect)
    - _Requirements: 1.1, 1.2, 1.3, 1.6_
  
  - [x] 8.2 Add dashboard route
    - Implement GET /client/dashboard route with @require_client_login
    - Fetch dashboard data using ClientDashboardService
    - Render client_dashboard.html template
    - _Requirements: 1.5, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_
  
  - [x] 8.3 Add billing routes
    - Implement GET /client/bills route with @require_client_login
    - Implement GET /client/bills/<id> route with @require_client_login
    - Implement GET /client/bills/<id>/pay route with @require_client_login
    - Add access control checks (client can only view own bills)
    - _Requirements: 1.5, 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.7_
  
  - [x] 8.4 Add payment and receipt routes
    - Implement GET /client/payments route with @require_client_login
    - Implement GET /client/payments/<id> route with @require_client_login
    - Implement GET /client/receipts/<id> route with @require_client_login
    - Add access control checks (client can only view own records)
    - _Requirements: 1.5, 6.1, 6.2, 6.3, 6.4, 6.5, 7.1, 7.2, 7.5_
  
  - [ ]* 8.5 Write property test for unauthenticated access redirect
    - **Property 4: Unauthenticated Access ay Nag-redirect sa Login**
    - **Validates: Requirements 1.5**
  
  - [ ]* 8.6 Write property test for data isolation
    - **Property 24: Data Isolation sa Pagitan ng mga Clients**
    - **Validates: Requirements 4.4, 6.4, 7.5**
  
  - [ ]* 8.7 Write unit tests for client routes
    - Test login flow with valid and invalid credentials
    - Test logout functionality
    - Test dashboard rendering
    - Test billing list and detail views
    - Test payment list and detail views
    - Test access control enforcement
    - _Requirements: 1.2, 1.3, 1.4, 1.5, 1.6, 4.4, 6.4, 7.5_

- [x] 9. Register client portal blueprint in app.py
  - Import client_portal_bp from routes.client_portal
  - Register blueprint with app.register_blueprint(client_portal_bp)
  - Ensure blueprint is registered before app.run()
  - _Requirements: 1.1_

- [x] 10. Checkpoint - Test client portal functionality
  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. Implement session security features
  - [x] 11.1 Configure secure session settings in app.py or config.py
    - Set SESSION_COOKIE_HTTPONLY = True
    - Set SESSION_COOKIE_SECURE = True (for production)
    - Set PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    - Enable CSRF protection
    - _Requirements: 9.1, 9.2, 9.4_
  
  - [x] 11.2 Add session timeout middleware
    - Check last_activity timestamp on each request
    - Expire session if inactive for 30 minutes
    - Redirect to login with expiration message
    - _Requirements: 9.2, 9.5_
  
  - [x] 11.3 Add session ID regeneration on login
    - Regenerate session ID after successful authentication
    - Prevent session fixation attacks
    - _Requirements: 9.3_
  
  - [ ]* 11.4 Write property tests for session security
    - **Property 26: Session Cookie Security Flags**
    - **Validates: Requirements 9.1**
  
  - [ ]* 11.5 Write property test for session timeout
    - **Property 27: Session Timeout Pagkatapos ng Inactivity**
    - **Validates: Requirements 9.2**
  
  - [ ]* 11.6 Write property test for session ID regeneration
    - **Property 28: Session ID Regeneration sa Login**
    - **Validates: Requirements 9.3**
  
  - [ ]* 11.7 Write unit tests for session security
    - Test HttpOnly flag on session cookies
    - Test session timeout after 30 minutes
    - Test CSRF token validation
    - Test session ID regeneration
    - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [x] 12. Implement access control separation
  - [x] 12.1 Add credential separation checks
    - Ensure client credentials don't work on admin login
    - Ensure admin credentials don't work on client login
    - Add tests for credential separation
    - _Requirements: 10.1, 10.3_
  
  - [x] 12.2 Add route access control
    - Prevent clients from accessing admin routes
    - Return 403 Forbidden for unauthorized access attempts
    - Log unauthorized access attempts
    - _Requirements: 10.2, 10.4_
  
  - [x] 12.3 Ensure session isolation
    - Verify client and admin sessions don't interfere
    - Test concurrent client and admin sessions
    - _Requirements: 10.5_
  
  - [ ]* 12.4 Write property tests for access control
    - **Property 31: Authentication Credential Separation**
    - **Validates: Requirements 10.1, 10.3**
  
  - [ ]* 12.5 Write property test for client access to admin routes
    - **Property 32: Client Access Control sa Admin Routes**
    - **Validates: Requirements 10.2, 10.4**
  
  - [ ]* 12.6 Write property test for session type isolation
    - **Property 33: Session Type Isolation**
    - **Validates: Requirements 10.5**
  
  - [ ]* 12.7 Write unit tests for access control
    - Test client cannot access admin routes
    - Test admin cannot use client portal with admin credentials
    - Test session isolation between client and admin
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 13. Add error handling and user feedback
  - [x] 13.1 Add error handling for authentication
    - Handle invalid credentials with user-friendly messages
    - Handle session expiration with redirect and message
    - Handle inactive account errors
    - _Requirements: 1.3, 9.5_
  
  - [x] 13.2 Add error handling for data access
    - Handle unauthorized access attempts (403 Forbidden)
    - Handle resource not found (404)
    - Handle Mikrotik connection errors
    - _Requirements: 4.4, 6.4, 7.5_
  
  - [x] 13.3 Add error handling for payment processing
    - Handle billing record not found
    - Handle already paid bills
    - Handle invalid amounts
    - _Requirements: 5.1, 5.2_
  
  - [ ]* 13.4 Write unit tests for error handling
    - Test authentication error messages
    - Test unauthorized access responses
    - Test payment processing errors
    - _Requirements: 1.3, 4.4, 5.1, 6.4, 7.5, 9.5_

- [x] 14. Final checkpoint - Run all tests and verify functionality
  - Run database migration
  - Run all unit tests
  - Run all property-based tests
  - Verify mobile responsiveness manually
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property-based tests use Hypothesis with 100+ iterations per property
- The implementation builds on existing Flask app structure
- Database migration must be run before testing authentication
- Default passwords for existing clients use PPPoE username as initial password
- GCash integration uses deep linking (no API integration required)
- Session security features are critical and should not be skipped
