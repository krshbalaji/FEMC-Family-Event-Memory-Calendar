# FEMC Data Lifecycle and Retention

**Version:** 1.0.0
**Status:** Engineering Design
**Owner:** Engineering Office

## Lifecycle

```text
CREATE
 ↓
USE
 ↓
UPDATE
 ↓
ARCHIVE
 ↓
EXPORT / PRESERVE
 ↓
DELETE WHEN AUTHORIZED
```

## Requirements

Lifecycle behavior must consider:

- family ownership;
- consent;
- legal/operational requirements where applicable;
- backups;
- derived copies;
- search indexes;
- AI-derived artifacts;
- exports;
- media representations.

## Deletion

Deleting canonical information must not leave uncontrolled hidden copies within FEMC-managed derived systems.

## Principle

Data lifecycle is a system-wide behavior, not a database command.
