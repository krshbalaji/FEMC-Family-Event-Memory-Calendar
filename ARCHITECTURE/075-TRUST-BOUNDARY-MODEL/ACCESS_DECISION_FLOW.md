# FEMC Access Decision Flow

**Version:** 1.0.0
**Status:** Architecture
**Owner:** Architecture Office

## Decision Flow

```text
REQUEST
  ↓
IDENTITY CONFIDENCE
  ↓
FAMILY CONTEXT
  ↓
RESOURCE
  ↓
PURPOSE / ACTION
  ↓
CONSENT + POLICY
  ↓
AUTHORIZATION
  ↓
ALLOW / DENY / REQUIRE CONFIRMATION
```

## Rules

1. Identity is established before sensitive access.
2. Family context is evaluated.
3. The requested resource is identified.
4. Requested action is evaluated.
5. Consent and policy are checked.
6. Authorization is decided.
7. Material actions may require confirmation.

## Failure

When authorization cannot be established confidently, the system should prefer privacy-preserving behavior.

## Principle

Being related to someone does not automatically authorize access to everything about them.
