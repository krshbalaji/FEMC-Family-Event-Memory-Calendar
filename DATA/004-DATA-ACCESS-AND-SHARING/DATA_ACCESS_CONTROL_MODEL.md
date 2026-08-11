# FEMC Data Access Control Model

**Version:** 1.0.0
**Status:** Data Architecture
**Owner:** Data Office

## Purpose

Define how access to family information follows authorized identity, purpose, resource scope, and lifecycle.

## Decision Path

```text
IDENTITY
 ↓
FAMILY CONTEXT
 ↓
RESOURCE
 ↓
PURPOSE
 ↓
AUTHORIZATION
 ↓
DATA ACCESS
```

## Rules

Data access must not be granted merely because a service can technically reach a datastore.

Derived stores, indexes, caches, exports, and analytical views must respect the effective authorization boundary.

## Principle

Data access follows meaning and authority, not database connectivity.
