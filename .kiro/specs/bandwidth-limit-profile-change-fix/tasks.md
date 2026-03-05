# Implementation Plan

- [x] 1. Gumawa ng bug condition exploration test
  - **Property 1: Fault Condition** - API Connection at Profile Matching Failures
  - **KRITIKAL**: Ang test na ito ay DAPAT BUMAGSAK sa unfixed code - ang pagbagsak ay nagpapatunay na ang bug ay umiiral
  - **HUWAG subukang ayusin ang test o ang code kapag bumagsak ito**
  - **TANDAAN**: Ang test na ito ay nag-encode ng expected behavior - ito ay mag-validate ng fix kapag pumasa pagkatapos ng implementation
  - **LAYUNIN**: Ipakita ang mga counterexample na nagpapakita na ang bug ay umiiral
  - **Scoped PBT Approach**: Para sa deterministic bugs, i-scope ang property sa konkretong failing case(s) para masiguro ang reproducibility
  - Test implementation details mula sa Fault Condition sa design:
    - Test 1a: Connection Failure - Subukan kumonekta sa Mikrotik gamit ang configured credentials
    - Test 1b: Profile Mismatch - Tawagan ang `set_bandwidth_limit("test_user", 5000000, 5000000)` kapag ang profile "5MBPS" ay hindi umiiral pero ang "5Mbps" ay umiiral
    - Test 1c: Profile Discovery - Subukan kunin ang listahan ng PPP profiles (ang method ay hindi umiiral sa unfixed code)
    - Test 1d: Case Sensitivity - Gumawa ng profile "5Mbps" sa Mikrotik, tawagan ang `set_bandwidth_limit()` na may 5 Mbps
  - Ang test assertions ay dapat tumugma sa Expected Behavior Properties mula sa design
  - Patakbuhin ang test sa UNFIXED code
  - **INAASAHANG RESULTA**: Ang test ay BUMAGSAK (ito ay tama - pinapatunayan nito na ang bug ay umiiral)
  - I-document ang mga counterexample na natagpuan para maintindihan ang root cause
  - Markahan ang task bilang complete kapag ang test ay nakasulat, napatakbo, at ang pagbagsak ay na-document
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7_

- [x] 2. Gumawa ng preservation property tests (BAGO i-implement ang fix)
  - **Property 2: Preservation** - Existing Mikrotik Operations
  - **IMPORTANTE**: Sundin ang observation-first methodology
  - I-observe ang behavior sa UNFIXED code para sa non-buggy inputs:
    - Observe: `create_pppoe_user()` ay gumagana nang tama sa unfixed code
    - Observe: `delete_pppoe_user()` ay gumagana nang tama sa unfixed code
    - Observe: `get_active_pppoe_users()` ay gumagana nang tama sa unfixed code
    - Observe: `disconnect_pppoe_session()` ay gumagana nang tama sa unfixed code
    - Observe: `get_session_bandwidth()` ay gumagana nang tama sa unfixed code
  - Gumawa ng property-based tests na kumukuha ng observed behavior patterns mula sa Preservation Requirements:
    - Test 2a: User Creation Preservation - Para sa lahat ng valid user data, ang `create_pppoe_user()` ay dapat gumana tulad ng dati
    - Test 2b: User Deletion Preservation - Para sa lahat ng existing users, ang `delete_pppoe_user()` ay dapat gumana tulad ng dati
    - Test 2c: Session Retrieval Preservation - Ang `get_active_pppoe_users()` ay dapat magbalik ng parehong data tulad ng dati
    - Test 2d: Disconnection Preservation - Para sa lahat ng active sessions, ang `disconnect_pppoe_session()` ay dapat gumana tulad ng dati
  - Ang property-based testing ay bumubuo ng maraming test cases para sa mas malakas na garantiya
  - Patakbuhin ang mga test sa UNFIXED code
  - **INAASAHANG RESULTA**: Ang mga test ay PUMASA (ito ay nagkukumpirma ng baseline behavior na dapat panatilihin)
  - Markahan ang task bilang complete kapag ang mga test ay nakasulat, napatakbo, at pumapasa sa unfixed code
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_

- [x] 3. Fix para sa Bandwidth Limit Profile Change Bug

  - [x] 3.1 I-implement ang connection retry logic sa `connect()` method
    - Magdagdag ng `max_retries` parameter (default: 3)
    - Magdagdag ng `retry_delay` parameter (default: 2 seconds)
    - I-implement ang retry loop na may exponential backoff
    - I-log ang bawat retry attempt na may detalye
    - Pagbutihin ang error messages para sa connection failures
    - Idagdag ang connection validation pagkatapos ng establishment
    - _Bug_Condition: connectionFails(input.host, input.credentials) OR connectionTimesOut(input.host, input.port)_
    - _Expected_Behavior: Ang fixed `connect()` method ay dapat successfully mag-establish ng API connection sa loob ng retry limit_
    - _Preservation: Ang context manager behavior (`__enter__` at `__exit__`) ay dapat manatiling hindi nagbabago_
    - _Requirements: 2.1, 2.2_

  - [x] 3.2 Gumawa ng bagong `get_ppp_profiles()` method
    - I-query ang Mikrotik para sa available PPP profiles mula sa `/ppp/profile`
    - Ibalik ang list ng profile dictionaries na may name at rate-limit information
    - Idagdag ang error handling para sa API failures
    - Idagdag ang logging para sa profile discovery
    - _Bug_Condition: Walang paraan para malaman ang available profiles bago mag-assign_
    - _Expected_Behavior: Ang method ay dapat magbalik ng complete list ng available profiles_
    - _Preservation: Walang existing functionality na apektado dahil ito ay bagong method_
    - _Requirements: 2.5_

  - [x] 3.3 Gumawa ng bagong `find_matching_profile()` method
    - I-implement ang flexible matching algorithm para sa profile names
    - Suportahan ang multiple naming conventions: "XMBPS", "XMbps", "XM", "Xmbps", "X_MBPS"
    - I-implement ang case-insensitive matching
    - I-parse ang profile rate-limit strings para makuha ang actual speeds
    - I-match base sa download speed primarily, isaalang-alang ang upload speed kung specified
    - Ibalik ang matching profile name, o None kung walang match
    - Idagdag ang logging para sa matching process
    - _Bug_Condition: constructedProfileName(input.download_bps) NOT IN availableProfiles()_
    - _Expected_Behavior: Ang method ay dapat makahanap ng matching profile gamit ang flexible matching_
    - _Preservation: Walang existing functionality na apektado dahil ito ay bagong method_
    - _Requirements: 2.6_

  - [x] 3.4 I-update ang `set_bandwidth_limit()` method para gumamit ng profile discovery
    - Tawagan ang `get_ppp_profiles()` bago mag-construct ng profile name
    - Tawagan ang `find_matching_profile()` para makuha ang actual profile name
    - Kung walang match, mag-raise ng ValueError na may listahan ng available profiles
    - Pagbutihin ang error messages na may actionable feedback
    - Idagdag ang logging para sa profile assignment process
    - Panatilihin ang existing error handling para sa non-existent users
    - _Bug_Condition: isBugCondition(input) kung saan ang input ay BandwidthLimitRequest_
    - _Expected_Behavior: Ang method ay dapat successfully mag-assign ng matching profile_
    - _Preservation: Ang error handling para sa non-existent users ay dapat manatiling ValueError_
    - _Requirements: 2.5, 2.6, 2.7, 2.8, 2.9, 3.1, 3.3_

  - [x] 3.5 I-verify na ang bug condition exploration test ay pumasa na
    - **Property 1: Expected Behavior** - API Connection at Profile Matching Success
    - **IMPORTANTE**: I-rerun ang PAREHONG test mula sa task 1 - HUWAG gumawa ng bagong test
    - Ang test mula sa task 1 ay nag-encode ng expected behavior
    - Kapag ang test na ito ay pumasa, kinukumpirma nito na ang expected behavior ay nasiyahan
    - Patakbuhin ang bug condition exploration test mula sa step 1
    - **INAASAHANG RESULTA**: Ang test ay PUMASA (kinukumpirma na ang bug ay na-fix)
    - _Requirements: 2.1, 2.2, 2.5, 2.6, 2.7, 2.8, 2.9_

  - [x] 3.6 I-verify na ang preservation tests ay pumapasa pa rin
    - **Property 2: Preservation** - Existing Mikrotik Operations
    - **IMPORTANTE**: I-rerun ang PAREHONG tests mula sa task 2 - HUWAG gumawa ng bagong tests
    - Patakbuhin ang preservation property tests mula sa step 2
    - **INAASAHANG RESULTA**: Ang mga test ay PUMASA (kinukumpirma na walang regressions)
    - Kumpirmahin na lahat ng tests ay pumapasa pa rin pagkatapos ng fix (walang regressions)

- [x] 4. Checkpoint - Siguraduhing lahat ng tests ay pumapasa
  - Siguraduhing lahat ng tests ay pumapasa, magtanong sa user kung may mga katanungan
