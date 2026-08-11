# FEMC Temporal and History Model

**Version:** 1.0.0
**Status:** Architecture
**Owner:** Architecture Office

## Temporal Dimensions

FEMC may need to distinguish:

- event time;
- record creation time;
- record modification time;
- relationship validity period;
- media creation time;
- memory recognition time;
- archival time.

## Uncertainty

The model should support:

- exact dates;
- approximate dates;
- date ranges;
- unknown dates;
- historical estimates.

## Corrections

A correction should not automatically destroy prior historical context when that context remains meaningful.

## Principle

Time is part of family meaning, not merely a database timestamp.
