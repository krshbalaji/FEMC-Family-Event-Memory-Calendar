# FEMC Data Ownership and Lifecycle Architecture

**Version:** 1.0.0
**Status:** Architecture
**Owner:** Architecture Office

## Data Lifecycle

```text
CREATE
 ↓
VALIDATE
 ↓
AUTHORITATIVE STORAGE
 ↓
DERIVE / INDEX
 ↓
USE / SHARE
 ↓
ARCHIVE / RETAIN
 ↓
DELETE / PRESERVE
```

## Rules

Every material data object must have:

- authoritative owner;
- lifecycle;
- access boundary;
- provenance;
- retention expectation;
- deletion/preservation behavior.

Derived stores must be rebuildable or have an explicitly governed recovery strategy where practical.

## Principle

Data ownership must remain understandable even when the same information appears in many technical representations.
