# FEMC Security Testing Model

**Version:** 1.0.0
**Status:** Engineering Design
**Owner:** Engineering Office

## Test Areas

- authentication;
- authorization;
- family-to-family isolation;
- privilege escalation;
- sharing;
- export;
- revocation;
- injection;
- dependency misuse;
- AI data exposure;
- sensitive error disclosure.

## Priority

Test negative paths aggressively.

Examples:

```text
Valid identity + invalid family access
Valid family access + invalid resource
Valid read + unauthorized write
Revoked access + stale session
Authorized source + unauthorized recipient
```

## Principle

Security testing must prove that forbidden paths remain forbidden.
