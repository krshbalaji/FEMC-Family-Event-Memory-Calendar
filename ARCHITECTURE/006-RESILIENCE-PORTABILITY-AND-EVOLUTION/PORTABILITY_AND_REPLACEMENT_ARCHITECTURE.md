# FEMC Portability and Replacement Architecture

**Version:** 1.0.0
**Status:** Architecture
**Owner:** Architecture Office

## Replaceable Areas

Where practical, maintain replaceability for:

- AI providers;
- storage;
- search;
- messaging;
- identity services;
- infrastructure providers;
- analytics;
- other material external dependencies.

## Replacement Path

```text
CONTRACT
 ↓
ADAPTER
 ↓
PROVIDER
```

The provider should not leak unnecessary implementation assumptions into the family domain.

## Principle

Portability is not the promise that every component can be replaced instantly. It is the deliberate preservation of the ability to change.
