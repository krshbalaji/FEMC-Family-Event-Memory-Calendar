# FEMC Domain Evolution Rules

**Version:** 1.0.0  
**Status:** Foundation  
**Owner:** Chief Product Architect

## Rule 1 — Preserve Meaning

Domain evolution must preserve the meaning of existing family records.

## Rule 2 — Never Invent History

If historical information is unknown, preserve it as unknown or uncertain.

AI must never convert probability into family fact without appropriate confirmation.

## Rule 3 — Preserve Relationships

When a concept changes, relationships to people, events, memories, and other concepts must be evaluated before migration.

## Rule 4 — Support Time

Relationships and facts may change over time.

The model must not assume that today's state is the only historical state.

## Rule 5 — Support Multiple Family Structures

FEMC must not encode unnecessary assumptions about what constitutes a family.

The model should support diverse real-world family structures while preserving clear semantics.

## Rule 6 — Separate Fact from Interpretation

User-confirmed information, imported information, inferred information, and AI-generated suggestions should remain distinguishable.

## Rule 7 — Prefer Additive Evolution

When practical, evolve by adding capabilities rather than destructively rewriting historical meaning.

## Rule 8 — Document Breaking Changes

If a change can affect historical interpretation, permissions, interoperability, or data migration, it requires a documented architectural decision.

## Rule 9 — Exportability

Domain evolution must consider whether family information remains understandable outside the current implementation.

## Rule 10 — Ten-Year Test

Before approving a fundamental domain change, ask:

> If FEMC still exists ten years from now, will this decision make the family record easier or harder to understand and preserve?

If the answer is unclear, record the uncertainty and avoid premature commitment.
