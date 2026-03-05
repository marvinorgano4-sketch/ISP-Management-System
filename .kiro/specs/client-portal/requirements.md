# Requirements Document

## Introduction

The Client Portal is a self-service web interface that enables ISP customers to manage their accounts, view billing information, make payments via GCash, and monitor their connection status. This portal provides clients with 24/7 access to their account information without requiring administrator assistance.

## Glossary

- **Client_Portal**: The web-based self-service interface for ISP customers
- **Client**: An ISP customer with an active account in the billing system
- **PPPoE_Username**: The unique account identifier used for client authentication
- **Dashboard**: The main client interface displaying account summary information
- **Billing_Record**: A record of charges for a billing period
- **Payment_Record**: A record of a payment transaction
- **Receipt**: A document confirming payment details
- **GCash_Payment_Link**: A URL that redirects to GCash payment interface with pre-filled amount and reference
- **Connection_Status**: The online/offline state of a client's connection from Mikrotik
- **Mikrotik_Service**: The existing service that queries Mikrotik router for connection status
- **Admin_User**: A system administrator with access to the admin interface
- **Session**: An authenticated client session in the portal
- **Due_Date**: The date when the next payment is required
- **Remaining_Days**: The number of days until the next payment due date

## Requirements

### Requirement 1: Client Authentication

**User Story:** As a client, I want to login using my PPPoE username and password, so that I can access my account information securely.

#### Acceptance Criteria

1. THE Client_Portal SHALL provide a login page separate from the admin login interface
2. WHEN a client submits valid PPPoE_Username and password credentials, THE Client_Portal SHALL create an authenticated Session
3. WHEN a client submits invalid credentials, THE Client_Portal SHALL display an error message and deny access
4. THE Client_Portal SHALL maintain Session state across page requests until logout or timeout
5. WHEN an unauthenticated client attempts to access protected pages, THE Client_Portal SHALL redirect to the login page
6. THE Client_Portal SHALL provide a logout function that terminates the Session

### Requirement 2: Client Password Management

**User Story:** As a system administrator, I want clients to have password credentials stored in the database, so that they can authenticate to the portal.

#### Acceptance Criteria

1. THE Client model SHALL include a password field for authentication
2. THE Client_Portal SHALL hash passwords before storing them in the database
3. WHEN a Client record is created without a password, THE Client_Portal SHALL generate a default password
4. THE Client_Portal SHALL verify passwords using secure comparison methods

### Requirement 3: Account Dashboard Display

**User Story:** As a client, I want to view my account dashboard, so that I can see my current account status at a glance.

#### Acceptance Criteria

1. WHEN a client accesses the dashboard, THE Client_Portal SHALL display the Remaining_Days until next payment
2. WHEN a client accesses the dashboard, THE Client_Portal SHALL display the total unpaid balance from all Billing_Records
3. WHEN a client accesses the dashboard, THE Client_Portal SHALL display the Connection_Status from Mikrotik_Service
4. WHEN a client accesses the dashboard, THE Client_Portal SHALL display the plan name and monthly amount
5. THE Client_Portal SHALL calculate Remaining_Days as the difference between Due_Date and current date
6. WHEN the Connection_Status is online, THE Client_Portal SHALL display a visual indicator showing active connection
7. WHEN the Connection_Status is offline, THE Client_Portal SHALL display a visual indicator showing inactive connection

### Requirement 4: Bill Viewing

**User Story:** As a client, I want to view my billing records, so that I can see what charges I owe.

#### Acceptance Criteria

1. THE Client_Portal SHALL display a list of all Billing_Records for the authenticated Client
2. WHEN displaying Billing_Records, THE Client_Portal SHALL show the billing period, amount, due date, and payment status
3. THE Client_Portal SHALL display unpaid Billing_Records prominently
4. THE Client_Portal SHALL allow clients to view only their own Billing_Records
5. WHEN a client accesses billing details, THE Client_Portal SHALL display the full breakdown of charges

### Requirement 5: GCash Payment Integration

**User Story:** As a client, I want to pay my bills via GCash, so that I can settle my account balance conveniently.

#### Acceptance Criteria

1. WHEN a client views unpaid Billing_Records, THE Client_Portal SHALL display a "Pay Now" button
2. WHEN a client clicks "Pay Now", THE Client_Portal SHALL generate a GCash_Payment_Link with the bill amount and reference number
3. THE GCash_Payment_Link SHALL include the recipient number 09495502589
4. THE GCash_Payment_Link SHALL include the recipient name "Jean Kimberlyn L"
5. THE GCash_Payment_Link SHALL include the payment amount from the Billing_Record
6. THE GCash_Payment_Link SHALL include a unique reference number identifying the Client and Billing_Record
7. WHEN the GCash_Payment_Link is generated, THE Client_Portal SHALL redirect the client to the GCash payment interface

### Requirement 6: Payment History

**User Story:** As a client, I want to view my payment history, so that I can track my past payments.

#### Acceptance Criteria

1. THE Client_Portal SHALL display a list of all Payment_Records for the authenticated Client
2. WHEN displaying Payment_Records, THE Client_Portal SHALL show the payment date, amount, method, and reference number
3. THE Client_Portal SHALL sort Payment_Records by date in descending order
4. THE Client_Portal SHALL allow clients to view only their own Payment_Records
5. WHEN a client accesses payment details, THE Client_Portal SHALL display the associated Billing_Record information

### Requirement 7: Receipt Access

**User Story:** As a client, I want to view and download receipts for my payments, so that I have proof of payment.

#### Acceptance Criteria

1. WHEN a Payment_Record exists, THE Client_Portal SHALL provide a link to view the Receipt
2. WHEN a client views a Receipt, THE Client_Portal SHALL display all payment details including date, amount, method, and reference
3. THE Client_Portal SHALL provide a download option for Receipt documents
4. THE Client_Portal SHALL generate Receipt documents in a printable format
5. THE Client_Portal SHALL allow clients to access only their own Receipt documents

### Requirement 8: Mobile Responsive Design

**User Story:** As a client, I want to access the portal from my mobile device, so that I can manage my account on the go.

#### Acceptance Criteria

1. THE Client_Portal SHALL render correctly on mobile devices with screen widths of 320px and above
2. THE Client_Portal SHALL render correctly on tablet devices with screen widths of 768px and above
3. THE Client_Portal SHALL render correctly on desktop devices with screen widths of 1024px and above
4. WHEN accessed from a mobile device, THE Client_Portal SHALL display navigation elements in a mobile-friendly format
5. WHEN accessed from a mobile device, THE Client_Portal SHALL display tables and data in a readable format without horizontal scrolling

### Requirement 9: Session Security

**User Story:** As a system administrator, I want client sessions to be secure, so that unauthorized users cannot access client accounts.

#### Acceptance Criteria

1. THE Client_Portal SHALL use secure session cookies with HttpOnly flag
2. THE Client_Portal SHALL expire inactive Sessions after 30 minutes
3. THE Client_Portal SHALL prevent Session fixation attacks by regenerating session identifiers after login
4. THE Client_Portal SHALL prevent cross-site request forgery attacks using CSRF tokens
5. WHEN a Session expires, THE Client_Portal SHALL redirect the client to the login page

### Requirement 10: Access Control Separation

**User Story:** As a system administrator, I want client portal access to be separate from admin access, so that clients cannot access administrative functions.

#### Acceptance Criteria

1. THE Client_Portal SHALL authenticate clients using Client credentials, not Admin_User credentials
2. THE Client_Portal SHALL prevent clients from accessing admin routes and functions
3. THE Client_Portal SHALL prevent Admin_Users from accessing the Client_Portal using admin credentials
4. WHEN a client attempts to access admin functions, THE Client_Portal SHALL deny access and return an error
5. THE Client_Portal SHALL maintain separate session management for clients and Admin_Users
