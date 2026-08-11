# FEMC Contract Versioning and Compatibility

**Version:** 1.0.0
**Status:** Architecture
**Owner:** Architecture Office

## Contract Lifecycle

```text
DEFINE
 ↓
PUBLISH
 ↓
CONSUME
 ↓
EVOLVE
 ↓
DEPRECATE
 ↓
RETIRE
```

## Rules

Material contracts should define compatibility expectations.

Prefer additive evolution where possible.

Breaking changes require an explicit migration path, affected-consumer assessment, and controlled retirement of the previous contract.

## Principle

A stable contract is not one that never changes; it is one that changes without surprising its dependents.
