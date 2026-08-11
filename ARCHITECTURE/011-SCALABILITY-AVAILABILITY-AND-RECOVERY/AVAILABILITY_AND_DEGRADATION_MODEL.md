# FEMC Availability and Degradation Model

**Version:** 1.0.0
**Status:** Architecture
**Owner:** Architecture Office

## Availability Priorities

Protect, in order appropriate to impact:

1. canonical family data integrity;
2. authorized access;
3. core family experience;
4. supporting capabilities;
5. enhancement capabilities.

## Graceful Degradation

Examples:

```text
AI unavailable
 → core family data remains usable

SEARCH degraded
 → direct family navigation remains available

EXTERNAL PROVIDER unavailable
 → unaffected family capabilities continue
```

## Principle

Not every capability needs to be available for FEMC to remain meaningfully alive.
