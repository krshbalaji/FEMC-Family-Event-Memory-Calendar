# FEMC Data Derivation and Indexing Model

**Version:** 1.0.0
**Status:** Data Architecture
**Owner:** Data Office

## Derivation

```text
CANONICAL DATA
      ↓
TRANSFORMATION
      ↓
DERIVED DATA
      ↓
SEARCH / AI / ANALYTICS
```

## Rules

Derived representations should have:

- source relationship;
- transformation logic;
- refresh strategy;
- invalidation behavior;
- access boundary;
- rebuild/recovery strategy.

Derived data must not silently override canonical data.

## Principle

Convenient representations are useful precisely because they are derived; they must never be mistaken for the source of family truth.
