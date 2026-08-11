# FEMC Trust Boundary Model

**Version:** 1.0.0
**Status:** Architecture
**Owner:** Architecture Office

## Trust Zones

```text
USER
 │
 ▼
IDENTITY / AUTHORIZATION
 │
 ▼
FAMILY CONTEXT
 │
 ▼
CANONICAL DOMAIN
 │
 ├────► DERIVED INTELLIGENCE
 │
 ├────► AI
 │
 └────► EXTERNAL INTEGRATIONS
```

Infrastructure and operational personnel remain separate trust concerns.

## Fundamental Rule

Access to one zone must not imply unrestricted access to another.

## AI Boundary

AI is an explicit trust boundary whenever family information leaves the canonical domain for model processing.

## External Provider Boundary

External providers are separate trust domains.

## Principle

Trust boundaries should follow information authority and risk, not only network topology.
