# FEMC Deployment and Rollback Model

**Version:** 1.0.0
**Status:** Engineering Operations
**Owner:** Engineering Office

## Deployment

Deployments should be:

- repeatable;
- observable;
- bounded;
- recoverable.

## Rollback

Rollback planning must distinguish between:

- code rollback;
- configuration rollback;
- schema/data migration;
- external dependency changes.

A code rollback alone may not restore a previous trusted state after irreversible data changes.

## Principle

Safe deployment means knowing how to move forward and how to recover when moving forward fails.
