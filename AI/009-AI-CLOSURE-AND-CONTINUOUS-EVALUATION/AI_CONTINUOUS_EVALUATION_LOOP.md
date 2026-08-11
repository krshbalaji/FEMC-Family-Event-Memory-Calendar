# FEMC AI Continuous Evaluation Loop

**Version:** 1.0.0
**Status:** AI Handoff
**Owner:** AI Office

## Loop

```text
CAPABILITY
 ↓
EVALUATE
 ↓
RELEASE
 ↓
OBSERVE
 ↓
REAL-WORLD FEEDBACK
 ↓
RE-EVALUATE
 ↓
IMPROVE / RESTRICT / RETIRE
 ↺
```

## Triggers

Re-evaluation should occur after:

- model/provider changes;
- prompt or retrieval changes;
- material incidents;
- significant family-context changes;
- new tools;
- new data sources;
- material behavior drift.

## Principle

AI quality is not a launch-time property; it is continuously earned.
