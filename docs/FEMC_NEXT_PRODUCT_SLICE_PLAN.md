# FEMC Next Product Slice Plan

## 1. What a real family member can do TODAY

With the current runtime implementation and approved first user experience, a family member can:
- authenticate and establish a session
- resolve their family context
- create a canonical family event within that context
- view the event in a family calendar projection
- retrieve a canonical event by its identifier
- attach a memory to a specific event
- retrieve that memory by its identifier
- search authorized events and memories with simple text matching
- rely on privacy-aware authorization to block unauthorized access

This provides a minimal end-to-end family event and memory creation experience.

## 2. What core user capability is still missing

The implementation does not yet deliver the expected event-centered memory discovery experience.
Specifically, a family member cannot reliably view the memories attached to an event as part of the event detail flow.

While memory creation is supported, the current runtime lacks an explicit event-to-memory retrieval path and event detail response shape that aggregates attached memories.

## 3. Which missing capability provides the highest product value

The highest product value is:
- event detail retrieval with attached memory listings

This delivers the core family use case of seeing the story behind a shared event, not just creating it.
It closes the gap between canonical event capture and the authored memory narrative that makes the experience meaningful.

## 4. The smallest next vertical slice that adds that capability

Build the next vertical slice around:
- retrieving an event together with its associated memories for the current authorized session
- exposing this as a single API/experience endpoint
- preserving existing privacy rules for both event and memory access

This slice should include:
- event detail response enriched with attached memory summaries
- a service call that lists memories for a given event and session
- a minimal acceptance test covering authorized event-memory discovery
- a denial path for unauthorized users attempting to view event memories

## 5. What existing runtime components can be reused

Reuse these runtime components without new architectural scope:
- `FEMCApi` façade
- `IdentityService` / session validation logic
- `EventService` canonical event retrieval
- `MemoryService` canonical memory listing and authorization
- `AuthorizationService` privacy checks
- `CanonicalRepository` event/memory storage
- `DerivedRepository` if search/calendar projection remains relevant
- existing domain models: `Event`, `Memory`, `FamilyContext`, `AuthenticatedSession`, `VisibilityLevel`, `ProvenanceMetadata`

## 6. Minimum new code/models/tests required

### Code
- extend `MemoryService` with a method to list memories by event ID and account authorization
- extend `EventService` or `FEMCApi` to return event detail plus associated memory summaries for a validated session
- add a small response model or DTO for `EventWithMemories` if needed

### Models
- likely no new canonical domain models are required
- one small derived response model for event detail with attached memory list may be enough

### Tests
- end-to-end test covering:
  - create event
  - attach memory to event
  - retrieve event detail with attached memories via authorized session
- regression test covering unauthorized access to event-attached memories
- privacy test verifying that event detail for a private event does not expose memories to unauthorized sessions

## 7. Explicit non-goals

This next slice does not include:
- family member invitation, RSVP, or participant management flows
- event editing, deletion, or complex scheduling coordination
- rich media storage or attachment handling
- AI-generated memories, summaries, or recommendations
- social feeds, comments, or community features
- third-party integrations, notifications, or payments
- production infrastructure, deployment, or observability platforms
- rearchitecting existing domains or adding new architecture packs

## 8. Acceptance criteria

1. An authenticated family member can request event detail by session and event ID.
2. The response includes the event data plus a list of memories attached to that event.
3. Only memories authorized for the session owner are returned.
4. Memory creation remains possible and is still linked to the event.
5. Unauthorized sessions cannot retrieve event-attached memories.
6. The existing calendar projection and event authorization behavior remain unchanged.
7. No new privacy or domain model boundaries are introduced beyond the current slice.
8. The slice is verified by runtime tests and acceptance tests only.

## Recommendation

NEXT SLICE = event detail with attached memory discovery
