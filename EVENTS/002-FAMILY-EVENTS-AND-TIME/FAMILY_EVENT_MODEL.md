# FEMC Family Event Model

**Version:** 1.0.0
**Status:** Events Architecture
**Owner:** Events Office

## Event Components

A material event may contain:

- identity;
- title/description;
- start and end;
- time-zone context;
- location;
- participants;
- organizer;
- recurrence;
- status;
- relationships;
- provenance;
- visibility.

## Event States

```text
PLANNED
 ↓
CONFIRMED
 ↓
OCCURRING
 ↓
COMPLETED
```

Other governed states may include cancelled, postponed, tentative, or historical.

## Principle

Event state expresses the family's understanding of the occurrence, not merely the state of a calendar UI.
