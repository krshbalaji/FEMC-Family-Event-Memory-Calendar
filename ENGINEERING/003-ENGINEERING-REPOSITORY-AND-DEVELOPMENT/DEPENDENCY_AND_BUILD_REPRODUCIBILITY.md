# FEMC Dependency and Build Reproducibility

**Version:** 1.0.0
**Status:** Engineering Foundation
**Owner:** Engineering Office

## Requirements

Builds should be reproducible enough to identify:

- source revision;
- dependency versions;
- configuration inputs;
- generated artifacts;
- build environment assumptions.

## Dependency Rules

Material dependencies should have:

- known ownership;
- version strategy;
- security assessment;
- replacement awareness;
- upgrade path.

## Principle

FEMC should be able to explain how a release was produced and reproduce it reliably enough to investigate or recover from failure.
