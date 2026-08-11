# FEMC Dependency Failure and Fallback Operations

**Version:** 1.0.0
**Status:** Operations
**Owner:** Operations Office

## Failure Flow

```text
DETECT
 ↓
CLASSIFY
 ↓
ISOLATE
 ↓
DEGRADE / FALLBACK
 ↓
PROTECT CANONICAL DATA
 ↓
RECOVER
 ↓
VERIFY
```

## Rules

- Do not fabricate successful external actions.
- Do not repeatedly retry unsafe side effects.
- Preserve user intent when safe.
- Clearly distinguish unavailable from completed.
- Restore derived services after core family access is trusted.

## Principle

Graceful degradation means preserving truth and trust when capability is temporarily unavailable.
