# FEMC Calendar Synchronization and Reconciliation

**Version:** 1.0.0
**Status:** Calendar Assurance
**Owner:** Calendar Office

## Synchronization

External calendar synchronization should define:

- source;
- direction;
- frequency;
- identity mapping;
- conflict behavior;
- deletion behavior;
- recurrence behavior;
- time-zone behavior.

## Reconciliation

Conflicting calendar representations must be resolved against canonical Event meaning rather than provider precedence alone.

## Principle

Synchronization moves representations; it must not silently move authority.
