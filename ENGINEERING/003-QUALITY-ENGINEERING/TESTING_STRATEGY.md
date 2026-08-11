# FEMC Testing Strategy

**Version:** 1.0.0
**Status:** Engineering Foundation

## Test Layers

```text
UNIT
 ↓
COMPONENT
 ↓
CONTRACT
 ↓
INTEGRATION
 ↓
SYSTEM
 ↓
FAMILY JOURNEY
 ↓
PRODUCTION READINESS
```

## Priority

High-risk areas receive deeper validation:

- authorization;
- family isolation;
- canonical data integrity;
- migration;
- media handling;
- AI boundaries;
- external integrations;
- recovery;
- sharing.

## Representative Journeys

Tests should include connected flows such as:

Event → Participants → Media → Memory → Sharing → Legacy.

## Principle

Testing should validate the system people depend on, not only the functions engineers wrote.
