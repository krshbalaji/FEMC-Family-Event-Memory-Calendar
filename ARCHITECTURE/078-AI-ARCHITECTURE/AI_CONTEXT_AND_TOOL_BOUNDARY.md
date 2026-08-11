# FEMC AI Context and Tool Boundary

**Version:** 1.0.0
**Status:** Architecture
**Owner:** Architecture Office

## Context Pipeline

```text
USER INTENT
 ↓
IDENTITY
 ↓
FAMILY CONTEXT
 ↓
AUTHORIZED RESOURCES
 ↓
TASK CONTEXT
 ↓
AI
```

## Tool Authority

AI tools should be individually governed.

A model that can read information does not automatically gain permission to modify it.

A model that can propose an action does not automatically gain authority to execute it.

## Context Minimization

Provide only the information needed for the task.

## Output Handling

AI output must pass through appropriate validation and authorization before consequential use.

## Principle

AI capability must never exceed the authority granted to the context in which it operates.
