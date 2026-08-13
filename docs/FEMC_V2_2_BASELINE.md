# FEMC V2.2 Baseline Record — Projection Truth Reconciliation

## 1. Baseline Name
`FEMC V2.2 — Projection Truth Reconciliation`

## 2. Purpose
Establish 100% cross-screen projection consistency between canonical `FEMCApi` state, Calendar, Home Dashboard, and Mayil AI projections for authorized family contexts.

## 3. V2.1 Observed Gap
During real browser walkthroughs of the V2.1 demo, the Calendar screen displayed 2 upcoming family events, whereas the Home Dashboard's "Upcoming Family Events" section displayed *"No upcoming events scheduled."* At the same time, Mayil AI Engine reported analyzing upcoming events.

## 4. Root Cause
The `DashboardProjectionEntry` dataclass defines the item type property as `item_type` (e.g., `item_type: DashboardEntryType = DashboardEntryType.UPCOMING_EVENT`). However, the `run.py` JavaScript presentation logic attempted to filter entries using `e.entry_type` (which evaluated to `undefined`). Consequently, `eventsList` filtered down to `[]` (empty array), causing Home to render *"No upcoming events scheduled"*, even though `FEMCApi` correctly returned valid upcoming event entries.

## 5. Correction
Updated presentation mapping in `run.py` to inspect both `(e.item_type || e.entry_type)` and `(e.date_or_time || e.date)` for safe, accurate property access.

## 6. Regression Protection
Added `test_projection_truth_cross_screen_consistency` in `ENGINEERING/tests/test_femc_demo_host.py` to ensure that every canonical upcoming event present in the Calendar projection is matched in the Dashboard projection entries and analyzed by Mayil AI.

## 7. Verification Results
- Total Tests: **117 passed**
- Failures: 0
- Errors: 0
- Skipped: 0

## 8. Cross-Screen Result
- Calendar: 2 upcoming events (`Alice's Birthday Celebration`, `Smith Family Weekend Dinner`)
- Home Dashboard: 2 upcoming events under **Upcoming Family Events**, 1 due reminder under **Reminders / Needs Attention**, 1 recent memory under **Recent Family Memories**, 1 celebration highlight under **Celebration Highlights**.
- Mayil AI Engine: Analyzed 2 events, 1 memory, and 0 places for context `'Smith Family'`.
- Agreement: **100% cross-screen alignment**.

## 9. Production Source Boundary
`ENGINEERING/source/femc/` remains **100% clean and untouched**.

## 10. V2.1 → V2.2 Growth Summary
- 116 -> 117 passing tests (+1 cross-screen projection reconciliation test)
- Cross-screen projection mismatch resolved
- Regression protection added
- 0% production-domain code drift

## 11. Deliberate Scope
V2.2 is a projection-truth and product-consistency checkpoint. It establishes that canonical `FEMCApi` state projects consistently across all user screens without claiming that FEMC is feature-complete.

## 12. Next Stage
V2.3 feature development begins only after a fresh user demo / discovery cycle.
