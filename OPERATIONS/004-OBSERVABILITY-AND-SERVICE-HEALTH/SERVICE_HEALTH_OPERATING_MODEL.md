# FEMC Service Health Operating Model

**Version:** 1.0.0
**Status:** Operations
**Owner:** Operations Office

## Purpose

Operate FEMC using evidence about availability, correctness, performance, integrity, security, and dependency health.

## Health Layers

```text
INFRASTRUCTURE
      ↓
PLATFORM
      ↓
APPLICATION
      ↓
DOMAIN
      ↓
FAMILY JOURNEY
      ↓
TRUST
```

## Rules

- A healthy infrastructure layer does not prove a healthy family journey.
- Canonical data integrity is a first-class health concern.
- Security and privacy failures are operational health failures.
- Derived capability failures should be distinguished from canonical-domain failures.

## Principle

Measure the health families experience, not only the health machines report.
