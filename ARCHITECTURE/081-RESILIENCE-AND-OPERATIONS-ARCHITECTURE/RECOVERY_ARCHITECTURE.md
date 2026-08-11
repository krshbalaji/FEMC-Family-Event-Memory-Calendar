# FEMC Recovery Architecture

**Version:** 1.0.0
**Status:** Architecture
**Owner:** Architecture Office

## Recovery Domains

Consider recovery independently for:

- canonical data;
- identity and access;
- application services;
- media;
- search indexes;
- AI-derived data;
- external integrations.

## Recovery Order

```text
TRUST + IDENTITY
      ↓
CANONICAL DATA
      ↓
CORE APPLICATION
      ↓
MEDIA
      ↓
DERIVED SYSTEMS
      ↓
AI / OPTIONAL SERVICES
```

## Principle

Recover the source of truth before rebuilding convenience layers.
