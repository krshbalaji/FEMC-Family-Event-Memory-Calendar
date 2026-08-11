# FEMC AI Provider Abstraction

**Version:** 1.0.0
**Status:** Engineering Design
**Owner:** Engineering Office

## Objective

Prevent provider-specific AI implementation from becoming embedded throughout FEMC.

## Boundary

```text
FEMC AI CONTRACT
       ↓
AI ADAPTER
       ↓
MODEL PROVIDER
```

## Provider-Specific Concerns

Keep provider-specific:

- authentication;
- model identifiers;
- request formats;
- response formats;
- provider-specific tools;
- provider telemetry.

## Migration

A provider change should affect the adapter and controlled configuration rather than the canonical family domain.

## Principle

The model is an implementation dependency; the AI capability is the architectural contract.
