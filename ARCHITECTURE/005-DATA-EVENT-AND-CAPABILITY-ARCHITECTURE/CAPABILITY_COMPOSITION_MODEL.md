# FEMC Capability Composition Model

**Version:** 1.0.0
**Status:** Architecture
**Owner:** Architecture Office

## Composition

```text
DOMAIN
 ↓
CAPABILITY
 ↓
WORKFLOW
 ↓
EXPERIENCE
```

A capability should compose existing domain meaning rather than duplicate it.

## Rules

- Prefer reusable capabilities over feature-specific copies.
- Keep workflows replaceable.
- Do not let presentation become the owner of domain rules.
- Avoid hidden coupling between unrelated capabilities.

## Principle

FEMC should behave like a coherent capability system, not a collection of feature silos.
