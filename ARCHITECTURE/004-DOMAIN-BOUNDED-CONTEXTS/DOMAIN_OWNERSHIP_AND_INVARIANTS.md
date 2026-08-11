# FEMC Domain Ownership and Invariants

**Version:** 1.0.0
**Status:** Architecture
**Owner:** Architecture Office

## Ownership

Each material domain must have an explicit owner for:

- semantic meaning;
- invariants;
- lifecycle;
- authoritative state;
- change rules;
- published contracts.

## Invariants

An invariant is a condition that must remain true for the domain to remain trustworthy.

Examples:

- an event has a coherent temporal identity;
- a relationship has defined participants and context;
- canonical memory is distinguishable from derived interpretation;
- authorization cannot be inferred solely from technical location.

## Principle

If nobody owns an invariant, the architecture does not actually own that behavior.
