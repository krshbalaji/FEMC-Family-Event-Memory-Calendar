# FEMC Data Integrity Principles

**Version:** 1.0.0  
**Status:** Foundation  
**Owner:** Chief Product Architect

## 1. Canonical Truth

Each core domain concept should have a clear authoritative representation.

## 2. Referential Meaning

Relationships between entities are part of the information's meaning.

## 3. No Silent Mutation

Important family history must not be changed invisibly.

## 4. Provenance

Material information should retain appropriate origin and status.

## 5. Validation

Inputs and migrations should be validated before becoming canonical.

## 6. Controlled Deletion

Destructive actions should be deliberate and governed.

## 7. Recovery

Integrity includes the ability to restore trustworthy state.

## 8. Migration Safety

A migration is successful only if it preserves both data and meaning.

## 9. Derived Data Separation

Caches, indexes, embeddings, summaries, and recommendations are not automatically canonical.

## 10. Integrity Over Convenience

When a shortcut risks corrupting family history, the shortcut must be rejected.
