# FEMC Export and Import Architecture

**Version:** 1.0.0
**Status:** Architecture
**Owner:** Architecture Office

## Export

A meaningful export should consider:

- people;
- relationships;
- events;
- memories;
- media;
- albums;
- provenance;
- permissions-related context where appropriate;
- schema/version information.

## Import

Imported information should retain:

- source;
- import time;
- transformation history;
- confidence;
- unresolved conflicts.

## Validation

Imports must be validated before affecting canonical family information.

## Provider Independence

Exports should not depend on one vendor's proprietary internal database representation.

## Principle

Portability means reconstructing family meaning, not merely copying bytes.
