# FEMC AI Discovery Architecture

**Version:** 1.0.0
**Status:** Architecture
**Owner:** Architecture Office

## Purpose

Use AI to improve family discovery while maintaining grounding and authorization.

## Flow

```text
USER INTENT
 ↓
AUTHORIZED FAMILY CONTEXT
 ↓
RETRIEVAL
 ↓
AI INTERPRETATION
 ↓
GROUNDING / POLICY CHECK
 ↓
ANSWER / DISCOVERY
```

## Requirements

AI discovery should:

- cite or expose source context where appropriate;
- distinguish facts from inference;
- respect authorization;
- handle uncertainty;
- avoid fabricated family relationships;
- remain independent of one model provider.

## Principle

AI can help families discover connections hidden in their history without inventing connections that do not exist.
