# FEMC External Failure Model

**Version:** 1.0.0
**Status:** Architecture
**Owner:** Architecture Office

## Failure Classes

External systems may experience:

- outage;
- timeout;
- rate limiting;
- partial response;
- stale data;
- authentication failure;
- contract change;
- permanent retirement.

## Required Behavior

FEMC should:

- preserve canonical information;
- distinguish unavailable from deleted;
- avoid uncontrolled retries;
- surface material failure appropriately;
- recover when the dependency returns;
- support provider replacement where practical.

## Principle

External dependency failure should reduce capability, not destroy family history.
