# FEMC Identity Lifecycle Model

**Version:** 1.0.0
**Status:** Identity Architecture
**Owner:** Identity Office

## Lifecycle

```text
DISCOVER / CREATE
 ↓
VERIFY / LINK
 ↓
ACTIVE
 ↓
UPDATE
 ↓
SUSPEND / INACTIVE
 ↓
RECOVER / REACTIVATE
 ↓
CLOSE / PRESERVE
```

## Requirements

Lifecycle behavior should distinguish:

- account state;
- person representation;
- family membership;
- authentication credentials;
- historical family records.

## Principle

Closing an account must not silently erase the person's historical place in family memory.
