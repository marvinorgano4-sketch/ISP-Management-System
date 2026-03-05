# Requirements Document

## Introduksyon

Ang feature na ito ay magpapahusay sa admin dashboard ng ISP Billing System upang magbigay ng mas mabilis na pag-edit ng client plans, real-time bandwidth monitoring, at kakayahang i-disconnect ang mga client. Makakatulong ito sa admin na mas epektibong pamahalaan ang network at mga client.

## Glossary

- **Admin_Dashboard**: Ang pangunahing interface kung saan nakikita ng administrator ang lahat ng mahalagang impormasyon tungkol sa ISP operations
- **Client_List**: Ang listahan ng lahat ng mga client na may account sa ISP system
- **Plan_Editor**: Ang component na nagbibigay-daan sa pag-edit ng plan details
- **Bandwidth_Monitor**: Ang component na nagpapakita ng real-time bandwidth usage data
- **Mikrotik_Service**: Ang existing service na nag-integrate sa Mikrotik router API
- **PPPoE_Session**: Ang active connection ng client sa Mikrotik router
- **RX**: Receive bandwidth (download) na sinusukat sa Mbps
- **TX**: Transmit bandwidth (upload) na sinusukat sa Mbps
- **Congestion_Indicator**: Ang visual warning na nagpapakita kung ang total bandwidth ay malapit na o lumampas na sa threshold
- **Disconnect_Button**: Ang button na ginagamit upang i-terminate ang active PPPoE session ng client

## Requirements

### Requirement 1: Inline Plan Editing

**User Story:** Bilang admin, gusto kong ma-edit ang plan name at plan amount ng client nang direkta mula sa client list, upang hindi na ako mag-navigate sa ibang page para sa simpleng changes.

#### Acceptance Criteria

1. WHEN ang admin ay nag-click sa plan name o plan amount field sa Client_List, THE Plan_Editor SHALL mag-display ng editable input field
2. WHEN ang admin ay nag-input ng bagong value at nag-save, THE Plan_Editor SHALL mag-update ng client record sa database
3. WHEN ang admin ay nag-input ng invalid value (halimbawa: negative amount), THE Plan_Editor SHALL mag-display ng error message at hindi mag-save
4. WHEN ang save operation ay successful, THE Plan_Editor SHALL mag-display ng success confirmation at mag-refresh ng displayed value
5. WHEN ang admin ay nag-cancel ng edit operation, THE Plan_Editor SHALL mag-restore ng original value

### Requirement 2: Client Bandwidth Monitoring

**User Story:** Bilang admin, gusto kong makita ang real-time RX at TX bandwidth ng bawat client, upang malaman ko kung sino ang gumagamit ng maraming bandwidth at kung may problema sa connection.

#### Acceptance Criteria

1. WHEN ang Client_List ay nag-load, THE Bandwidth_Monitor SHALL kumuha ng bandwidth data mula sa Mikrotik_Service para sa bawat active client
2. FOR EACH active PPPoE_Session, THE Bandwidth_Monitor SHALL mag-display ng current RX value sa Mbps
3. FOR EACH active PPPoE_Session, THE Bandwidth_Monitor SHALL mag-display ng current TX value sa Mbps
4. WHEN ang client ay offline (walang active PPPoE_Session), THE Bandwidth_Monitor SHALL mag-display ng "Offline" status
5. THE Bandwidth_Monitor SHALL mag-update ng bandwidth values every 10 seconds upang mag-reflect ng current usage
6. WHEN ang admin ay nag-view ng client detail page, THE Bandwidth_Monitor SHALL mag-display ng bandwidth information doon din

### Requirement 3: ISP Total Bandwidth Dashboard

**User Story:** Bilang admin, gusto kong makita ang kabuuang RX at TX bandwidth ng lahat ng clients, upang malaman ko kung congested na ba ang network at kailangan ko nang mag-upgrade ng capacity.

#### Acceptance Criteria

1. WHEN ang Admin_Dashboard ay nag-load, THE Bandwidth_Monitor SHALL mag-calculate ng total RX ng lahat ng active PPPoE_Sessions
2. WHEN ang Admin_Dashboard ay nag-load, THE Bandwidth_Monitor SHALL mag-calculate ng total TX ng lahat ng active PPPoE_Sessions
3. THE Bandwidth_Monitor SHALL mag-display ng total RX value sa Mbps sa dashboard
4. THE Bandwidth_Monitor SHALL mag-display ng total TX value sa Mbps sa dashboard
5. THE Bandwidth_Monitor SHALL mag-update ng total bandwidth values every 10 seconds
6. WHEN ang total RX o total TX ay umabot sa 80% ng configured threshold, THE Congestion_Indicator SHALL mag-display ng warning (yellow indicator)
7. WHEN ang total RX o total TX ay lumampas sa configured threshold, THE Congestion_Indicator SHALL mag-display ng critical alert (red indicator)
8. THE Admin_Dashboard SHALL mag-allow sa admin na i-configure ang bandwidth threshold value

### Requirement 4: Client Disconnect Functionality

**User Story:** Bilang admin, gusto kong may disconnect button para sa bawat client, upang mabilis kong ma-disconnect ang kanilang connection kung kinakailangan (halimbawa: hindi pa bayad o may violation).

#### Acceptance Criteria

1. WHERE ang client ay may active PPPoE_Session, THE Disconnect_Button SHALL mag-display sa Client_List
2. WHERE ang client ay offline, THE Disconnect_Button SHALL hindi mag-display
3. WHEN ang admin ay nag-click ng Disconnect_Button, THE Admin_Dashboard SHALL mag-display ng confirmation dialog
4. WHEN ang admin ay nag-confirm sa dialog, THE Mikrotik_Service SHALL mag-terminate ng PPPoE_Session ng client
5. WHEN ang disconnect operation ay successful, THE Admin_Dashboard SHALL mag-display ng success message at mag-update ng client status to "Offline"
6. IF ang disconnect operation ay nabigo, THEN THE Admin_Dashboard SHALL mag-display ng error message na may detalye ng failure reason
7. THE Disconnect_Button SHALL mag-display din sa client detail page kung ang client ay online
8. WHEN ang client ay na-disconnect, THE Bandwidth_Monitor SHALL mag-update ng displayed values upang mag-reflect ng bagong status

### Requirement 5: Bandwidth Data Retrieval

**User Story:** Bilang system, kailangan kong kumuha ng accurate bandwidth data mula sa Mikrotik, upang ma-display ang tamang impormasyon sa admin.

#### Acceptance Criteria

1. THE Mikrotik_Service SHALL mag-query ng active PPPoE sessions mula sa Mikrotik API
2. FOR EACH active PPPoE_Session, THE Mikrotik_Service SHALL kumuha ng current RX rate sa bytes per second
3. FOR EACH active PPPoE_Session, THE Mikrotik_Service SHALL kumuha ng current TX rate sa bytes per second
4. THE Mikrotik_Service SHALL mag-convert ng bandwidth values mula bytes per second to Mbps
5. WHEN ang Mikrotik API ay hindi available, THE Mikrotik_Service SHALL mag-return ng error status
6. THE Mikrotik_Service SHALL mag-cache ng bandwidth data for 5 seconds upang hindi mag-overload ang Mikrotik router
7. THE Mikrotik_Service SHALL mag-match ng PPPoE session username sa client username sa database

### Requirement 6: Error Handling at User Feedback

**User Story:** Bilang admin, gusto kong makatanggap ng clear feedback kung may error o successful ang operation, upang malaman ko kung ano ang nangyari at ano ang dapat kong gawin.

#### Acceptance Criteria

1. WHEN ang Mikrotik_Service ay hindi maka-connect sa router, THE Admin_Dashboard SHALL mag-display ng error message na "Hindi maka-connect sa Mikrotik router"
2. WHEN ang plan edit operation ay nabigo, THE Plan_Editor SHALL mag-display ng specific error message
3. WHEN ang disconnect operation ay nabigo, THE Admin_Dashboard SHALL mag-display ng error message na may troubleshooting hint
4. THE Admin_Dashboard SHALL mag-display ng loading indicator habang nag-fetch ng bandwidth data
5. WHEN ang operation ay successful, THE Admin_Dashboard SHALL mag-display ng success message na automatically mag-disappear after 3 seconds
6. IF ang admin ay walang permission para sa operation, THEN THE Admin_Dashboard SHALL mag-display ng "Access Denied" message

### Requirement 7: Performance at Scalability

**User Story:** Bilang system, kailangan kong mag-perform nang mabuti kahit maraming clients, upang hindi mag-slow down ang admin dashboard.

#### Acceptance Criteria

1. THE Bandwidth_Monitor SHALL mag-fetch ng bandwidth data using batch queries upang minimize ang API calls sa Mikrotik
2. THE Admin_Dashboard SHALL mag-implement ng pagination sa Client_List kung may more than 50 clients
3. THE Bandwidth_Monitor SHALL mag-use ng asynchronous requests upang hindi mag-block ang UI habang nag-fetch ng data
4. THE Admin_Dashboard SHALL mag-load ng bandwidth data only for visible clients sa current page
5. WHEN ang bandwidth update ay tumatagal ng more than 5 seconds, THE Admin_Dashboard SHALL mag-display ng timeout warning
6. THE Mikrotik_Service SHALL mag-limit ng concurrent API requests to 5 upang hindi ma-overwhelm ang router
