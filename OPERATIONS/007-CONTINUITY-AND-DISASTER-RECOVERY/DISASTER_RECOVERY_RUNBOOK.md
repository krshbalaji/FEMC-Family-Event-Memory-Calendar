# FEMC Disaster Recovery Runbook

**Version:** 1.0.0
**Status:** Operations
**Owner:** Operations Office

## Recovery Sequence

```text
DECLARE
 ↓
ASSESS
 ↓
CONTAIN
 ↓
ESTABLISH TRUST
 ↓
RESTORE CANONICAL DATA
 ↓
RESTORE CORE SERVICES
 ↓
VERIFY
 ↓
RESTORE DERIVED CAPABILITIES
 ↓
RETURN TO NORMAL
```

## Requirements

Recovery actions must be attributable, documented, and verified.

No recovery step should silently replace canonical family information with unverified derived information.

## Principle

Recover in an order that restores truth before convenience.
