# FEMC Identity Session and Device Context

**Version:** 1.0.0
**Status:** Identity Architecture
**Owner:** Identity Office

## Context

Sessions and devices are technical representations of an authenticated participant.

They may carry:

- session state;
- device trust;
- risk signals;
- expiry;
- revocation state.

## Rules

A trusted device is not itself a family identity.

Session/device context must expire, be revocable, and remain subordinate to identity and authorization.

## Principle

Convenience signals may strengthen authentication decisions; they must not become permanent identity truth.
