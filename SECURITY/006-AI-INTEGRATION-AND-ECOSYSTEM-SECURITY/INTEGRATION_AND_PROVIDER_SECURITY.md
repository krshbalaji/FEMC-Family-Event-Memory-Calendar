# FEMC Integration and Provider Security

**Version:** 1.0.0
**Status:** Security Architecture
**Owner:** Security Office

## Requirements

External integrations should have:

- explicit identity;
- bounded credentials;
- minimum required data;
- scoped permissions;
- secure transport;
- failure isolation;
- revocation;
- provider-risk review.

## Data Minimization

Send only information required for the specific integration task.

## Principle

A trusted FEMC user does not automatically make an external provider trusted with the same information.
