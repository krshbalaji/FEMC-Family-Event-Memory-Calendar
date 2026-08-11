# FEMC Sharing Implementation and Tests

**Version:** 1.0.0
**Status:** Engineering Design
**Owner:** Engineering Office

## Sharing Controls

Implement and test:

- recipient validation;
- family-scope validation;
- resource authorization;
- consent/policy checks;
- expiration or revocation where applicable;
- external channel boundaries;
- auditability.

## Negative Tests

A recipient must not receive content when:

- access was revoked;
- the recipient is outside the authorized family scope;
- the resource is private;
- the share token/context is invalid;
- the external channel is unauthorized.

## Principle

Sharing is an authorization event, not merely a send operation.
