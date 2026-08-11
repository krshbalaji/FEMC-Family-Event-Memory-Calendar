# FEMC Environment and Configuration Management

**Version:** 1.0.0
**Status:** Engineering Operations
**Owner:** Engineering Office

## Environments

Material environments should have explicit purpose and boundaries, such as:

- development;
- test;
- staging;
- production.

## Rules

Configuration must be separated from source code where appropriate.

Production secrets must never be treated as ordinary development configuration.

Environment differences should be deliberate and documented enough to prevent accidental behavior drift.

## Principle

An environment should be reproducible enough to understand why software behaves differently there.
