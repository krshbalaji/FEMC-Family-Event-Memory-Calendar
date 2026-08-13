# FEMC Implementation Vertical Slice

## Objective

Design the minimum end-to-end FEMC vertical slice that proves the architecture in runtime using the existing constitutional and architectural foundation.

This plan preserves the current architecture, avoids new packs, and keeps the implementation scope minimal while validating:

- identity and family context
- canonical event creation and calendar projection
- memory capture and search/retrieval
- privacy and authorization boundaries
- persistence of canonical family information
- API/presentation contract without detailed UI or infrastructure speculation

## 1. Current implementation scaffolding

### What exists

- The repository contains only architecture, engineering, privacy, identity, calendar, events, memory, and data governance documentation.
- Key implementation-oriented documents include:
  - `ARCHITECTURE/091-IMPLEMENTATION-TOPOLOGY/IMPLEMENTATION_TOPOLOGY.md`
  - `ARCHITECTURE/073-LOGICAL-SYSTEM-MODEL/LOGICAL_SYSTEM_MODEL.md`
  - `ARCHITECTURE/075-TRUST-BOUNDARY-MODEL/TRUST_BOUNDARY_MODEL.md`
  - `ARCHITECTURE/079-API-CONTRACT-ARCHITECTURE/API_CONTRACT_ARCHITECTURE.md`
  - `ENGINEERING/007-API-AND-INTEGRATION-IMPLEMENTATION/API_IMPLEMENTATION_GUIDELINES.md`
  - Domain models in `IDENTITY`, `EVENTS`, `CALENDAR`, `MEMORY`, `PRIVACY`, `DATA`, and `ARCHITECTURE/074-FAMILY-DATA-MODEL/`

### What does not exist

- No production source code files (`.py`, `.ts`, `.js`, etc.)
- No executable schema files or schema definitions (`.json`, `.yaml`, `.yml`, etc.)
- No test code files or test framework artifacts
- No build/system configuration files for implementation

The current scaffold is therefore architectural documentation, not code.

## 2. Existing source/schema/test structure

- Source: none present
- Schema: none present as executable artifacts; only conceptual schema guidance in documentation
- Tests: none present in repository

## 3. Constitutional/domain models ready for implementation

### Identity

- `IDENTITY/002-FAMILY-IDENTITY-AND-RELATIONSHIPS/FAMILY_PERSON_AND_ACCOUNT_MODEL.md`
- `IDENTITY/004-IDENTITY-AUTHENTICATION-AND-RECOVERY/IDENTITY_AUTHENTICATION_ARCHITECTURE.md`
- `IDENTITY/004-IDENTITY-AUTHENTICATION-AND-RECOVERY/IDENTITY_SESSION_AND_DEVICE_CONTEXT.md`
- `PRIVACY/004-IDENTITY-CONSENT-AND-FAMILY-CONTEXT/IDENTITY_CONTEXT_AND_PRIVACY.md`

### Event

- `EVENTS/002-FAMILY-EVENTS-AND-TIME/FAMILY_EVENT_MODEL.md`
- `EVENTS/004-EVENTS-CALENDAR-AND-SCHEDULING/EVENTS_CALENDAR_PROJECTION_MODEL.md`
- `EVENTS/004-EVENTS-CALENDAR-AND-SCHEDULING/EVENTS_SCHEDULING_COORDINATION_MODEL.md`

### Calendar

- `CALENDAR/002-FAMILY-CALENDAR-AND-VIEWS/FAMILY_CALENDAR_MODEL.md`
- `CALENDAR/004-CALENDAR-SCHEDULING-AND-COORDINATION/CALENDAR_SCHEDULING_COORDINATION_MODEL.md`
- `CALENDAR/002-FAMILY-CALENDAR-AND-VIEWS/CALENDAR_VIEW_AND_PROJECTION_MODEL.md`

### Memory

- `MEMORY/005-MEMORY-SEARCH-STORYTELLING-AND-LEGACY/MEMORY_SEARCH_ARCHITECTURE.md`
- `ARCHITECTURE/085-FAMILY-TIMELINE-AND-MEMORY-GRAPH/MEMORY_GRAPH_ARCHITECTURE.md`
- `ARCHITECTURE/074-FAMILY-DATA-MODEL/FAMILY_DATA_MODEL_PRINCIPLES.md`

### Privacy/Consent

- `PRIVACY/004-IDENTITY-CONSENT-AND-FAMILY-CONTEXT/CONSENT_AND_USER_CONTROL_MODEL.md`
- `PRIVACY/002-FAMILY-PRIVACY-AND-CONSENT/FAMILY_VISIBILITY_AND_PRIVACY_BOUNDARIES.md`
- `PRIVACY/004-IDENTITY-CONSENT-AND-FAMILY-CONTEXT/FAMILY_CONTEXT_PRIVACY_RULES.md`

### Persistence

- `DATA/002-CANONICAL-FAMILY-DATA-GOVERNANCE/DATA_DEFINITION_AND_SEMANTIC_STANDARDS.md`
- `DATA/004-DATA-ACCESS-AND-SHARING/DATA_ACCESS_CONTROL_MODEL.md`
- `DATA/003-DATA-LIFECYCLE-AND-ASSURANCE/DATA_ASSURANCE_GATE.md`
- `ARCHITECTURE/074-FAMILY-DATA-MODEL/TEMPORAL_AND_HISTORY_MODEL.md`

### Retrieval

- `ARCHITECTURE/083-SEARCH-DISCOVERY-ARCHITECTURE/SEARCH_AUTHORIZATION_ARCHITECTURE.md`
- `MEMORY/005-MEMORY-SEARCH-STORYTELLING-AND-LEGACY/MEMORY_SEARCH_ARCHITECTURE.md`
- `ARCHITECTURE/074-FAMILY-DATA-MODEL/PROVENANCE_AND_CONFIDENCE_MODEL.md`

### Presentation

- `ARCHITECTURE/079-API-CONTRACT-ARCHITECTURE/API_CONTRACT_ARCHITECTURE.md`
- `ENGINEERING/007-API-AND-INTEGRATION-IMPLEMENTATION/API_IMPLEMENTATION_GUIDELINES.md`
- `ENGINEERING/013-FAMILY-EXPERIENCE-IMPLEMENTATION/FAMILY_CONTEXT_AND_NAVIGATION.md`

## 4. Minimum dependencies

The vertical slice should minimize dependencies by remaining within a single implementation boundary and avoiding new cross-domain features.

### Identity

- Authentication/session management
- Account vs person separation
- Family context resolution
- Manual or low-risk identity matching

### Event

- Canonical event model
- Time context and status transitions
- Event persistence as canonical domain state

### Calendar

- Calendar projection from canonical events
- View filtering by family context and authorization
- Multiple calendar contexts without duplicating events

### Memory

- Canonical memory capture and linking to events/people
- Memory metadata, provenance, and confidence
- Basic memory search and retrieval

### Privacy/Consent

- Visibility levels and consent model
- Authorization evaluation by identity, family context, purpose, and resource
- Privacy filtering for calendar, event, and memory results

### Persistence

- Canonical family data store for domain entities
- Derived retrieval/index store for search and calendar views
- Provenance and lifecycle tracking for updates and corrections

### Retrieval

- Authorized query execution
- Search result filtering by effective access
- Authorization-aware retrieval of calendar and memory records

### Presentation

- Minimal API contract layer exposing domain capabilities
- Simple UI/consumer boundary for authenticated requests
- Separation of canonical domain output and derived display data

## 5. Smallest demonstrable end-to-end user journey

### Journey title

**Authenticated family member creates a family event, views it on a calendar, adds an associated memory, and then discovers it by authorized search.**

### Steps

1. User authenticates and establishes an authenticated session.
2. The system resolves the user’s family context and authorization scope.
3. User creates a canonical family event with title, time, participants, and visibility.
4. The calendar service projects the event into the appropriate family calendar view(s).
5. User creates or links a memory/story associated with the event.
6. User searches for the event or memory within their authorized family context.
7. The retrieval layer honors privacy/visibility and returns only authorized results.

This journey proves identity, event/calendar, memory, privacy, persistence, retrieval, and presentation in a single vertical slice.

## 6. Required domain models

### Core domain entities

- Person
- FamilyContext
- Relationship
- Event
- TimeContext
- Memory
- Consent
- AccessPolicy
- Provenance

### Supporting domain artifacts

- CalendarView
- SearchResult
- AuthenticatedSession
- VisibilityLevel
- DerivedIndexEntry
- Confidence/Provenance metadata

## 7. Required schemas

### Conceptual schemas

- Identity schema: person, account, session, family context, relationship context
- Event schema: event details, time contexts, recurrence, participants, status, provenance
- Calendar schema: calendar context, view type, event projection metadata
- Memory schema: memory record, linked event, linked persons, provenance, confidence
- Privacy schema: consent choice, visibility level, access policy, purpose
- Retrieval schema: search query, authorization context, result filtering, facets
- Presentation schema: API response shapes for event, calendar, memory, and search

### Notes

- No executable schema files exist in the repo; these schemas are conceptual and should be derived from the documented domain model.
- The implementation slice should keep schemas small and explicit, with canonical data shape separated from derived shapes.

## 8. Service boundaries

### Domain services

- Identity Service
- Family Context Service
- Event Service
- Calendar Service
- Memory Service
- Search/Retrieval Service

### Cross-cutting services

- Authorization/Privacy Service
- Data Access Control Service
- API/Presentation Gateway
- Provenance/Lifecycle Service

### Boundary rules

- Each service owns coherent canonical state.
- Derived data, indexes, and caches remain outside canonical ownership.
- Authorization decisions are explicit at every service boundary.
- External providers stay behind integration boundaries.

## 9. Persistence boundary

### Canonical persistence

- Persist Person, FamilyContext, Relationship, Event, Memory, Consent, and Audit/Provenance records in the canonical store.

### Derived persistence

- Persist search indexes, calendar projections, and materialized views separately from canonical data.

### Boundary enforcement

- Derived stores must enforce the same effective authorization boundary.
- Corrections and updates must maintain provenance and not silently lose previous history.

## 10. Privacy boundary

### Authorization path

- Identity → Family Context → Resource → Purpose → Authorization → Data Access

### Requirements

- Privacy policy must be applied before data reaches presentation.
- Search, calendar views, and memory retrieval must not expose unauthorized records.
- Consent decisions must be explicit, changeable, and visible to the user.

### Visibility model

- private
- person-specific
- household
- selected family
- family-wide
- externally shareable

### Principle

Visibility belongs to family meaning, not to the implementation.

## 11. Minimum UI/API boundary

### API contract surface

- `POST /auth/login` or equivalent session creation
- `GET /family/context`
- `POST /events`
- `GET /events/{id}`
- `GET /calendars/{context}`
- `POST /memories`
- `GET /memories/{id}`
- `GET /search?q=...`

### UI boundary

- Simple authenticated family dashboard
- Calendar list or monthly view with event cards
- Event detail screen
- Memory/story detail screen
- Search box and authorized result list

### API rules

- Validate inputs
- Enforce authorization server-side
- Return only authorized data
- Keep canonical vs derived outputs distinguishable

## 12. Test cases

### Identity and authorization

- authenticated user can create and access events within their family context
- unauthorized user cannot access another family’s events or memories
- session resolution preserves person/account separation

### Event/calendar

- event creation stores canonical event data
- calendar view returns authorized event projections
- an event can appear in multiple calendar contexts without duplicating canonical state

### Memory/retrieval

- memory creation is linked to event/family context
- search returns only authorized event and memory results
- privacy boundary filters search and calendar payloads

### Privacy/consent

- visibility levels restrict access as defined
- consent change affects subsequent retrieval results
- search does not leak hidden information in snippets

### Persistence and provenance

- canonical store contains primary domain records
- derived views/indexes do not bypass authorization
- provenance metadata is attached to created records

## 13. Implementation order

1. Identity and family context resolution
2. Canonical domain model persistence for Person, FamilyContext, Relationship, Event, Memory
3. Event creation and basic calendar projection
4. Memory capture and event-memory linking
5. Search/retrieval with authorization and privacy filtering
6. API contract implementation for the minimal surface
7. Privacy/consent enforcement across all exposures
8. Provenance, lifecycle, and audit support
9. Basic UI/presentation boundary for authenticated journeys

## 14. Explicit non-goals

- No AI inference or generative assistant behavior in this slice
- No full media upload, processing, or media-service implementation
- No external provider integration beyond the established integration boundary
- No broad search discovery beyond the family-authorized scope
- No architecture redesign or new constitutional decisions
- No creation of new architecture packs
- No code implementation in this audit phase
- No unnecessary frameworks or infrastructure speculation

## 15. Conclusion

The smallest runtime vertical slice is an authenticated family member workflow covering event creation, calendar projection, memory capture, and authorized search within the existing family privacy and trust architecture.

This slice proves the core architecture with minimal scope and preserves the current architectural and constitutional decisions.