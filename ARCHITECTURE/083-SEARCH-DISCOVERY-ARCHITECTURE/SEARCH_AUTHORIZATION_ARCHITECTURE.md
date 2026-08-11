# FEMC Search Authorization Architecture

**Version:** 1.0.0
**Status:** Architecture
**Owner:** Architecture Office

## Security Rule

Search must never become a side door around family authorization.

## Flow

```text
QUERY
 ↓
IDENTITY
 ↓
FAMILY CONTEXT
 ↓
AUTHORIZED SCOPE
 ↓
RETRIEVAL
 ↓
RESULT FILTERING
 ↓
PRESENTATION
```

## Principles

- Do not index information into a globally searchable space without considering authorization.
- Revoked access must affect future discovery.
- Sensitive information requires appropriate filtering.
- Search snippets must not expose information the user cannot open.

## Principle

If a person cannot access the source information, search should not reveal it through a result.
