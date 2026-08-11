# FEMC State Transitions and Consistency

**Version:** 1.0.0
**Status:** Architecture
**Owner:** Architecture Office

## State Model

```text
VALID STATE
   ↓
AUTHORIZED COMMAND
   ↓
VALIDATED TRANSITION
   ↓
NEW CANONICAL STATE
   ↓
DERIVED UPDATES
```

## Rules

State transitions must preserve domain invariants.

Where immediate consistency is not required, the architecture must explicitly define:

- acceptable delay;
- source of truth;
- reconciliation behavior;
- user-visible state;
- failure recovery.

## Principle

Consistency is a domain decision, not merely a database setting.
