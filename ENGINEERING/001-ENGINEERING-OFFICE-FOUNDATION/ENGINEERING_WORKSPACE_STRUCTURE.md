# FEMC Engineering Workspace Structure

**Version:** 1.0.0
**Status:** Engineering Foundation

## Recommended Logical Structure

```text
ENGINEERING/
├── docs/
│   ├── decisions/
│   ├── design/
│   └── validation/
├── source/
├── tests/
├── tooling/
├── deployment/
└── operations/
```

## Rules

- Documentation remains discoverable.
- Tests remain first-class engineering artifacts.
- Deployment definitions are separated from application source where appropriate.
- Architecture decisions remain traceable.
- Generated artifacts are distinguishable from source.
- Secrets never belong in source control.

## Principle

The repository should make the correct engineering workflow obvious.
