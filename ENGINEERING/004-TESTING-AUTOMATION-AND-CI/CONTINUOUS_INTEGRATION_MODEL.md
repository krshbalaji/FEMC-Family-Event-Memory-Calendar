# FEMC Continuous Integration Model

**Version:** 1.0.0
**Status:** Engineering Delivery
**Owner:** Engineering Office

## Flow

```text
CHANGE
 ↓
BUILD
 ↓
STATIC / QUALITY CHECKS
 ↓
TEST
 ↓
PACKAGE
 ↓
EVIDENCE
```

## Requirements

CI should verify material changes before they become shared release candidates.

Failures should be visible, attributable, and reproducible enough to investigate.

## Principle

Continuous integration is a feedback system, not merely a gate that turns builds red or green.
