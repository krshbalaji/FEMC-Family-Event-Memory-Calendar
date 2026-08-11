# FEMC AI Output Validation

**Version:** 1.0.0
**Status:** Engineering Design
**Owner:** Engineering Office

## Validation Layers

```text
MODEL OUTPUT
 ↓
FORMAT VALIDATION
 ↓
POLICY VALIDATION
 ↓
GROUNDING / SOURCE CHECK
 ↓
DOMAIN VALIDATION
 ↓
HUMAN CONFIRMATION WHERE REQUIRED
 ↓
USE / STORE AS DERIVED OUTPUT
```

## Rules

AI output must be treated according to its risk.

Low-risk presentation assistance may require lighter controls.

Material family facts, relationship changes, sharing actions, or destructive operations require stronger validation.

## Principle

Confidence in a model is never a substitute for validation.
