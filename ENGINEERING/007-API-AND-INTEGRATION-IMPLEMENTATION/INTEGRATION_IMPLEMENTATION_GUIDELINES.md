# FEMC Integration Implementation Guidelines

**Version:** 1.0.0
**Status:** Engineering Design
**Owner:** Engineering Office

## Integration Boundary

External providers must be accessed through explicit integration adapters or equivalent boundaries.

## Requirements

- isolate provider-specific formats;
- validate external responses;
- preserve provenance;
- handle timeout and retry safely;
- prevent duplicate side effects;
- protect credentials;
- support provider replacement.

## Failure

An unavailable provider must not corrupt canonical family information.

## Principle

Integrations should be replaceable without rewriting FEMC's family domain.
