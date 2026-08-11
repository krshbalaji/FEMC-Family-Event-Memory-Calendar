# FEMC AI Memory Architecture

**Version:** 1.0.0
**Status:** AI Architecture
**Owner:** AI Office

## Purpose

Define how AI obtains family context without confusing retrieval with canonical family memory.

## Layers

```text
CANONICAL FAMILY DATA
        ↓
AUTHORIZED RETRIEVAL
        ↓
RELEVANT CONTEXT
        ↓
AI PROCESSING
        ↓
GROUNDED OUTPUT
```

## Rules

- Canonical data remains outside the model as governed source truth.
- Retrieval is authorization-aware.
- Context is task-specific.
- Retrieved information should retain source identity where material.
- AI-generated context must not silently become canonical data.

## Principle

AI memory is a controlled view of family memory, not a second uncontrolled database.
