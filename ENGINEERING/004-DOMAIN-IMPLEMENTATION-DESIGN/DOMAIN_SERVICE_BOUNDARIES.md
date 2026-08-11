# FEMC Domain Service Boundaries

**Version:** 1.0.0
**Status:** Engineering Design
**Owner:** Engineering Office

## Boundary Rule

A domain service should own a coherent business responsibility rather than a convenient technical grouping.

## Examples

```text
Family Context
People & Relationships
Events & Time
Memory & Media
Communication
Legacy
```

Cross-cutting capabilities such as authorization, audit, search, and AI interact with these boundaries through explicit contracts.

## Rules

- Avoid circular ownership.
- Avoid duplicate canonical state.
- Keep transactional responsibilities clear.
- Keep derived processing outside canonical ownership where possible.
- Prefer explicit interfaces between material responsibilities.

## Principle

A service boundary should answer “who owns this meaning?” clearly.
