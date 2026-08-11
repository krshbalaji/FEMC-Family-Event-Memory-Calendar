# FEMC Integration Boundary Principles

**Version:** 1.0.0  
**Status:** Foundation  
**Owner:** Chief Product Architect

## Boundary Model

```text
FEMC Canonical Domain
        ↕
   Integration Boundary
        ↕
External Provider
```

## Rule 1 — Translate Meaning

External representations should be mapped into FEMC's canonical concepts rather than copied blindly.

## Rule 2 — Preserve Provenance

Imported information should retain its source where appropriate.

## Rule 3 — Minimize Exposure

Send only the information required for the integration purpose.

## Rule 4 — Permission Follows Context

An integration must respect existing family permissions.

## Rule 5 — Failure Must Be Contained

External failures should not become canonical data corruption.

## Rule 6 — Replacement Must Be Possible

Integrations should be designed so that an alternative provider can eventually be introduced.

## Rule 7 — AI Providers Are Integrations

AI providers follow the same boundary principles as other external systems.

## Rule 8 — No Hidden Dependency

A critical family capability should not silently depend on an external provider that users cannot replace or understand.

## Rule 9 — Contracts Over Convenience

Stable conceptual contracts are preferable to provider-specific assumptions.

## Rule 10 — Document Material Integrations

Significant integrations require documented purpose, data scope, trust boundary, and failure implications.
