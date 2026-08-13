# FEMC Vertical Slice Implementation Specification

**Version:** 1.0.0
**Status:** Implementation Specification
**Owner:** Architecture Office

## Purpose

Provide the smallest concrete implementation specification required to deliver the approved FEMC vertical slice without changing the existing architecture, introducing new packs, or presuming an implementation technology stack.

This specification translates the approved vertical slice into:
- canonical domain entity definitions,
- minimal derived/primary store boundaries,
- authorization and privacy enforcement points,
- API contract surface,
- acceptance criteria for end-to-end verification.

## Scope

### In scope
- canonical Person + FamilyContext + Relationship identity model
- Authenticated session scope for a participant
- canonical Event creation with minimal calendar semantics
- calendar projection of owned/visible events
- canonical Memory attachment to an Event
- consented visibility and authorization rules for Person/Event/Memory access
- first-record provenance metadata for canonical archives
- authorized search and retrieval of Events and Memories
- minimal API contract and verification harness

### Out of scope
- multi-family federation
- media management or rich attachments
- AI assistance, summarization, or recommendation
- bulk import/export pipelines
- external integration with financial, health, or third-party services
- advanced policy engines beyond direct consent and visibility rules

## Context

The repository is currently documentation-only and contains no executable source, schema, or test artifacts. This spec is intentionally concrete enough to enable a runtime implementation in a future repository or module without requiring architecture changes in FEMC.

Key architecture source documents:
- `ARCHITECTURE/079-API-CONTRACT-ARCHITECTURE/API_CONTRACT_ARCHITECTURE.md`
- `ARCHITECTURE/074-FAMILY-DATA-MODEL/PROVENANCE_AND_CONFIDENCE_MODEL.md`
- `ARCHITECTURE/083-SEARCH-DISCOVERY-ARCHITECTURE/SEARCH_AUTHORIZATION_ARCHITECTURE.md`
- `PRIVACY/002-FAMILY-PRIVACY-AND-CONSENT/FAMILY_VISIBILITY_AND_PRIVACY_BOUNDARIES.md`
- `IDENTITY/002-FAMILY-IDENTITY-AND-RELATIONSHIPS/FAMILY_PERSON_AND_ACCOUNT_MODEL.md`
- `EVENTS/002-FAMILY-EVENTS-AND-TIME/FAMILY_EVENT_MODEL.md`
- `CALENDAR/002-FAMILY-CALENDAR-AND-VIEWS/FAMILY_CALENDAR_MODEL.md`
- `MEMORY/005-MEMORY-SEARCH-STORYTELLING-AND-LEGACY/MEMORY_SEARCH_ARCHITECTURE.md`

## Implementation Goals

1. Validate canonical family identity and relationship boundaries.
2. Enable event capture and calendar projection under family context.
3. Capture memories linked to events while preserving provenance.
4. Enforce visibility and authorization across calendar, event, memory, and search.
5. Keep canonical data authoritative and derived views distinct.
6. Expose a minimal API contract for authenticated clients.
7. Provide a verification path for an end-to-end user journey.

## Concrete Domain Model Definitions

### 1. Identity and Family Context

#### Person
A persistent individual record representing a person in family history.

Fields:
- `personId` (string, stable canonical identifier)
- `name` (string)
- `birthDate` (date or partial date)
- `status` (`active` | `inactive` | `deceased`)
- `relationships` (list of `Relationship` references)
- `canonicalSource` (metadata reference)

#### FamilyContext
A resolved set of family relationships, memberships, and contextual boundaries for a participant.

Fields:
- `familyId` (string)
- `contextOwnerPersonId` (string) - person through whom the context is evaluated
- `memberPersonIds` (list of string)
- `relationshipGraph` (optional minimal graph metadata)
- `visibilityDefaults` (struct describing default visibility levels)

#### Relationship
A directional connection between persons that supports family context and event participation.

Fields:
- `relationshipId` (string)
- `fromPersonId` (string)
- `toPersonId` (string)
- `relationshipType` (`parent` | `child` | `spouse` | `sibling` | `chosen` | `other`)
- `status` (`confirmed` | `disputed` | `historical`)
- `canonicalSource`

#### Account vs AuthenticatedSession
An account represents participation in FEMC; the authenticated session is a transient runtime credential.

**Account**
- `accountId` (string)
- `personId` (string)
- `accountStatus` (`enabled` | `disabled`)
- `roles` (list of string)
- `createdAt`

**AuthenticatedSession**
- `sessionId` (string)
- `accountId` (string)
- `personId` (string)
- `issuedAt`
- `expiresAt`
- `deviceContext` (optional trust/risk metadata)
- `authorizationScope` (scope or purpose metadata)

### 2. Event
A canonical event is the source of truth for family time, participants, and visibility.

Fields:
- `eventId` (string)
- `title` (string)
- `description` (string)
- `startTime` (timestamp)
- `endTime` (timestamp)
- `timeZone` (string)
- `participants` (list of `personId`)
- `organizerPersonId` (string)
- `familyContextId` (string)
- `visibility` (`private` | `person-specific` | `household` | `selected-family` | `family-wide`)
- `status` (`planned` | `confirmed` | `completed` | `cancelled`)
- `provenance` (`ProvenanceMetadata`)
- `createdBy` (`personId`)
- `createdAt`
- `modifiedAt`

### 3. Calendar Projection
A derived view that presents events filtered by family context and effective authorization.

Projection item fields:
- `calendarViewId` (string)
- `eventId` (string)
- `title`
- `startTime`
- `endTime`
- `timeZone`
- `eventVisibility` (source visibility)
- `participantCount`
- `derivedStatus` (`visible` | `restricted` | `hidden`)
- `canonicalSourceEventId`

The Calendar Service creates projections without mutating canonical event state.

### 4. Memory
A canonical memory record attaches meaning, narrative, or context to an event and to family history.

Fields:
- `memoryId` (string)
- `eventId` (string)
- `authorPersonId` (string)
- `linkedPersonIds` (list of string)
- `summary` (string)
- `details` (string)
- `visibility` (`private` | `person-specific` | `household` | `selected-family` | `family-wide`)
- `provenance` (`ProvenanceMetadata`)
- `confidence` (`confirmed` | `reported` | `approximate` | `disputed` | `unknown`)
- `createdAt`
- `modifiedAt`

Memory is canonical and is only visible according to its own visibility plus any event-level restrictions.

### 5. Consent and Visibility
Consent and visibility control effective access in this vertical slice.

#### VisibilityLevel
- `private`
- `person-specific`
- `household`
- `selected-family`
- `family-wide`

#### Consent record
Fields:
- `consentId` (string)
- `personId` (string)
- `resourceType` (`event` | `memory` | `calendar`)
- `resourceId` (string)
- `purpose` (string)
- `grantedAt`
- `expiresAt` (optional)
- `status` (`active` | `revoked`)

#### AccessPolicy
An effective policy derived from resource visibility, family context, and consent.

Fields:
- `policyId` (string)
- `resourceType`
- `resourceId`
- `effectiveVisibility`
- `authorizedPersonIds` (list)
- `evaluationReason`

Privacy enforcement occurs at two points:
1. Authorization evaluation for any request.
2. Result filtering for derived calendar and search responses.

### 6. Provenance Metadata
Preserve first-record source and authority for all canonical updates.

#### ProvenanceMetadata
Fields:
- `sourceType` (`user-input` | `import` | `migration` | `system-derivation`)
- `sourceId` (string)
- `recordedByPersonId` (string)
- `recordedAt`
- `confidence`
- `changeType` (`create` | `update` | `correct`)
- `isCanonical` (boolean)

Principles:
- Keep provenance with the canonical record.
- Do not treat derived records as canonical unless confirmed.

## Minimal API Contract

This section defines the smallest conceptual API surface needed for the vertical slice. Actual endpoint names and wire formats may vary by implementation.

### 1. Authentication / Session

- `POST /auth/session` - issue session for an authenticated account
- `GET /auth/session/{sessionId}` - retrieve session details and authorization scope

Request/response shapes must include `accountId`, `personId`, `expiresAt`, and effective authorization context.

### 2. Event Operations

- `POST /events`
  - create canonical event
  - request body includes `title`, `description`, `startTime`, `endTime`, `timeZone`, `participants`, `visibility`, `familyContextId`
- `GET /events/{eventId}`
  - retrieve canonical event details if authorized
- `GET /calendar?context={familyContextId}&view={viewType}`
  - return a calendar projection of authorized events

Authorization context must accompany each request.

### 3. Memory Operations

- `POST /memories`
  - create canonical memory linked to an event
  - request body includes `eventId`, `authorPersonId`, `linkedPersonIds`, `summary`, `details`, `visibility`
- `GET /memories/{memoryId}`
  - retrieve memory if authorized

### 4. Search / Retrieval

- `GET /search?query={query}&context={familyContextId}`
  - authorized search across events and memories
  - results include `type`, `id`, `title`, `snippet`, `visibility`, `provenance`

Search must never return information the requester is not authorized to access.

### 5. Authorization / Privacy

- `POST /authorization/evaluate`
  - optionally evaluate effective access for a resource and session

All operations use the same authorization model and evaluate visibility consistently.

## Persistence and Store Boundaries

### Canonical Store
Stores primary domain entities:
- Person
- Relationship
- FamilyContext
- Event
- Memory
- Consent
- AccessPolicy
- ProvenanceMetadata

This store is the source of truth for vertical slice data.

### Derived Store / Projection
Stores read-optimized results for:
- Calendar views
- Search index entries
- authorized result sets

Derived stores are rebuilt or updated from canonical sources and preserve access boundaries.

## Service Boundaries

### Domain services in this slice
- Identity Service
- Family Context Service
- Event Service
- Calendar Projection Service
- Memory Service
- Search/Retrieval Service
- Authorization Service

### Cross-cutting responsibilities
- Privacy enforcement
- Provenance tracking
- Session and request context propagation
- Data quality validation

## End-to-end Vertical Slice Journey

The smallest demonstrable experience is:
1. Authenticate as a person with an account.
2. Resolve the person’s family context.
3. Create a canonical event for that family context.
4. Observe the event in a projected calendar view.
5. Create a canonical memory linked to that event.
6. Search for the event or memory within the authorized family context.
7. Confirm returned results respect visibility and provenance.

## Verification Requirements

### Acceptance criteria
- Authenticated sessions map to a person and account.
- Canonical events persist with required provenance metadata.
- Calendar projections only expose events authorized for the requesting family context.
- Memories linked to events are only retrievable if the requester is authorized.
- Search returns only authorized event and memory results.
- Resource visibility is honored consistently across event retrieval, calendar projection, search, and memory retrieval.
- Canonical data shapes remain distinct from derived projection shapes.

### Minimal test types
- Identity/session resolution tests
- Event create/retrieve/authorization tests
- Calendar projection filtering tests
- Memory create/retrieve/authorization tests
- Search authorization and result filtering tests
- Provenance recording tests

## Implementation Constraints

- Do not introduce new architectural packs.
- Keep the vertical slice small and self-contained within FEMC’s existing domains.
- Preserve canonical family data as the authority and keep projections derived.
- Avoid assumptions about storage technology, UI framework, or runner.
- Keep contract definitions explicit and minimal.

## Notes

- This specification is intentionally implementation-agnostic; it defines structural and behavioral requirements rather than provider details.
- A future implementation may be delivered as a runtime module, service, or microservice set based on this spec.
- The focus is on preserving family meaning, privacy, provenance, and authorization while enabling a real end-to-end verification path.