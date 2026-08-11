# FEMC Search and Discovery Architecture

**Version:** 1.0.0
**Status:** Architecture
**Owner:** Architecture Office

## Purpose

Enable families to discover people, events, memories, media, and history without making search an alternate source of truth.

## Model

```text
CANONICAL DOMAIN
      │
      ▼
INDEX / RETRIEVAL
      │
 ┌────┼────┐
 ▼    ▼    ▼
TEXT  TIME  SEMANTIC
      │
      ▼
RESULTS
      │
      ▼
AUTHORIZED FAMILY EXPERIENCE
```

## Principles

1. Search results are derived.
2. Authorization applies before results are exposed.
3. Indexes may be rebuilt.
4. Stale indexes must not silently alter canonical information.
5. Search should support connected family context.

## Principle

Search helps families find their history; it does not define their history.
