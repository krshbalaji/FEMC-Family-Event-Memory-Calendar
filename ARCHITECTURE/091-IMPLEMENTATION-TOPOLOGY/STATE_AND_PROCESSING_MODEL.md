# FEMC State and Processing Model

**Version:** 1.0.0
**Status:** Architecture
**Owner:** Architecture Office

## State Classes

```text
CANONICAL STATE
     ↓
DERIVED STATE
     ↓
EPHEMERAL PROCESSING STATE
```

## Canonical State

Authoritative family information.

## Derived State

Search indexes, analytics models, AI-derived artifacts, thumbnails, caches, and similar rebuildable representations.

## Ephemeral State

Temporary processing information that can be recreated or discarded safely.

## Rules

- Derived state must identify its source.
- Ephemeral state must not become accidental canonical state.
- Rebuilding derived state must preserve family meaning.
- State transitions affecting canonical information require stronger validation.

## Principle

Know what must survive before deciding what may be discarded.
