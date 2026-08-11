# FEMC Memory Graph Architecture

**Version:** 1.0.0
**Status:** Architecture
**Owner:** Architecture Office

## Purpose

Represent the relationships connecting family memories so discovery can follow meaning rather than only keywords.

## Graph Concepts

```text
Person ── Relationship ── Person
  │                         │
  ├──── Event ──────────────┤
  │       │
  │       ├── Media
  │       └── Memory
  │             │
  │             └── Album
  │
  └──── Legacy
```

## Rules

- Graph relationships must derive from authorized domain information.
- Inferred relationships remain explicitly derived.
- Removing a derived edge must not remove canonical records.
- Privacy boundaries apply to graph traversal.
- Graph indexes may be rebuilt.

## Principle

The memory graph connects meaning; it does not manufacture relationships.
