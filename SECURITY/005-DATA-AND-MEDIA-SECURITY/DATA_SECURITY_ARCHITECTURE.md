# FEMC Data Security Architecture

**Version:** 1.0.0
**Status:** Security Architecture
**Owner:** Security Office

## Protection Layers

```text
IDENTITY
 ↓
AUTHORIZATION
 ↓
DATA ACCESS
 ↓
DATA STORAGE
 ↓
DATA TRANSFER
 ↓
BACKUP / EXPORT
 ↓
RETENTION / DELETION
```

## Requirements

Protect canonical family information throughout its lifecycle.

Security controls should account for:

- confidentiality;
- integrity;
- availability;
- provenance;
- authorized transformation;
- recovery.

## Principle

Data security follows family information wherever it travels.
