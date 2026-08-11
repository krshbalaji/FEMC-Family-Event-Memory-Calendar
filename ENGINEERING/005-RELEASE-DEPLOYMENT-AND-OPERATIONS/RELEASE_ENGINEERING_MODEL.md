# FEMC Release Engineering Model

**Version:** 1.0.0
**Status:** Engineering Delivery
**Owner:** Engineering Office

## Release Flow

```text
VERIFIED CHANGE
 ↓
RELEASE CANDIDATE
 ↓
RELEASE VALIDATION
 ↓
APPROVAL
 ↓
DEPLOY
 ↓
VERIFY
 ↓
OBSERVE
```

## Requirements

Every material release should identify:

- source revision;
- included changes;
- verification evidence;
- deployment method;
- rollback/recovery approach;
- responsible owner.

## Principle

A release is a controlled transition from one trusted state to another.
