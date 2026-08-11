# FEMC Architecture Responsibility and Boundaries

**Version:** 1.0.0
**Status:** Architecture Foundation
**Owner:** Architecture Office

## Architecture Decisions

Architecture determines:

- boundaries;
- ownership;
- dependencies;
- information flow;
- integration contracts;
- resilience patterns;
- evolution constraints.

## Architecture Must Coordinate With

```text
CONSTITUTION
    ↓
PRODUCT
    ↓
ARCHITECTURE
    ↓
ENGINEERING
    ↓
OPERATIONS
```

Security, Privacy, AI, and Governance participate whenever their domains are materially affected.

## Principle

Architecture owns coherence, not implementation authority.
