# FEMC Operations Responsibility Model

**Version:** 1.0.0
**Status:** Operations Foundation

## Responsibilities

```text
HEALTH
  ↓
DETECT
  ↓
RESPOND
  ↓
RECOVER
  ↓
VERIFY
  ↓
LEARN
```

Operations is responsible for coordinating this lifecycle.

## Operational Classes

### Normal
Routine monitoring, maintenance, capacity, and release support.

### Degraded
Partial capability loss requiring controlled response.

### Incident
Material impact to availability, integrity, privacy, or security.

### Continuity
Recovery from major infrastructure, dependency, or data failure.

## Principle

Operational responsibility follows system impact, not organizational convenience.
