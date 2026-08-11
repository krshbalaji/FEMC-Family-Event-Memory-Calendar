# FEMC Multichannel Message Consistency

**Version:** 1.0.0
**Status:** Communication Architecture
**Owner:** Communication Office

## Goal

Maintain consistent communication meaning across channels while allowing appropriate channel-specific presentation.

## Distinguish

```text
MESSAGE INTENT
   ↓
CANONICAL MESSAGE CONTENT
   ↓
CHANNEL REPRESENTATION
```

## Rules

A shorter SMS, push notification, email, or voice rendering may differ in format but must not silently change material meaning.

## Principle

Different channels may speak differently; FEMC should not say different things accidentally.
