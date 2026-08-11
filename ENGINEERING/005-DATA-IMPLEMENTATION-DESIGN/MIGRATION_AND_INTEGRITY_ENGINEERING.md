# FEMC Migration and Integrity Engineering

**Version:** 1.0.0
**Status:** Engineering Design
**Owner:** Engineering Office

## Migration Requirements

Every material migration should define:

1. source;
2. target;
3. mapping;
4. transformation;
5. validation;
6. reconciliation;
7. rollback/recovery;
8. post-migration verification.

## Integrity Checks

Engineering should validate:

- record counts where meaningful;
- relationship consistency;
- required fields;
- provenance;
- authorization boundaries;
- media references;
- derived-state rebuildability.

## Principle

A migration is a data transformation with a correctness proof, not a copy operation.
