# FEMC Secure Configuration and Secrets

**Version:** 1.0.0
**Status:** Security Architecture
**Owner:** Security Office

## Requirements

Secrets and sensitive configuration must have:

- controlled storage;
- limited access;
- rotation capability;
- revocation capability;
- environment separation;
- appropriate monitoring.

## Rules

Never place credentials in source code, ordinary documentation, logs, or family data.

Configuration changes affecting security boundaries require appropriate review.

## Principle

Security-sensitive configuration is controlled authority, not ordinary application text.
