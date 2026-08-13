# FEMC First User Experience Plan

## Purpose

Define the smallest user-visible FEMC slice that can be built on top of the proven canonical runtime core.
This plan focuses on a lightweight, privacy-aware family event and memory experience without introducing AI, media, or external integration complexity.

## Overview

The first FEMC user experience should enable a family member to:
- enter as an authenticated participant,
- resolve a family context,
- create and view a single family event,
- see the event in a calendar projection,
- attach a memory to the event,
- retrieve the memory with privacy-aware access controls.

This slice reuses the existing canonical runtime components and exposes a minimal presentation/API boundary for a simple client.

## User Journey

1. Family member signs in using account credentials.
2. The system establishes an authenticated session and resolves the participant's family context.
3. The user creates a family event associated with that family context.
4. The event is stored canonically and projected into a calendar view.
5. The user attaches a memory to the created event.
6. The user views the event and attached memory through the calendar or direct event detail view.
7. The system enforces visibility rules so only authorized family participants can see the event or memory.

## Required Screens / API Interactions

### Front-end screens

- Sign-in / session entry screen
- Family context summary screen
- Event creation screen
- Calendar view with event tiles
- Event detail screen with attached memory
- Memory creation form
- Authorization feedback when access is denied

### Minimal API interactions

- `POST /sessions` — create authenticated session for an account
- `GET /family-contexts/{accountId}` — resolve family context for the signed-in member
- `POST /events` — create a canonical family event
- `GET /calendar?familyContextId={id}` — retrieve calendar projection entries for a family context
- `GET /events/{eventId}` — retrieve canonical event details
- `POST /memories` — attach memory to an event
- `GET /memories/{memoryId}` — retrieve memory detail
- `GET /search?q={query}` — authorized search across events and memories (minimal support)

## Reused Runtime Components

- `IdentityService` for person, account, and session management
- `CanonicalRepository` for storing persons, accounts, sessions, events, and memories
- `EventService` for controlled canonical event creation and projection
- `CalendarService` for derived calendar projection retrieval
- `MemoryService` for canonical memory attachment and authorized persistence
- `AuthorizationService` for privacy-aware access decisions
- `SearchService` for minimal authorized retrieval experience
- `FEMCApi` façade as the single runtime entry point

## Minimum New Components

This slice requires only a thin presentation/API layer on top of the current runtime core:

- API surface definitions for session, family context, event, calendar, memory, and search
- a small client experience model or screen flow definition for the above interactions
- request/response shaping for event and memory detail views
- explicit privacy-aware result filtering in the API contract

No new canonical domain models are required.
No new derived store patterns are required beyond current calendar and search projections.
No infrastructure or orchestration components are required.

## Acceptance Criteria

1. A family participant can authenticate and establish a valid session.
2. The runtime resolves a family context for the signed-in participant.
3. The participant can create a canonical event linked to the family context.
4. The event appears in a calendar projection filtered by family context.
5. The participant can attach a memory to the event.
6. The memory is stored canonically and retrievable through the API.
7. Privacy and authorization rules prevent access to events and memories for unauthorized participants.
8. Provenance metadata exists on canonical event and memory records.
9. The experience is exposed through a minimal API contract.
10. No AI, media attachments, social features, external integrations, advanced search, notifications, payments, or full production infrastructure are introduced.

## Tests

### Runtime tests

- identity/session creation and lookup
- family context resolution for a signed-in participant
- authorized event creation within family context
- calendar projection creation and retrieval
- memory attachment to an event
- authorized retrieval of event and memory details
- unauthorized access denial for events and memories
- provenance presence on canonical event and memory records
- minimal search result inclusion for event and memory

### Acceptance tests

- end-to-end journey from session sign-in to event creation, calendar view, memory attachment, and memory retrieval
- privacy boundary confirmation for authorized and unauthorized participants
- API contract validation for the minimal endpoint set

## Explicit Non-Goals

- AI-assisted composition, summarization, or recommendation
- image, audio, video, or rich media attachments
- social networking or community feed features
- external integration with third-party services (finance, health, messaging, calendar providers)
- advanced search beyond simple authorized text matching
- notification delivery, scheduling, or push mechanisms
- payments, billing, subscription, or commerce workflows
- full production-grade infrastructure, deployment, or observability platforms
- full multi-family federation or complex family graph reconciliation

## Summary

This plan defines the smallest user-visible FEMC slice that remains faithful to the confirmed core architecture.
It preserves the runtime's canonical/derived separation, enforces privacy-aware access, and exposes a minimal end-to-end user/API experience for family event and memory management.
