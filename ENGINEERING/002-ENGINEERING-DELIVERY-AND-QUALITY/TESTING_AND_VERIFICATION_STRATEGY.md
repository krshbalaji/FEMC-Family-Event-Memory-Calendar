# FEMC Testing and Verification Strategy

**Version:** 1.0.0
**Status:** Engineering Quality
**Owner:** Engineering Office

## Test Layers

```text
UNIT
 ↓
COMPONENT
 ↓
CONTRACT
 ↓
INTEGRATION
 ↓
SYSTEM
 ↓
END-TO-END
 ↓
RECOVERY / FAILURE
```

## Priority

Higher testing depth is required where changes affect:

- canonical family data;
- authorization;
- privacy;
- security;
- AI tools;
- media;
- sharing;
- deletion;
- migration;
- financial or irreversible actions.

## Principle

The required evidence rises with the consequence of failure.
