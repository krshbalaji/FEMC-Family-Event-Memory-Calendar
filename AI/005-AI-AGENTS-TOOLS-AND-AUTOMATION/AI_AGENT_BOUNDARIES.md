# FEMC AI Agent Boundaries

**Version:** 1.0.0
**Status:** AI Architecture
**Owner:** AI Office

## Agent Model

```text
USER INTENT
 ↓
AI REASONING
 ↓
AUTHORIZED TOOLS
 ↓
VALIDATED ACTION
 ↓
OBSERVABLE RESULT
```

## Rules

Agents must have explicit tool permissions.

An agent must not infer permission from conversational intent alone.

Actions affecting canonical family information, sharing, deletion, identity, or durable records require controls appropriate to their consequence.

## Principle

An AI agent is a bounded operator, not a family administrator.
