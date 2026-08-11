# FEMC Identity and Access Model

**Version:** 1.0.0
**Status:** Security Architecture
**Owner:** Security Office

## Core Distinctions

```text
IDENTITY
  ≠
AUTHENTICATION
  ≠
AUTHORIZATION
  ≠
RELATIONSHIP
```

A person's family relationship does not automatically determine every permission.

## Requirements

Access decisions should consider:

- authenticated identity;
- family context;
- resource;
- action;
- policy;
- current authorization;
- revocation state.

## Principle

Identity establishes who is acting; authorization determines what that person may do.
