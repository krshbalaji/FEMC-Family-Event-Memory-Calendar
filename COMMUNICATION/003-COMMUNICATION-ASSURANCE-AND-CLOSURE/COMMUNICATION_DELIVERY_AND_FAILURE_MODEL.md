# FEMC Communication Delivery and Failure Model

**Version:** 1.0.0
**Status:** Communication Assurance
**Owner:** Communication Office

## Delivery Lifecycle

```text
CREATE
 ↓
AUTHORIZE
 ↓
QUEUE
 ↓
DELIVER
 ↓
ACKNOWLEDGE / EXPIRE
 ↓
RECONCILE
```

## Failure Classes

- invalid recipient;
- unavailable channel;
- provider failure;
- timeout;
- duplicate delivery;
- delayed delivery;
- content failure;
- authorization failure.

## Principle

A failed message must not silently become a failed family expectation.
