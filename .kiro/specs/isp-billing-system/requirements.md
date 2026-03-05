# Requirements Document: ISP Billing System

## Panimula

Ang ISP Billing System ay isang web-based na aplikasyon para sa pamamahala ng internet service provider operations. Ang sistema ay nag-integrate sa Mikrotik RouterOS para sa real-time monitoring ng mga koneksyon at nag-aalok ng komprehensibong billing at payment management.

## Glossary

- **Sistema**: Ang ISP Billing System web application
- **Admin**: Ang user na may access sa lahat ng features ng sistema
- **Cliente**: Ang subscriber o customer ng ISP
- **Mikrotik**: Ang RouterOS device na nag-manage ng PPPoE connections
- **PPPoE_User**: Ang active na user connection sa Mikrotik router
- **Billing_Record**: Ang record ng bayad na dapat bayaran ng cliente
- **Payment**: Ang record ng bayad na ginawa ng cliente
- **Resibo**: Ang printed o digital receipt ng payment
- **Dashboard**: Ang main interface na nagpapakita ng overview ng sistema

## Requirements

### Requirement 1: User Authentication

**User Story:** Bilang admin, gusto kong mag-login sa sistema gamit ang secure credentials, para ma-access ko ang billing management features.

#### Acceptance Criteria

1. WHEN ang admin ay mag-enter ng valid username at password, THE Sistema SHALL authenticate ang user at mag-redirect sa dashboard
2. WHEN ang admin ay mag-enter ng invalid credentials, THE Sistema SHALL display error message at hindi mag-allow ng access
3. WHEN ang admin ay naka-login na, THE Sistema SHALL maintain ang session hanggang mag-logout
4. WHEN ang admin ay mag-click ng logout button, THE Sistema SHALL clear ang session at mag-redirect sa login page
5. WHEN ang unauthenticated user ay mag-attempt na mag-access ng protected pages, THE Sistema SHALL redirect sa login page

### Requirement 2: Cliente Management

**User Story:** Bilang admin, gusto kong mag-manage ng mga cliente records, para ma-track ko ang lahat ng subscribers at kanilang information.

#### Acceptance Criteria

1. WHEN ang admin ay mag-add ng bagong cliente, THE Sistema SHALL save ang client information (pangalan, address, contact number, plan, PPPoE username)
2. WHEN ang admin ay mag-view ng client list, THE Sistema SHALL display lahat ng clients with their basic information
3. WHEN ang admin ay mag-search ng cliente, THE Sistema SHALL filter ang results based sa search query
4. WHEN ang admin ay mag-edit ng client information, THE Sistema SHALL update ang record at mag-preserve ng data integrity
5. WHEN ang admin ay mag-view ng specific client, THE Sistema SHALL display complete client details including payment history at connection status
6. THE Sistema SHALL validate na ang PPPoE username ay unique para sa bawat cliente

### Requirement 3: Mikrotik Integration

**User Story:** Bilang admin, gusto kong makita ang real-time status ng mga PPPoE connections mula sa Mikrotik, para ma-monitor ko kung sino ang online at offline.

#### Acceptance Criteria

1. WHEN ang sistema ay kumokonekta sa Mikrotik, THE Sistema SHALL use ang configured credentials (host, username, password)
2. WHEN ang admin ay mag-view ng dashboard, THE Sistema SHALL fetch at display ang active PPPoE users mula sa Mikrotik
3. WHEN ang PPPoE_User ay online, THE Sistema SHALL display ang connection details (name, IP address, service, uptime)
4. IF ang Mikrotik connection ay nag-fail, THEN THE Sistema SHALL display error message at mag-continue functioning para sa other features
5. WHEN ang admin ay mag-refresh ng dashboard, THE Sistema SHALL fetch updated data mula sa Mikrotik

### Requirement 4: Billing Management

**User Story:** Bilang admin, gusto kong mag-generate at mag-manage ng monthly bills para sa mga clients, para ma-track ko kung sino ang may utang at sino ang paid na.

#### Acceptance Criteria

1. WHEN ang admin ay mag-generate ng bills para sa buwan, THE Sistema SHALL create Billing_Record para sa lahat ng active clients
2. WHEN ang Billing_Record ay na-create, THE Sistema SHALL include ang client name, amount based sa plan, due date, at status (unpaid)
3. WHEN ang admin ay mag-view ng billing list, THE Sistema SHALL display lahat ng bills with filter options (paid, unpaid, overdue)
4. WHEN ang admin ay mag-search ng bill, THE Sistema SHALL filter results based sa client name o date range
5. THE Sistema SHALL calculate ang total amount due para sa bawat cliente including any outstanding balance

### Requirement 5: Payment Processing

**User Story:** Bilang admin, gusto kong mag-record ng payments mula sa clients, para ma-update ang billing status at ma-generate ang receipt.

#### Acceptance Criteria

1. WHEN ang admin ay mag-record ng payment, THE Sistema SHALL update ang corresponding Billing_Record status to "paid"
2. WHEN ang Payment ay na-record, THE Sistema SHALL save ang payment date, amount, at payment method
3. WHEN ang payment ay successful, THE Sistema SHALL generate Resibo with unique receipt number
4. WHEN ang admin ay mag-view ng payment history, THE Sistema SHALL display lahat ng payments with client name, amount, date, at status
5. THE Sistema SHALL validate na ang payment amount ay hindi less than ang billed amount

### Requirement 6: Receipt Generation

**User Story:** Bilang admin, gusto kong mag-generate at mag-print ng official receipts, para may proof of payment ang clients.

#### Acceptance Criteria

1. WHEN ang payment ay na-record, THE Sistema SHALL generate Resibo with company name "L SECURITY ISP BILLING"
2. WHEN ang Resibo ay na-generate, THE Sistema SHALL include client name, amount paid, date, receipt number, at status
3. WHEN ang admin ay mag-click ng print button, THE Sistema SHALL format ang receipt para sa thermal printer (300px width)
4. WHEN ang receipt ay nag-print, THE Sistema SHALL hide ang print button sa printed output
5. THE Sistema SHALL store ang receipt records para sa future reference

### Requirement 7: Dashboard Overview

**User Story:** Bilang admin, gusto kong makita ang overview ng business operations sa isang dashboard, para ma-monitor ko ang overall status ng ISP.

#### Acceptance Criteria

1. WHEN ang admin ay mag-access ng dashboard, THE Sistema SHALL display summary statistics (total clients, active connections, pending payments, total revenue)
2. WHEN ang dashboard ay nag-load, THE Sistema SHALL display list ng active PPPoE users mula sa Mikrotik
3. WHEN ang dashboard ay nag-display ng clients, THE Sistema SHALL show connection status (online/offline) with uptime
4. WHEN ang admin ay nag-view ng dashboard, THE Sistema SHALL display recent payments at pending bills
5. THE Sistema SHALL auto-refresh ang Mikrotik connection data every time na mag-reload ang page

### Requirement 8: Payment History Tracking

**User Story:** Bilang admin, gusto kong makita ang complete payment history ng bawat cliente, para ma-track ko ang payment behavior at outstanding balances.

#### Acceptance Criteria

1. WHEN ang admin ay mag-view ng client details, THE Sistema SHALL display complete payment history with dates at amounts
2. WHEN ang admin ay mag-filter ng payment history, THE Sistema SHALL allow filtering by date range at payment status
3. WHEN ang payment history ay nag-display, THE Sistema SHALL show receipt numbers para sa bawat payment
4. WHEN ang admin ay mag-click ng receipt number, THE Sistema SHALL display o mag-download ng receipt copy
5. THE Sistema SHALL calculate at display ang total amount paid ng cliente over time

### Requirement 9: Data Validation at Security

**User Story:** Bilang admin, gusto kong secure ang sistema at validated ang lahat ng inputs, para ma-prevent ang data corruption at unauthorized access.

#### Acceptance Criteria

1. WHEN ang user ay mag-input ng data, THE Sistema SHALL validate ang format at required fields
2. WHEN ang invalid data ay na-submit, THE Sistema SHALL display specific error messages
3. WHEN ang sistema ay nag-store ng sensitive data, THE Sistema SHALL encrypt ang passwords
4. WHEN ang admin session ay nag-expire, THE Sistema SHALL require re-authentication
5. THE Sistema SHALL prevent SQL injection at XSS attacks sa lahat ng input fields

### Requirement 10: Responsive User Interface

**User Story:** Bilang admin, gusto kong gumamit ng sistema sa different devices, para ma-access ko ang billing system kahit naka-mobile o tablet.

#### Acceptance Criteria

1. WHEN ang sistema ay na-access sa mobile device, THE Sistema SHALL display responsive layout
2. WHEN ang screen size ay nag-change, THE Sistema SHALL adjust ang UI elements accordingly
3. WHEN ang admin ay nag-navigate, THE Sistema SHALL provide clear navigation menu
4. WHEN ang forms ay nag-display, THE Sistema SHALL be usable sa touch screens
5. THE Sistema SHALL maintain readability at usability across different screen sizes
