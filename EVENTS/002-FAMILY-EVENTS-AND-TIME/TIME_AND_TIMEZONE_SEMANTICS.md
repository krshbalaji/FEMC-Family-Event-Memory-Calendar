# FEMC Time and Time-Zone Semantics

**Version:** 1.0.0
**Status:** Events Architecture
**Owner:** Events Office

## Time Concepts

FEMC should distinguish:

- instant;
- local date;
- local date-time;
- duration;
- time zone;
- recurring local time;
- approximate/unknown time.

## Rules

Never silently convert an unknown or approximate time into false precision.

Historical time-zone interpretation should be preserved where material.

## Principle

A technically valid timestamp can still misrepresent family history if its temporal meaning is wrong.
