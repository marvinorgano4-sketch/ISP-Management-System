# Dokumento ng Disenyo: Client Portal

## Pangkalahatang-ideya (Overview)

Ang Client Portal ay isang self-service web interface na nagbibigay-daan sa mga customer ng ISP na pamahalaan ang kanilang mga account nang walang tulong ng administrator. Ang portal ay nagbibigay ng authenticated access sa impormasyon ng account, billing records, payment processing gamit ang GCash, at real-time na connection status monitoring.

### Mga Pangunahing Desisyon sa Disenyo

1. **Hiwalay na Authentication System**: Ang client authentication ay gumagamit ng PPPoE credentials na naka-store sa Client model, ganap na hiwalay sa admin User authentication. Ito ay nagsisiguro ng tamang access control separation at pumipigil sa privilege escalation.

2. **Session-Based Authentication**: Ang Flask sessions na may secure cookies ay nagbibigay ng stateful authentication. Ang approach na ito ay sumasama nang maayos sa existing Flask-Login infrastructure habang pinapanatili ang paghihiwalay ng client at admin sessions.

3. **GCash Deep Linking**: Ang payment integration ay gumagamit ng GCash URL scheme para i-pre-fill ang payment details, nagbibigay ng seamless mobile payment experience nang hindi nangangailangan ng API integration o merchant accounts.

4. **Read-Only Client Access**: Ang mga client ay maaaring tingnan ang kanilang data pero hindi maaaring baguhin ang account details, billing records, o payment records. Lahat ng modifications ay nananatiling admin-only operations.

5. **Responsive-First Design**: Ang mobile-first CSS approach gamit ang Bootstrap ay nagsisiguro ng optimal experience sa lahat ng device sizes, kritikal para sa mga client na nag-access ng portal mula sa smartphones.

## Arkitektura (Architecture)

### Mga Bahagi ng Sistema (System Components)

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Portal Layer                      │
├─────────────────────────────────────────────────────────────┤
│  Client Auth Routes  │  Client Dashboard  │  Client Views   │
│  - Login/Logout      │  - Account Summary │  - Bills        │
│  - Session Mgmt      │  - Quick Stats     │  - Payments     │
│                      │                    │  - Receipts     │
└──────────────┬───────────────────┬────────────────┬─────────┘
               │                   │                │
               ▼                   ▼                ▼
┌──────────────────────┐  ┌─────────────────────────────────┐
│  Client Auth Service │  │   Existing Services Layer       │
│  - authenticate()    │  │  - BillingService               │
│  - create_session()  │  │  - PaymentService               │
│  - destroy_session() │  │  - MikrotikService              │
│  - require_login()   │  │  - ReceiptService               │
└──────────────────────┘  └─────────────────────────────────┘
               │                   │
               ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│  Client Model (+ password_hash)  │  Billing  │  Payment     │
│  Receipt  │  Mikrotik API                                    │
└─────────────────────────────────────────────────────────────┘
```


### Daloy ng Authentication (Authentication Flow)

```
Client Login Request
       │
       ▼
┌──────────────────────┐
│ Validate Credentials │
│ (PPPoE username/pwd) │
└──────────┬───────────┘
           │
           ▼
    ┌──────────┐
    │ Valid?   │
    └─┬────┬───┘
      │    │
   Oo │    │Hindi
      │    │
      ▼    ▼
   Create  Return
   Session Error
      │
      ▼
   Redirect sa
   Dashboard
```

### Pamamahala ng Session (Session Management)

Ang portal ay gumagamit ng Flask session management na may sumusunod na security measures:

- **HttpOnly Cookies**: Pumipigil sa JavaScript access sa session cookies
- **Secure Flag**: Nagsisiguro na ang cookies ay nai-transmit lang sa HTTPS sa production
- **Session Timeout**: 30-minute inactivity timeout
- **Session Regeneration**: Bagong session ID na ginawa pagkatapos ng successful login
- **CSRF Protection**: Lahat ng forms ay protektado ng CSRF tokens

### Access Control Model

```
┌─────────────────────────────────────────────────────────┐
│                   Request Middleware                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
              ┌──────────────┐
              │ Session Type?│
              └──┬────────┬──┘
                 │        │
          Client │        │ Admin
                 │        │
                 ▼        ▼
         ┌────────────┐ ┌────────────┐
         │ Client     │ │ Admin      │
         │ Routes     │ │ Routes     │
         │ Allowed    │ │ Allowed    │
         └────────────┘ └────────────┘
```

## Mga Bahagi at Interface (Components and Interfaces)

### 1. Client Authentication Service

**Layunin**: Pangasiwaan ang client login, logout, at session management na hiwalay sa admin authentication.

**Interface**:
```python
class ClientAuthService:
    @staticmethod
    def authenticate_client(pppoe_username: str, password: str) -> Client | None:
        """I-authenticate ang client gamit ang PPPoE credentials"""
        
    @staticmethod
    def create_client_session(client: Client) -> None:
        """Gumawa ng authenticated session para sa client"""
        
    @staticmethod
    def destroy_client_session() -> None:
        """Sirain ang client session (logout)"""
        
    @staticmethod
    def get_current_client() -> Client | None:
        """Kunin ang kasalukuyang authenticated client mula sa session"""
        
    @staticmethod
    def require_client_login(func):
        """Decorator para kailanganin ang client authentication"""
```

**Mga Pangunahing Gawi (Key Behaviors)**:
- Vina-validate ang PPPoE username at password laban sa Client model
- Gumagamit ng bcrypt para sa password verification
- Nag-store ng client_id sa Flask session (hiwalay sa Flask-Login's user session)
- Nag-update ng last_login timestamp sa successful authentication
- Nag-implement ng 30-minute session timeout

### 2. Client Dashboard Service

**Layunin**: Pagsama-samahin at kalkulahin ang dashboard metrics para sa client account summary.

**Interface**:
```python
class ClientDashboardService:
    @staticmethod
    def get_dashboard_data(client_id: int) -> dict:
        """Kunin ang lahat ng dashboard data para sa client"""
        
    @staticmethod
    def calculate_remaining_days(client_id: int) -> int:
        """Kalkulahin ang mga araw hanggang sa susunod na payment due"""
        
    @staticmethod
    def get_total_unpaid_balance(client_id: int) -> float:
        """Kalkulahin ang kabuuang unpaid balance"""
        
    @staticmethod
    def get_connection_status(pppoe_username: str) -> dict:
        """Kunin ang kasalukuyang connection status mula sa Mikrotik"""
```

**Mga Pangunahing Gawi**:
- Pinagsasama ang data mula sa maraming services (Billing, Payment, Mikrotik)
- Kinakalkula ang remaining days mula sa pinakamaagang unpaid due date
- Sinusuma ang lahat ng unpaid at overdue billing records
- Nag-query sa Mikrotik para sa real-time connection status
- Nagbabalik ng structured data para sa dashboard rendering

### 3. GCash Payment Service

**Layunin**: Gumawa ng GCash payment deep links na may pre-filled payment information.

**Interface**:
```python
class GCashPaymentService:
    GCASH_NUMBER = "09495502589"
    GCASH_NAME = "Jean Kimberlyn L"
    
    @staticmethod
    def generate_payment_link(billing_id: int) -> str:
        """Gumawa ng GCash payment URL na may pre-filled details"""
        
    @staticmethod
    def generate_reference_number(client_id: int, billing_id: int) -> str:
        """Gumawa ng unique payment reference number"""
```

**Mga Pangunahing Gawi**:
- Gumagawa ng reference number format: `CLIENT{client_id}-BILL{billing_id}-{timestamp}`
- Lumilikha ng GCash deep link URL na may recipient, amount, at reference
- URL format: `gcash://pay?number={number}&name={name}&amount={amount}&reference={ref}`
- Bumabalik sa web URL kung hindi supported ang deep link

### 4. Client Portal Routes

**Blueprint**: `client_portal_bp`

**Mga Route**:
- `GET /client/login` - Ipakita ang client login page
- `POST /client/login` - Proseso ang client login
- `GET /client/logout` - I-logout ang client
- `GET /client/dashboard` - Ipakita ang client dashboard
- `GET /client/bills` - Listahan ng client billing records
- `GET /client/bills/<id>` - Tingnan ang billing detail
- `GET /client/bills/<id>/pay` - Gumawa ng GCash payment link at i-redirect
- `GET /client/payments` - Listahan ng client payment history
- `GET /client/payments/<id>` - Tingnan ang payment detail
- `GET /client/receipts/<id>` - Tingnan ang receipt

**Access Control**: Lahat ng routes maliban sa `/client/login` ay nangangailangan ng client authentication gamit ang `@require_client_login` decorator.

### 5. Client Portal Templates

**Base Template**: `client_base.html`
- Hiwalay sa admin base template
- Client-specific navigation (Dashboard, Bills, Payments)
- Mobile-responsive navbar na may hamburger menu
- Logout button
- Walang admin functionality links

**Dashboard Template**: `client_dashboard.html`
- Account summary cards (Remaining Days, Unpaid Balance, Connection Status, Plan Details)
- Connection status indicator (online/offline na may visual badge)
- Quick action buttons (View Bills, View Payments)
- Responsive grid layout (1 column mobile, 2 columns tablet, 4 columns desktop)

**Bills List Template**: `client_bills.html`
- Table ng billing records na may status badges
- Filters: Status (All, Unpaid, Paid, Overdue)
- "Pay Now" button para sa unpaid bills
- Mobile-responsive table (stacked cards sa mobile)

**Payments List Template**: `client_payments.html`
- Table ng payment records
- Payment method badges
- Link para tingnan ang receipt
- Mobile-responsive table

## Mga Data Model (Data Models)

### Client Model Extension

Ang existing Client model ay nangangailangan ng password field para sa authentication:

```python
class Client(db.Model):
    # ... existing fields ...
    password_hash = db.Column(db.String(255), nullable=False)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password: str) -> None:
        """I-hash at i-set ang client password"""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """I-verify ang password laban sa naka-store na hash"""
        password_bytes = password.encode('utf-8')
        hash_bytes = self.password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
```

**Migration Strategy**:
1. Idagdag ang `password_hash` column (nullable muna)
2. Idagdag ang `last_login` column
3. Gumawa ng default passwords para sa existing clients (PPPoE username bilang default)
4. I-hash at i-store ang default passwords
5. Gawing non-nullable ang `password_hash`

**Default Password Generation**:
- Para sa existing clients na walang passwords: gamitin ang PPPoE username bilang initial password
- Ang mga admin ay maaaring mag-reset ng client passwords sa admin interface
- Future enhancement: client password change functionality

### Session Data Structure

Ang client sessions ay nag-store ng minimal data sa Flask session:

```python
session = {
    'client_id': int,           # Client primary key
    'client_username': str,     # PPPoE username para sa display
    'login_time': datetime,     # Session creation time
    'last_activity': datetime   # Last request time
}
```

### Dashboard Data Structure

```python
dashboard_data = {
    'client': {
        'full_name': str,
        'pppoe_username': str,
        'plan_name': str,
        'plan_amount': float,
        'status': str
    },
    'remaining_days': int,      # Mga araw hanggang sa susunod na payment due
    'unpaid_balance': float,    # Kabuuang unpaid amount
    'connection_status': {
        'online': bool,
        'address': str | None,  # IP address kung online
        'uptime': str | None    # Connection uptime kung online
    },
    'recent_bills': list[Billing],    # Huling 3 billing records
    'recent_payments': list[Payment]  # Huling 3 payments
}
```

### GCash Payment Link Structure

```python
gcash_link = {
    'url': str,                 # Buong GCash payment URL
    'reference': str,           # Unique reference number
    'amount': float,            # Payment amount
    'recipient_number': str,    # GCash number
    'recipient_name': str       # GCash account name
}
```


## Mga Katangiang Pagtutumbas (Correctness Properties)

*Ang property ay isang katangian o gawi na dapat manatiling totoo sa lahat ng valid na pagpapatupad ng sistema—sa madaling salita, isang pormal na pahayag tungkol sa kung ano ang dapat gawin ng sistema. Ang mga properties ay nagsisilbing tulay sa pagitan ng human-readable specifications at machine-verifiable correctness guarantees.*

### Property 1: Valid Client Authentication ay Lumilikha ng Session

*Para sa anumang* client na may valid na PPPoE username at password credentials, ang pag-submit ng mga credentials na iyon sa login endpoint ay dapat lumikha ng authenticated session na may client_id na naka-store sa session.

**Vina-validate: Requirements 1.2**

### Property 2: Invalid Credentials ay Tumatanggi ng Access

*Para sa anumang* invalid credentials (hindi umiiral na username, maling password, o walang laman na credentials), ang pag-submit nito sa login endpoint ay dapat tumangging mag-access at hindi lumikha ng session.

**Vina-validate: Requirements 1.3**

### Property 3: Session Persistence sa Maraming Requests

*Para sa anumang* authenticated client session, ang paggawa ng maraming requests sa protected endpoints ay dapat mapanatili ang parehong session state hanggang sa explicit logout o timeout.

**Vina-validate: Requirements 1.4**

### Property 4: Unauthenticated Access ay Nag-redirect sa Login

*Para sa anumang* protected client portal route, ang pag-access nito nang walang authenticated session ay dapat mag-redirect sa client login page.

**Vina-validate: Requirements 1.5**

### Property 5: Logout ay Nag-terminate ng Session

*Para sa anumang* authenticated client session, ang pagtawag sa logout function ay dapat mag-terminate ng session at ang susunod na requests ay hindi na dapat authenticated.

**Vina-validate: Requirements 1.6**

### Property 6: Password Storage Security

*Para sa anumang* password na naka-set sa client account, ang naka-store na password_hash ay hindi dapat katumbas ng plaintext password, at ang check_password method ay dapat tama ang pag-verify ng orihinal na password.

**Vina-validate: Requirements 2.2, 2.4**

### Property 7: Dashboard Data Completeness

*Para sa anumang* authenticated client na nag-access ng dashboard, ang response ay dapat maglaman ng remaining_days, unpaid_balance, connection_status, plan_name, at plan_amount.

**Vina-validate: Requirements 3.1, 3.2, 3.3, 3.4**

### Property 8: Remaining Days Calculation Accuracy

*Para sa anumang* client na may unpaid billing records, ang remaining_days calculation ay dapat katumbas ng pagkakaiba sa pagitan ng pinakamaagang due_date at ang kasalukuyang petsa.

**Vina-validate: Requirements 3.5**

### Property 9: Connection Status Indicator Accuracy

*Para sa anumang* client, ang connection status indicator na ipinapakita sa dashboard ay dapat tumugma sa online/offline status na ibinalik ng Mikrotik service para sa PPPoE username ng client na iyon.

**Vina-validate: Requirements 3.6, 3.7**

### Property 10: Client Billing Records Completeness

*Para sa anumang* authenticated client, ang billing list ay dapat maglaman ng lahat at tanging mga billing records kung saan ang client_id ay tumutugma sa authenticated client's ID.

**Vina-validate: Requirements 4.1, 4.4**

### Property 11: Billing Record Field Completeness

*Para sa anumang* billing record na ipinapakita sa client, ang rendered output ay dapat maglaman ng billing_period, amount, due_date, at status fields.

**Vina-validate: Requirements 4.2**

### Property 12: Billing Detail Completeness

*Para sa anumang* billing record na na-access ng may-ari nito, ang detail view ay dapat magpakita ng lahat ng charge information kasama ang amount breakdown at billing period details.

**Vina-validate: Requirements 4.5**

### Property 13: Pay Button Presence para sa Unpaid Bills

*Para sa anumang* billing record na may status na 'unpaid' o 'overdue', ang rendered billing list ay dapat maglaman ng "Pay Now" button o link para sa record na iyon.

**Vina-validate: Requirements 5.1**

### Property 14: GCash Payment Link Completeness

*Para sa anumang* unpaid billing record, ang paggawa ng GCash payment link ay dapat mag-produce ng URL na naglalaman ng recipient number (09495502589), recipient name (Jean Kimberlyn L), ang billing amount, at unique reference number na nag-identify ng client at billing record.

**Vina-validate: Requirements 5.2, 5.3, 5.4, 5.5, 5.6**

### Property 15: GCash Payment Link Reference Uniqueness

*Para sa anumang* dalawang magkaibang billing records (magkaibang billing_id), ang mga ginawang GCash payment reference numbers ay dapat unique.

**Vina-validate: Requirements 5.6**

### Property 16: Payment Link Redirect Behavior

*Para sa anumang* unpaid billing record, ang pag-request sa pay endpoint ay dapat magbalik ng HTTP redirect response sa GCash payment URL.

**Vina-validate: Requirements 5.7**

### Property 17: Client Payment Records Completeness

*Para sa anumang* authenticated client, ang payment list ay dapat maglaman ng lahat at tanging mga payment records kung saan ang client_id ay tumutugma sa authenticated client's ID.

**Vina-validate: Requirements 6.1, 6.4**

### Property 18: Payment Record Field Completeness

*Para sa anumang* payment record na ipinapakita sa client, ang rendered output ay dapat maglaman ng payment_date, amount, payment_method, at reference_number fields.

**Vina-validate: Requirements 6.2**

### Property 19: Payment Records Sorted by Date Descending

*Para sa anumang* listahan ng payment records na ipinapakita sa client, ang petsa ng bawat payment ay dapat mas malaki o katumbas ng petsa ng susunod na payment sa listahan.

**Vina-validate: Requirements 6.3**

### Property 20: Payment Detail ay Nagpapakita ng Associated Billing

*Para sa anumang* payment record na na-access ng may-ari nito, ang detail view ay dapat magpakita ng associated billing record information kasama ang billing period at amount.

**Vina-validate: Requirements 6.5**

### Property 21: Receipt Link Availability

*Para sa anumang* payment record na may associated receipt, ang payment display ay dapat maglaman ng link o button para tingnan ang receipt na iyon.

**Vina-validate: Requirements 7.1**

### Property 22: Receipt Content Completeness

*Para sa anumang* receipt na na-access ng may-ari nito, ang rendered receipt ay dapat magpakita ng payment_date, amount, payment_method, at reference_number.

**Vina-validate: Requirements 7.2**

### Property 23: Receipt Download Availability

*Para sa anumang* receipt na na-access ng may-ari nito, ang receipt page ay dapat maglaman ng download option o print-friendly format.

**Vina-validate: Requirements 7.3, 7.4**

### Property 24: Data Isolation sa Pagitan ng mga Clients

*Para sa anumang* authenticated client, hindi nila dapat ma-access ang billing records, payment records, o receipts na pag-aari ng ibang client (magkaibang client_id).

**Vina-validate: Requirements 4.4, 6.4, 7.5**

### Property 25: Mobile Table Layout Walang Horizontal Scroll

*Para sa anumang* table na ipinapakita sa client portal sa viewport width na 320px, ang table ay hindi dapat mag-cause ng horizontal scrolling (overflow-x ay dapat hidden o ang content ay dapat mag-wrap).

**Vina-validate: Requirements 8.5**

### Property 26: Session Cookie Security Flags

*Para sa anumang* client session cookie na naka-set ng portal, ang cookie ay dapat may HttpOnly flag na enabled.

**Vina-validate: Requirements 9.1**

### Property 27: Session Timeout Pagkatapos ng Inactivity

*Para sa anumang* client session, kung walang requests na ginawa sa loob ng 30 minuto, ang susunod na request sa protected endpoint ay dapat mag-redirect sa login (session expired).

**Vina-validate: Requirements 9.2**

### Property 28: Session ID Regeneration sa Login

*Para sa anumang* successful client login, ang session identifier pagkatapos ng login ay dapat magkaiba sa session identifier bago ang login.

**Vina-validate: Requirements 9.3**

### Property 29: CSRF Protection sa mga Forms

*Para sa anumang* form submission sa client portal, ang request ay dapat mangailangan ng valid CSRF token, at ang mga requests na walang valid tokens ay dapat tanggihan.

**Vina-validate: Requirements 9.4**

### Property 30: Expired Session Redirect

*Para sa anumang* expired client session, ang pagtatangka na mag-access ng protected endpoint ay dapat mag-redirect sa client login page.

**Vina-validate: Requirements 9.5**

### Property 31: Authentication Credential Separation

*Para sa anumang* admin user credentials, hindi dapat sila successfully mag-authenticate sa client login endpoint, at para sa anumang client credentials, hindi dapat sila successfully mag-authenticate sa admin login endpoint.

**Vina-validate: Requirements 10.1, 10.3**

### Property 32: Client Access Control sa Admin Routes

*Para sa anumang* authenticated client session, ang pagtatangka na mag-access ng admin routes ay dapat magbalik ng access denied error o redirect, hindi mag-grant ng access.

**Vina-validate: Requirements 10.2, 10.4**

### Property 33: Session Type Isolation

*Para sa anumang* client session at admin session na umiiral nang sabay-sabay, hindi dapat sila mag-interfere sa authentication state o accessible routes ng isa't isa.

**Vina-validate: Requirements 10.5**


## Pag-handle ng mga Error (Error Handling)

### Authentication Errors

**Invalid Credentials**:
- Ipakita ang user-friendly error message: "Invalid username o password"
- Huwag ibunyag kung umiiral ang username (security best practice)
- I-log ang failed login attempts para sa security monitoring
- Rate limit ang login attempts para pigilan ang brute force attacks

**Session Expiration**:
- I-redirect sa login page na may message: "Nag-expire na ang iyong session. Mag-login ulit."
- I-clear ang expired session data
- I-preserve ang intended destination URL para sa post-login redirect

**Account Status Errors**:
- Kung ang client account ay inactive: "Ang iyong account ay kasalukuyang inactive. Makipag-ugnayan sa support."
- Pigilan ang login para sa inactive accounts
- I-log ang access attempts para sa inactive accounts

### Data Access Errors

**Unauthorized Access**:
- Magbalik ng 403 Forbidden para sa mga pagtatangka na mag-access ng data ng ibang clients
- I-log ang unauthorized access attempts
- Ipakita ang generic error: "Wala kang permission na mag-access ng resource na ito"

**Resource Not Found**:
- Magbalik ng 404 Not Found para sa hindi umiiral na billing/payment/receipt IDs
- Ipakita ang user-friendly message: "Hindi nahanap ang hiniling na record"
- Siguraduhing ang error ay hindi nag-leak ng impormasyon tungkol sa data ng ibang clients

**Mikrotik Connection Errors**:
- Ipakita ang connection status bilang "Unknown" kung ang Mikrotik ay hindi maabot
- I-log ang Mikrotik connection failures
- I-cache ang last known status para sa maikling panahon
- Ipakita ang message: "Connection status ay pansamantalang hindi available"

### Payment Processing Errors

**GCash Link Generation Errors**:
- Kung ang billing record ay hindi nahanap: "Hindi nahanap ang billing record"
- Kung ang billing ay paid na: "Ang bill na ito ay bayad na"
- Kung ang amount ay invalid: "Invalid na payment amount"
- I-log ang generation failures para sa troubleshooting

**Payment Verification Errors**:
- Kailangan ng manual payment verification (ang GCash ay walang automatic callbacks)
- Ang admin ay dapat manually mag-mark ng payments bilang received
- Ipakita ang instructions: "Pagkatapos kumpletuhin ang payment, maghintay para sa admin confirmation"

### Form Validation Errors

**CSRF Token Errors**:
- Magbalik ng 400 Bad Request para sa missing/invalid CSRF tokens
- Ipakita ang message: "Nag-expire ang security token. Subukan ulit."
- I-regenerate ang form na may bagong token

**Input Validation Errors**:
- Ipakita ang field-specific error messages
- I-preserve ang valid form data sa error
- I-highlight ang invalid fields

### Database Errors

**Connection Failures**:
- Ipakita ang generic error: "Ang serbisyo ay pansamantalang hindi available. Subukan ulit mamaya."
- I-log ang database errors na may full stack trace
- Magbalik ng 503 Service Unavailable status

**Data Integrity Errors**:
- I-log ang constraint violations
- Ipakita ang user-friendly message nang hindi nag-expose ng database details
- I-rollback ang transactions sa error

## Estratehiya sa Pagsusuri (Testing Strategy)

### Unit Testing

Ang unit tests ay mag-verify ng specific examples, edge cases, at error conditions:

**Authentication Tests**:
- I-test ang login na may valid credentials
- I-test ang login na may invalid username
- I-test ang login na may invalid password
- I-test ang login na may walang laman na credentials
- I-test ang logout functionality
- I-test ang session creation at destruction
- I-test ang password hashing at verification
- I-test ang default password generation para sa bagong clients

**Dashboard Tests**:
- I-test ang dashboard data aggregation na may mock data
- I-test ang remaining days calculation na may iba't ibang due dates
- I-test ang unpaid balance calculation na may maraming bills
- I-test ang connection status display na may online/offline states
- I-test ang dashboard rendering na walang billing records
- I-test ang dashboard rendering na walang payments

**GCash Payment Tests**:
- I-test ang payment link generation na may valid billing record
- I-test na ang payment link ay naglalaman ng lahat ng kinakailangang fields
- I-test ang reference number format at uniqueness
- I-test ang payment link generation para sa paid bill (dapat mag-fail)
- I-test ang payment link generation para sa hindi umiiral na bill (dapat mag-fail)

**Access Control Tests**:
- I-test na ang client ay maaaring mag-access ng sariling data
- I-test na ang client ay hindi maaaring mag-access ng data ng ibang client
- I-test na ang unauthenticated access ay nag-redirect sa login
- I-test na ang admin credentials ay hindi gumagana sa client login
- I-test na ang client credentials ay hindi gumagana sa admin login

**Session Security Tests**:
- I-test na ang session cookie ay may HttpOnly flag
- I-test ang session timeout pagkatapos ng 30 minuto
- I-test ang session ID regeneration sa login
- I-test ang CSRF token validation sa forms

### Property-Based Testing

Ang property-based tests ay mag-verify ng universal properties sa randomized inputs gamit ang Hypothesis library para sa Python. Ang bawat test ay mag-run ng minimum na 100 iterations.

**Test Configuration**:
```python
from hypothesis import given, settings
import hypothesis.strategies as st

@settings(max_examples=100)
```

**Mga Halimbawa ng Property Test**:

**Property 1: Valid Client Authentication ay Lumilikha ng Session**
```python
@given(st.text(min_size=1), st.text(min_size=1))
@settings(max_examples=100)
def test_valid_authentication_creates_session(username, password):
    """Feature: client-portal, Property 1: Para sa anumang client na may valid credentials,
    ang authentication ay dapat lumikha ng session"""
```

**Property 6: Password Storage Security**
```python
@given(st.text(min_size=1, max_size=100))
@settings(max_examples=100)
def test_password_hashing_security(password):
    """Feature: client-portal, Property 6: Para sa anumang password, ang stored hash ay
    hindi dapat katumbas ng plaintext at ang verification ay dapat gumana nang tama"""
```

**Property 8: Remaining Days Calculation Accuracy**
```python
@given(st.dates())
@settings(max_examples=100)
def test_remaining_days_calculation(due_date):
    """Feature: client-portal, Property 8: Para sa anumang due date, ang remaining days
    ay dapat katumbas ng pagkakaiba mula sa kasalukuyang petsa"""
```

**Property 14: GCash Payment Link Completeness**
```python
@given(st.integers(min_value=1), st.floats(min_value=0.01, max_value=100000))
@settings(max_examples=100)
def test_gcash_link_completeness(billing_id, amount):
    """Feature: client-portal, Property 14: Para sa anumang billing record, ang GCash link
    ay dapat maglaman ng recipient number, name, amount, at reference"""
```

**Property 19: Payment Records Sorted by Date Descending**
```python
@given(st.lists(st.dates(), min_size=2))
@settings(max_examples=100)
def test_payment_sorting(payment_dates):
    """Feature: client-portal, Property 19: Para sa anumang listahan ng payments, dapat
    silang naka-sort by date descending"""
```

**Property 24: Data Isolation sa Pagitan ng mga Clients**
```python
@given(st.integers(min_value=1), st.integers(min_value=1))
@settings(max_examples=100)
def test_data_isolation(client_id_1, client_id_2):
    """Feature: client-portal, Property 24: Para sa anumang dalawang magkaibang clients,
    ang isa ay hindi dapat mag-access ng data ng isa"""
```

### Integration Testing

Ang integration tests ay mag-verify ng interaction sa pagitan ng mga components:

**Client Portal Flow Tests**:
- I-test ang kumpletong login → dashboard → view bills → generate payment link flow
- I-test ang login → view payments → view receipt flow
- I-test ang session timeout habang nag-navigate
- I-test ang concurrent client at admin sessions

**Mikrotik Integration Tests**:
- I-test ang connection status retrieval para sa online clients
- I-test ang connection status retrieval para sa offline clients
- I-test ang handling ng Mikrotik connection failures
- I-test ang connection status caching

**Database Integration Tests**:
- I-test ang client authentication na may database
- I-test ang dashboard data retrieval na may joins
- I-test ang billing at payment record queries
- I-test ang transaction rollback sa errors

### End-to-End Testing

Ang E2E tests ay mag-verify ng kumpletong user workflows gamit ang Selenium o Playwright:

**Client Portal Workflows**:
- Kumpletong login at dashboard viewing
- Tingnan ang billing records at gumawa ng payment link
- Tingnan ang payment history at receipts
- Logout at i-verify ang session termination

**Responsive Design Tests**:
- I-test ang portal sa 320px width (mobile)
- I-test ang portal sa 768px width (tablet)
- I-test ang portal sa 1024px+ width (desktop)
- I-verify na walang horizontal scrolling sa mobile
- I-verify ang navigation menu responsiveness

**Security Tests**:
- I-test ang CSRF protection sa lahat ng forms
- I-test ang session timeout enforcement
- I-test ang unauthorized access attempts
- I-test ang credential separation sa pagitan ng client at admin

### Mga Layunin sa Test Coverage

- Unit test coverage: 90%+ para sa services at models
- Property test coverage: Lahat ng 33 correctness properties ay implemented
- Integration test coverage: Lahat ng major component interactions
- E2E test coverage: Lahat ng critical user workflows

### Mga Gamit sa Testing

- **Unit Testing**: pytest
- **Property-Based Testing**: Hypothesis
- **Integration Testing**: pytest na may Flask test client
- **E2E Testing**: Playwright o Selenium
- **Coverage**: pytest-cov
- **Mocking**: unittest.mock, pytest-mock
- **Database**: SQLite in-memory para sa tests
