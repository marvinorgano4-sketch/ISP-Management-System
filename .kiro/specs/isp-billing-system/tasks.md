# Implementation Plan: ISP Billing System

## Overview

Ang implementation plan ay mag-build sa existing Flask app na may Mikrotik integration. Mag-start tayo sa database setup at models, then authentication, client management, billing, payments, at receipts. Bawat major component ay may corresponding property-based tests para sa correctness validation.

## Tasks

- [x] 1. Setup project structure at dependencies
  - Install required packages: Flask-SQLAlchemy, Flask-Login, Flask-WTF, Flask-Migrate, hypothesis, pytest, pytest-flask, bcrypt
  - Create directory structure: models/, services/, routes/, templates/, static/, tests/
  - Setup configuration file para sa database at Mikrotik credentials
  - Initialize Flask extensions (SQLAlchemy, Login Manager, CSRF protection)
  - _Requirements: 9.3, 9.5_

- [ ] 2. Implement database models
  - [x] 2.1 Create User model with password hashing
    - Define User model with id, username, password_hash, full_name, timestamps
    - Implement password hashing methods using bcrypt
    - _Requirements: 1.1, 9.3_
  
  - [ ]* 2.2 Write property test for password encryption
    - **Property 27: Password encryption**
    - **Validates: Requirements 9.3**
  
  - [x] 2.3 Create Client model
    - Define Client model with all fields (name, address, contact, email, pppoe_username, plan_name, plan_amount, status)
    - Add unique constraint on pppoe_username
    - _Requirements: 2.1, 2.6_
  
  - [ ]* 2.4 Write property test for PPPoE username uniqueness
    - **Property 10: PPPoE username uniqueness**
    - **Validates: Requirements 2.6**
  
  - [x] 2.5 Create Billing model
    - Define Billing model with client relationship, amount, billing period, due date, status
    - Add foreign key to Client and Payment
    - _Requirements: 4.1, 4.2_
  
  - [x] 2.6 Create Payment model
    - Define Payment model with billing and client relationships, amount, date, method, reference number
    - Add foreign key to Billing, Client, and Receipt
    - _Requirements: 5.1, 5.2_
  
  - [x] 2.7 Create Receipt model
    - Define Receipt model with payment relationship, receipt number, client name, amount, date, status
    - Add unique constraint on receipt_number
    - _Requirements: 6.1, 6.2_
  
  - [x] 2.8 Setup database migrations
    - Initialize Flask-Migrate
    - Create initial migration with all models
    - Create seed data script for admin user
    - _Requirements: 1.1_

- [ ] 3. Implement authentication system
  - [x] 3.1 Create AuthService class
    - Implement authenticate_user method with password verification
    - Implement create_session and destroy_session methods
    - Implement require_login decorator
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  
  - [ ]* 3.2 Write property tests for authentication
    - **Property 1: Valid credentials authenticate successfully**
    - **Property 2: Invalid credentials are rejected**
    - **Validates: Requirements 1.1, 1.2**
  
  - [x] 3.3 Create authentication routes
    - Implement GET /login route with login form
    - Implement POST /login route with credential validation
    - Implement GET /logout route with session clearing
    - _Requirements: 1.1, 1.2, 1.4_
  
  - [ ]* 3.4 Write property test for session persistence
    - **Property 3: Session persistence after login**
    - **Validates: Requirements 1.3**
  
  - [ ]* 3.5 Write property test for protected routes
    - **Property 5: Protected routes require authentication**
    - **Validates: Requirements 1.5**
  
  - [x] 3.6 Create login template
    - Design login form with username and password fields
    - Add CSRF token protection
    - Style with Tailwind CSS
    - _Requirements: 1.1, 1.2_

- [x] 4. Checkpoint - Ensure authentication works
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implement Mikrotik integration service
  - [x] 5.1 Create MikrotikService class
    - Implement connection management with configured credentials
    - Implement get_active_pppoe_users method
    - Implement get_user_by_name and is_user_online methods
    - Add error handling for connection failures
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  
  - [ ]* 5.2 Write property test for Mikrotik connection
    - **Property 11: Mikrotik connection uses configured credentials**
    - **Validates: Requirements 3.1**
  
  - [ ]* 5.3 Write property test for connection error handling
    - **Property 14: Mikrotik connection failure is handled gracefully**
    - **Validates: Requirements 3.4**
  
  - [ ]* 5.4 Write unit tests for Mikrotik service
    - Mock Mikrotik API responses
    - Test successful connection and data retrieval
    - Test connection timeout and authentication failure
    - _Requirements: 3.1, 3.2, 3.4_

- [ ] 6. Implement client management
  - [x] 6.1 Create ClientService class
    - Implement create_client with validation
    - Implement get_client, get_all_clients, update_client methods
    - Implement search_clients with query filtering
    - Implement validate_pppoe_username for uniqueness check
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.6_
  
  - [ ]* 6.2 Write property test for client creation
    - **Property 6: Client creation persists data**
    - **Validates: Requirements 2.1**
  
  - [ ]* 6.3 Write property test for client retrieval
    - **Property 7: Client retrieval returns complete data**
    - **Validates: Requirements 2.2, 2.5**
  
  - [ ]* 6.4 Write property test for search functionality
    - **Property 8: Search filters results correctly**
    - **Validates: Requirements 2.3**
  
  - [x] 6.5 Create client management routes
    - Implement GET /clients (list with search/filter)
    - Implement GET /clients/new (add form)
    - Implement POST /clients (create)
    - Implement GET /clients/<id> (view details)
    - Implement GET /clients/<id>/edit (edit form)
    - Implement POST /clients/<id> (update)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [x] 6.6 Create client templates
    - Create client list template with search bar and table
    - Create client form template (for add/edit)
    - Create client detail template with payment history
    - Style with Tailwind CSS
    - _Requirements: 2.2, 2.3, 2.5_

- [ ] 7. Implement billing management
  - [x] 7.1 Create BillingService class
    - Implement generate_monthly_bills method
    - Implement get_billing, get_client_bills, get_all_bills methods
    - Implement calculate_total_due method
    - Implement mark_as_paid method
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [ ]* 7.2 Write property test for bill generation
    - **Property 16: Monthly bill generation creates bills for all active clients**
    - **Validates: Requirements 4.1**
  
  - [ ]* 7.3 Write property test for billing record fields
    - **Property 17: Billing records contain required fields**
    - **Validates: Requirements 4.2**
  
  - [ ]* 7.4 Write property test for total due calculation
    - **Property 18: Total amount due calculation**
    - **Validates: Requirements 4.5**
  
  - [x] 7.5 Create billing routes
    - Implement GET /billing (list with filters)
    - Implement GET /billing/generate (generate form)
    - Implement POST /billing/generate (create bills)
    - Implement GET /billing/<id> (view details)
    - _Requirements: 4.1, 4.3, 4.4_
  
  - [x] 7.6 Create billing templates
    - Create billing list template with filters (paid, unpaid, overdue)
    - Create generate bills form template
    - Create billing detail template
    - Style with Tailwind CSS
    - _Requirements: 4.3_

- [x] 8. Checkpoint - Ensure billing system works
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Implement payment processing
  - [x] 9.1 Create PaymentService class
    - Implement record_payment method with billing status update
    - Implement get_payment, get_client_payments, get_all_payments methods
    - Implement calculate_total_paid method
    - Implement validate_payment_amount method
    - _Requirements: 5.1, 5.2, 5.4, 5.5_
  
  - [ ]* 9.2 Write property test for payment recording
    - **Property 19: Payment recording updates billing status**
    - **Validates: Requirements 5.1**
  
  - [ ]* 9.3 Write property test for payment validation
    - **Property 21: Payment amount validation**
    - **Validates: Requirements 5.5**
  
  - [ ]* 9.4 Write property test for payment history
    - **Property 22: Payment history completeness**
    - **Validates: Requirements 5.4, 8.1**
  
  - [x] 9.5 Create payment routes
    - Implement GET /payments (list with filters)
    - Implement GET /payments/new (payment form with billing_id)
    - Implement POST /payments (record payment)
    - Implement GET /payments/<id> (view details)
    - _Requirements: 5.1, 5.2, 5.4_
  
  - [x] 9.6 Create payment templates
    - Create payment list template with filters
    - Create payment form template
    - Create payment detail template
    - Style with Tailwind CSS
    - _Requirements: 5.4_

- [ ] 10. Implement receipt generation
  - [x] 10.1 Create ReceiptService class
    - Implement generate_receipt method with unique receipt number
    - Implement get_receipt, get_receipt_by_number methods
    - Implement format_for_print method
    - Implement generate_receipt_number method (format: LSEC-YYYYMMDD-XXXX)
    - _Requirements: 5.3, 6.1, 6.2, 6.5_
  
  - [ ]* 10.2 Write property test for receipt generation
    - **Property 23: Receipt generation from payment**
    - **Validates: Requirements 5.3, 6.1, 6.2**
  
  - [ ]* 10.3 Write property test for receipt persistence
    - **Property 24: Receipt persistence and retrieval**
    - **Validates: Requirements 6.5, 8.4**
  
  - [x] 10.4 Create receipt routes
    - Implement GET /receipts/<id> (view/print receipt)
    - Implement GET /receipts/<id>/download (download as PDF - optional)
    - _Requirements: 6.3, 8.4_
  
  - [x] 10.5 Update receipt template
    - Enhance existing receipt.html with dynamic data
    - Add company name "L SECURITY ISP BILLING"
    - Format for thermal printer (300px width)
    - Add print button with CSS media query to hide on print
    - Style with inline CSS for print compatibility
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [ ] 11. Implement dashboard
  - [x] 11.1 Create DashboardService class
    - Implement get_statistics method (total clients, active connections, pending payments, revenue)
    - Implement get_active_connections method (integrate with MikrotikService)
    - Implement get_recent_payments method
    - Implement get_pending_bills method
    - _Requirements: 7.1, 7.2, 7.3, 7.4_
  
  - [ ]* 11.2 Write property test for dashboard statistics
    - **Property 25: Dashboard statistics completeness**
    - **Validates: Requirements 7.1, 7.4**
  
  - [ ]* 11.3 Write property test for Mikrotik data display
    - **Property 12: Dashboard displays Mikrotik active users**
    - **Property 13: Online users show complete connection details**
    - **Validates: Requirements 3.2, 3.3, 7.2, 7.3**
  
  - [x] 11.4 Update dashboard route
    - Enhance existing / route to use DashboardService
    - Add statistics, recent payments, pending bills
    - Keep existing Mikrotik active users display
    - _Requirements: 7.1, 7.2, 7.4_
  
  - [x] 11.5 Update dashboard template
    - Enhance existing dashboard.html with complete layout
    - Add statistics cards at top
    - Add recent payments section
    - Add pending bills section
    - Keep existing active users table
    - Add navigation menu
    - Style with Tailwind CSS
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 12. Implement data validation and security
  - [x] 12.1 Create form validation classes
    - Create LoginForm with username and password validators
    - Create ClientForm with all field validators
    - Create BillingForm with month/year validators
    - Create PaymentForm with amount validator
    - Add CSRF protection to all forms
    - _Requirements: 9.1, 9.2, 9.5_
  
  - [ ]* 12.2 Write property test for input validation
    - **Property 26: Input validation on all forms**
    - **Validates: Requirements 9.1, 9.2**
  
  - [x] 12.3 Implement session expiration
    - Configure session timeout (e.g., 30 minutes)
    - Add session expiration check in require_login decorator
    - _Requirements: 9.4_
  
  - [ ]* 12.4 Write property test for session expiration
    - **Property 28: Session expiration requires re-authentication**
    - **Validates: Requirements 9.4**
  
  - [ ]* 12.5 Write unit tests for security features
    - Test CSRF protection on forms
    - Test SQL injection prevention (parameterized queries)
    - Test XSS prevention (template escaping)
    - _Requirements: 9.5_

- [ ] 13. Implement responsive UI enhancements
  - [x] 13.1 Create base template with navigation
    - Create base.html with responsive navigation menu
    - Add mobile menu toggle
    - Include Tailwind CSS CDN
    - Add flash message display
    - _Requirements: 10.1, 10.2_
  
  - [x] 13.2 Make all templates responsive
    - Update all templates to extend base.html
    - Add responsive classes for mobile, tablet, desktop
    - Test forms on touch screens (appropriate input sizes)
    - _Requirements: 10.1, 10.2, 10.4_

- [ ] 14. Integration and wiring
  - [x] 14.1 Wire all routes to services
    - Connect authentication routes to AuthService
    - Connect client routes to ClientService
    - Connect billing routes to BillingService
    - Connect payment routes to PaymentService and ReceiptService
    - Connect dashboard route to DashboardService and MikrotikService
    - _Requirements: All_
  
  - [x] 14.2 Add error handling middleware
    - Implement error handlers for 404, 403, 500
    - Add logging for errors and important events
    - Create error templates
    - _Requirements: 3.4, 9.1_
  
  - [x] 14.3 Setup configuration management
    - Move Mikrotik credentials to environment variables
    - Add Flask secret key configuration
    - Add database URL configuration
    - Create .env.example file
    - _Requirements: 3.1, 9.3_
  
  - [ ]* 14.4 Write integration tests
    - Test complete billing cycle (generate → pay → receipt)
    - Test client lifecycle (create → bill → pay → history)
    - Test authentication flow (login → access → logout)
    - _Requirements: All_

- [x] 15. Final checkpoint - Ensure all tests pass
  - Run all unit tests and property tests
  - Check code coverage
  - Test manually on different devices (desktop, mobile, tablet)
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Existing code (app.py, templates) will be enhanced and integrated
- Property tests use hypothesis library with minimum 100 iterations
- Each property test references specific design document property
- Mikrotik credentials: Host 10.114.215.133, user 'admin', password 'adminTaboo'
- Company name for receipts: "L SECURITY ISP BILLING"
- Receipt format: 300px width for thermal printer
- All templates use Tailwind CSS for styling
- Database: SQLite with SQLAlchemy ORM
- Authentication: Flask-Login with session management
