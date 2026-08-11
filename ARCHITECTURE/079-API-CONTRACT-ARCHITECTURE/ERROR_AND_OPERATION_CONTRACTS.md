# FEMC Error and Operation Contracts

**Version:** 1.0.0
**Status:** Architecture
**Owner:** Architecture Office

## Error Classes

Contracts should distinguish, where appropriate:

- invalid request;
- unauthorized access;
- unavailable dependency;
- conflict;
- validation failure;
- temporary failure;
- permanent failure.

## Safety

Errors must not unnecessarily expose private family information or internal security details.

## Idempotency

Operations that may be retried should have defined idempotency behavior where appropriate.

## Partial Failure

A failed optional integration must not be represented as loss of canonical family data.

## Principle

A contract is incomplete if successful behavior is defined but failure behavior is not.
