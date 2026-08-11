# FEMC Extension Engineering Model

**Version:** 1.0.0
**Status:** Engineering Design
**Owner:** Engineering Office

## Extension Boundary

```text
FEMC CONTRACT
     ↓
EXTENSION ADAPTER
     ↓
EXTERNAL CAPABILITY
```

## Requirements

Extensions must have:

- explicit identity;
- bounded permissions;
- scoped data access;
- failure isolation;
- lifecycle state;
- revocation;
- compatibility rules.

## Rules

An extension cannot directly become the canonical owner of family information.

## Principle

Extensions expand FEMC without becoming dependencies that FEMC cannot survive.
