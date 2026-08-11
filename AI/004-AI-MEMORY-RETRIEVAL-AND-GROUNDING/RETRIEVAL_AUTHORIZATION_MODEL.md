# FEMC Retrieval Authorization Model

**Version:** 1.0.0
**Status:** AI Architecture
**Owner:** AI Office

## Retrieval Decision

```text
WHO
 ↓
WHICH FAMILY CONTEXT
 ↓
WHICH RESOURCE
 ↓
WHICH ACTION
 ↓
WHICH PURPOSE
 ↓
ALLOW / DENY
```

## Rules

Authorization must be enforced before protected family information enters an AI context.

Search indexes, embeddings, caches, summaries, and derived representations must respect the same effective access boundary.

## Principle

AI retrieval cannot be more privileged than the user or service invoking it.
