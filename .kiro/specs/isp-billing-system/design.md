# Design Document: ISP Billing System

## Overview

Ang ISP Billing System ay isang Flask-based web application na nag-integrate sa Mikrotik RouterOS para sa real-time PPPoE monitoring at comprehensive billing management. Ang sistema ay gumagamit ng SQLite database para sa data persistence, session-based authentication, at responsive UI gamit ang Tailwind CSS.

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Web Browser                          │
│              (Admin Interface)                          │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/HTTPS
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Flask Application                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Routes Layer                                     │  │
│  │  - Auth routes (/login, /logout)                 │  │
│  │  - Dashboard routes (/)                          │  │
│  │  - Client routes (/clients/*)                    │  │
│  │  - Billing routes (/billing/*)                   │  │
│  │  - Payment routes (/payments/*)                  │  │
│  │  - Receipt routes (/receipts/*)                  │  │
│  └──────────────────┬───────────────────────────────┘  │
│                     ▼                                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Business Logic Layer                            │  │
│  │  - AuthService                                   │  │
│  │  - ClientService                                 │  │
│  │  - BillingService                                │  │
│  │  - PaymentService                                │  │
│  │  - MikrotikService                               │  │
│  └──────────────────┬───────────────────────────────┘  │
│                     ▼                                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Data Access Layer                               │  │
│  │  - Database models (SQLAlchemy)                  │  │
│  │  - CRUD operations                               │  │
│  └──────────────────┬───────────────────────────────┘  │
└────────────────────┼────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌──────────────────┐    ┌──────────────────┐
│  SQLite Database │    │  Mikrotik Router │
│  - Users         │    │  RouterOS API    │
│  - Clients       │    │  PPPoE Active    │
│  - Billings      │    │  Users           │
│  - Payments      │    └──────────────────┘
│  - Receipts      │
└──────────────────┘
```

### Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login with session management
- **Mikrotik Integration**: routeros_api library
- **Frontend**: Jinja2 templates with Tailwind CSS
- **Forms**: Flask-WTF with CSRF protection

## Components and Interfaces

### 1. Authentication Module

**AuthService**
```python
class AuthService:
    def authenticate_user(username: str, password: str) -> User | None
    def create_session(user: User) -> None
    def destroy_session() -> None
    def require_login(func) -> decorator
    def hash_password(password: str) -> str
    def verify_password(password: str, hashed: str) -> bool
```

**Routes**
- `GET /login` - Display login form
- `POST /login` - Process login credentials
- `GET /logout` - Destroy session and redirect

### 2. Client Management Module

**ClientService**
```python
class ClientService:
    def create_client(data: dict) -> Client
    def get_client(client_id: int) -> Client | None
    def get_all_clients(filters: dict = None) -> list[Client]
    def update_client(client_id: int, data: dict) -> Client
    def search_clients(query: str) -> list[Client]
    def validate_pppoe_username(username: str) -> bool
```

**Routes**
- `GET /clients` - List all clients with search/filter
- `GET /clients/new` - Display add client form
- `POST /clients` - Create new client
- `GET /clients/<id>` - View client details
- `GET /clients/<id>/edit` - Display edit form
- `POST /clients/<id>` - Update client
- `DELETE /clients/<id>` - Delete client (soft delete)

### 3. Mikrotik Integration Module

**MikrotikService**
```python
class MikrotikService:
    def __init__(host: str, username: str, password: str)
    def connect() -> RouterOsApiPool
    def disconnect() -> None
    def get_active_pppoe_users() -> list[dict]
    def get_user_by_name(username: str) -> dict | None
    def is_user_online(username: str) -> bool
```

**Data Structure**
```python
PPPoEUser = {
    'name': str,           # PPPoE username
    'address': str,        # Assigned IP address
    'service': str,        # Service name
    'uptime': str,         # Connection uptime
    'caller_id': str       # MAC address
}
```

### 4. Billing Management Module

**BillingService**
```python
class BillingService:
    def generate_monthly_bills(month: int, year: int) -> list[Billing]
    def get_billing(billing_id: int) -> Billing | None
    def get_client_bills(client_id: int, filters: dict = None) -> list[Billing]
    def get_all_bills(filters: dict = None) -> list[Billing]
    def calculate_total_due(client_id: int) -> float
    def mark_as_paid(billing_id: int, payment_id: int) -> Billing
```

**Routes**
- `GET /billing` - List all bills with filters
- `GET /billing/generate` - Display generate bills form
- `POST /billing/generate` - Generate monthly bills
- `GET /billing/<id>` - View billing details

### 5. Payment Processing Module

**PaymentService**
```python
class PaymentService:
    def record_payment(billing_id: int, data: dict) -> Payment
    def get_payment(payment_id: int) -> Payment | None
    def get_client_payments(client_id: int) -> list[Payment]
    def get_all_payments(filters: dict = None) -> list[Payment]
    def calculate_total_paid(client_id: int) -> float
    def validate_payment_amount(billing_id: int, amount: float) -> bool
```

**Routes**
- `GET /payments` - List all payments with filters
- `GET /payments/new?billing_id=<id>` - Display payment form
- `POST /payments` - Record new payment
- `GET /payments/<id>` - View payment details

### 6. Receipt Generation Module

**ReceiptService**
```python
class ReceiptService:
    def generate_receipt(payment_id: int) -> Receipt
    def get_receipt(receipt_id: int) -> Receipt | None
    def get_receipt_by_number(receipt_number: str) -> Receipt | None
    def format_for_print(receipt: Receipt) -> str
    def generate_receipt_number() -> str
```

**Routes**
- `GET /receipts/<id>` - View receipt (printable format)
- `GET /receipts/<id>/download` - Download receipt as PDF

### 7. Dashboard Module

**DashboardService**
```python
class DashboardService:
    def get_statistics() -> dict
    def get_active_connections() -> list[dict]
    def get_recent_payments(limit: int = 10) -> list[Payment]
    def get_pending_bills(limit: int = 10) -> list[Billing]
```

**Statistics Structure**
```python
Statistics = {
    'total_clients': int,
    'active_connections': int,
    'pending_payments': int,
    'total_revenue_month': float,
    'total_revenue_all': float,
    'overdue_bills': int
}
```

**Routes**
- `GET /` - Dashboard with overview and statistics

## Data Models

### User Model
```python
class User:
    id: int (primary key)
    username: str (unique, not null)
    password_hash: str (not null)
    full_name: str
    created_at: datetime
    last_login: datetime
```

### Client Model
```python
class Client:
    id: int (primary key)
    full_name: str (not null)
    address: str
    contact_number: str
    email: str
    pppoe_username: str (unique, not null)
    plan_name: str (not null)
    plan_amount: float (not null)
    status: str (active, inactive, suspended)
    created_at: datetime
    updated_at: datetime
```

### Billing Model
```python
class Billing:
    id: int (primary key)
    client_id: int (foreign key -> Client)
    amount: float (not null)
    billing_month: int (1-12)
    billing_year: int
    due_date: date
    status: str (unpaid, paid, overdue)
    created_at: datetime
    paid_at: datetime (nullable)
    payment_id: int (foreign key -> Payment, nullable)
```

### Payment Model
```python
class Payment:
    id: int (primary key)
    billing_id: int (foreign key -> Billing)
    client_id: int (foreign key -> Client)
    amount: float (not null)
    payment_date: date (not null)
    payment_method: str (cash, gcash, bank_transfer)
    reference_number: str (nullable)
    notes: str (nullable)
    created_at: datetime
    receipt_id: int (foreign key -> Receipt, nullable)
```

### Receipt Model
```python
class Receipt:
    id: int (primary key)
    payment_id: int (foreign key -> Payment)
    receipt_number: str (unique, not null)
    client_name: str (not null)
    amount: float (not null)
    payment_date: date (not null)
    status: str (paid, void)
    created_at: datetime
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Authentication Properties

Property 1: Valid credentials authenticate successfully
*For any* valid username and password combination, authentication should succeed and create an active session that redirects to the dashboard.
**Validates: Requirements 1.1**

Property 2: Invalid credentials are rejected
*For any* invalid username or password, authentication should fail and display an error message without granting access.
**Validates: Requirements 1.2**

Property 3: Session persistence after login
*For any* authenticated session, subsequent requests to protected routes should maintain authentication state until explicit logout.
**Validates: Requirements 1.3**

Property 4: Logout clears session
*For any* authenticated session, calling logout should clear the session and redirect to the login page.
**Validates: Requirements 1.4**

Property 5: Protected routes require authentication
*For any* protected route, unauthenticated access attempts should redirect to the login page.
**Validates: Requirements 1.5**

### Client Management Properties

Property 6: Client creation persists data
*For any* valid client data (name, address, contact, PPPoE username, plan), creating a client should save all fields correctly and return the created client.
**Validates: Requirements 2.1**

Property 7: Client retrieval returns complete data
*For any* client in the database, retrieving the client (by ID or in a list) should return all stored fields including payment history and connection status.
**Validates: Requirements 2.2, 2.5**

Property 8: Search filters results correctly
*For any* search query on clients, bills, or payments, the returned results should only include records that match the search criteria.
**Validates: Requirements 2.3, 4.3, 4.4, 8.2**

Property 9: Client updates preserve data integrity
*For any* client and valid update data, updating the client should persist the changes while maintaining referential integrity with related billings and payments.
**Validates: Requirements 2.4**

Property 10: PPPoE username uniqueness
*For any* two clients, their PPPoE usernames must be different, and attempting to create or update a client with a duplicate PPPoE username should be rejected.
**Validates: Requirements 2.6**

### Mikrotik Integration Properties

Property 11: Mikrotik connection uses configured credentials
*For any* connection attempt to Mikrotik, the system should use the configured host, username, and password values.
**Validates: Requirements 3.1**

Property 12: Dashboard displays Mikrotik active users
*For any* dashboard load, the displayed active PPPoE users should match the current active users returned by the Mikrotik API.
**Validates: Requirements 3.2, 7.2**

Property 13: Online users show complete connection details
*For any* online PPPoE user, the displayed information should include name, IP address, service, and uptime.
**Validates: Requirements 3.3, 7.3**

Property 14: Mikrotik connection failure is handled gracefully
*For any* Mikrotik connection failure, the system should display an error message and continue functioning for non-Mikrotik features.
**Validates: Requirements 3.4**

Property 15: Dashboard refresh fetches current data
*For any* dashboard page reload, the system should query Mikrotik again for the current state of active users.
**Validates: Requirements 3.5, 7.5**

### Billing Management Properties

Property 16: Monthly bill generation creates bills for all active clients
*For any* month, year, and set of active clients, generating bills should create a billing record for each active client.
**Validates: Requirements 4.1**

Property 17: Billing records contain required fields
*For any* generated billing record, it should include client name, amount (based on plan), due date, and status (unpaid).
**Validates: Requirements 4.2**

Property 18: Total amount due calculation
*For any* client with multiple billing records, the total amount due should equal the sum of all unpaid billing amounts.
**Validates: Requirements 4.5, 8.5**

### Payment Processing Properties

Property 19: Payment recording updates billing status
*For any* payment recorded against a billing record, the billing status should be updated to "paid" and linked to the payment.
**Validates: Requirements 5.1**

Property 20: Payment records contain required fields
*For any* recorded payment, it should include payment date, amount, payment method, and reference to the billing record.
**Validates: Requirements 5.2**

Property 21: Payment amount validation
*For any* payment attempt, if the payment amount is less than the billed amount, the payment should be rejected with a validation error.
**Validates: Requirements 5.5**

Property 22: Payment history completeness
*For any* client, viewing their payment history should display all payments with dates, amounts, and receipt numbers.
**Validates: Requirements 5.4, 8.1, 8.3**

### Receipt Generation Properties

Property 23: Receipt generation from payment
*For any* successful payment, a receipt should be generated with a unique receipt number, company name "L SECURITY ISP BILLING", client name, amount paid, date, and status.
**Validates: Requirements 5.3, 6.1, 6.2**

Property 24: Receipt persistence and retrieval
*For any* generated receipt, it should be stored in the database and retrievable by receipt ID or receipt number.
**Validates: Requirements 6.5, 8.4**

### Dashboard Properties

Property 25: Dashboard statistics completeness
*For any* dashboard load, the displayed statistics should include total clients, active connections, pending payments, total revenue (monthly and all-time), and overdue bills.
**Validates: Requirements 7.1, 7.4**

### Data Validation and Security Properties

Property 26: Input validation on all forms
*For any* form submission with invalid data (missing required fields or incorrect format), the system should reject the submission and display specific error messages.
**Validates: Requirements 9.1, 9.2**

Property 27: Password encryption
*For any* user password stored in the database, it should be hashed (not plaintext) using a secure hashing algorithm.
**Validates: Requirements 9.3**

Property 28: Session expiration requires re-authentication
*For any* expired session, attempting to access protected routes should redirect to the login page and require re-authentication.
**Validates: Requirements 9.4**

## Error Handling

### Mikrotik Connection Errors
- **Connection Timeout**: Display user-friendly error message, log technical details, continue serving other features
- **Authentication Failure**: Alert admin about incorrect credentials, provide configuration check guidance
- **API Errors**: Catch and log specific RouterOS API errors, display generic error to user

### Database Errors
- **Connection Errors**: Implement connection pooling with retry logic, display maintenance message if persistent
- **Constraint Violations**: Catch unique constraint violations (e.g., duplicate PPPoE username), display specific error message
- **Transaction Failures**: Rollback transactions on error, log details for debugging

### Validation Errors
- **Form Validation**: Display field-specific error messages inline with forms
- **Business Logic Validation**: Return clear error messages (e.g., "Payment amount cannot be less than billed amount")
- **Data Type Errors**: Validate data types before database operations, return user-friendly messages

### Session and Authentication Errors
- **Session Expiration**: Redirect to login with message "Your session has expired. Please login again."
- **Unauthorized Access**: Redirect to login for unauthenticated users, show 403 for authenticated but unauthorized
- **CSRF Token Errors**: Display error message and refresh form with new token

### Payment and Billing Errors
- **Duplicate Payment**: Prevent duplicate payments for same billing record, show warning if attempted
- **Invalid Billing Period**: Validate month (1-12) and year before generating bills
- **Missing Client Data**: Validate client exists before creating billing or payment records

## Testing Strategy

### Dual Testing Approach

The system will use both unit tests and property-based tests for comprehensive coverage:

**Unit Tests** focus on:
- Specific examples of correct behavior (e.g., login with specific credentials)
- Edge cases (e.g., empty form submissions, boundary values)
- Error conditions (e.g., database connection failures, Mikrotik timeouts)
- Integration points between components

**Property-Based Tests** focus on:
- Universal properties that hold for all inputs (e.g., all valid clients can be created)
- Comprehensive input coverage through randomization
- Invariants that must always hold (e.g., PPPoE username uniqueness)

### Property-Based Testing Configuration

**Library**: Use `hypothesis` for Python property-based testing

**Configuration**:
- Minimum 100 iterations per property test
- Each test must reference its design document property
- Tag format: `# Feature: isp-billing-system, Property {number}: {property_text}`

**Example Property Test Structure**:
```python
from hypothesis import given, strategies as st

# Feature: isp-billing-system, Property 10: PPPoE username uniqueness
@given(
    client1=st.builds(Client, pppoe_username=st.text(min_size=1)),
    client2=st.builds(Client, pppoe_username=st.text(min_size=1))
)
def test_pppoe_username_uniqueness(client1, client2):
    # Create first client
    created1 = client_service.create_client(client1)
    
    # Attempt to create second client with same PPPoE username
    client2.pppoe_username = created1.pppoe_username
    
    # Should raise validation error
    with pytest.raises(ValidationError):
        client_service.create_client(client2)
```

### Unit Testing Strategy

**Test Coverage Areas**:
1. **Authentication**: Login success/failure, logout, session management
2. **Client CRUD**: Create, read, update, delete operations with specific examples
3. **Mikrotik Integration**: Mock Mikrotik API responses, test error handling
4. **Billing Generation**: Test specific month/year combinations, edge cases
5. **Payment Processing**: Test payment recording, validation, receipt generation
6. **Dashboard**: Test statistics calculation with known data sets

**Testing Tools**:
- `pytest` for test framework
- `pytest-flask` for Flask application testing
- `unittest.mock` for mocking external dependencies (Mikrotik API)
- `hypothesis` for property-based testing
- `coverage.py` for code coverage reporting

### Integration Testing

**Test Scenarios**:
1. Complete billing cycle: Generate bills → Record payment → Generate receipt
2. Client lifecycle: Create client → Generate bills → Record payments → View history
3. Dashboard data flow: Fetch Mikrotik data → Display statistics → Show recent activity
4. Authentication flow: Login → Access protected routes → Logout → Verify access denied

### Test Data Management

**Fixtures**:
- Sample users with hashed passwords
- Sample clients with various plans and statuses
- Sample billing records (paid, unpaid, overdue)
- Sample payments with receipts
- Mock Mikrotik API responses

**Database**:
- Use in-memory SQLite for fast test execution
- Reset database between tests for isolation
- Seed test data using fixtures

## Implementation Notes

### Security Considerations
- Use Flask-Login for session management
- Implement CSRF protection with Flask-WTF
- Hash passwords with bcrypt or werkzeug.security
- Validate and sanitize all user inputs
- Use parameterized queries (SQLAlchemy ORM) to prevent SQL injection
- Implement rate limiting for login attempts

### Performance Considerations
- Cache Mikrotik connection for dashboard (with TTL)
- Index database columns used in searches (client name, PPPoE username)
- Paginate large result sets (client list, billing list, payment history)
- Use lazy loading for related objects in SQLAlchemy

### Deployment Considerations
- Use environment variables for sensitive configuration (Mikrotik credentials, secret key)
- Implement database migrations with Flask-Migrate
- Set up logging for production (errors, authentication attempts, payment records)
- Configure HTTPS for production deployment
- Set up backup strategy for SQLite database

### Future Enhancements
- SMS notifications for due dates and payment confirmations
- Email receipt delivery
- Multiple user roles (admin, staff, viewer)
- Client self-service portal
- Automated billing generation (scheduled task)
- Payment gateway integration (GCash, PayMaya)
- Reporting and analytics dashboard
- Audit trail for all transactions
