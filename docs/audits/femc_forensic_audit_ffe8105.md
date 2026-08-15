# FEMC Canonical Implementation Forensic Audit
**Repository:** `FEMC-Family-Event-Memory-Calendar-GIT`
**Branch:** `reconcile/femc-execution-plan`
**Audit Commit:** `ffe8105`
**Audit Date:** 2026-08-14
**Status:** AUDIT COMPLETE — AUDIT-ONLY, NO CODE MODIFIED

---

## A. Repository Truth

| Field | Value |
|---|---|
| Branch | `reconcile/femc-execution-plan` |
| HEAD Commit | `ffe8105` |
| Working Tree | **Clean** (no uncommitted changes) |
| Test Baseline | **200 passed, 2 failed** |

---

## B. Source Structure Map

```
ENGINEERING/
  source/
    femc/
      models.py          # All data models / enums (729 lines)
      repositories.py    # State storage: CanonicalRepository, DerivedRepository,
                         #   TransactionMemoryRepository
      services.py        # Domain logic: all *Service classes
      api.py             # FEMCApi — primary integration surface (orchestrator)
  tests/
    test_femc_*.py       # 15 test files, 202 tests total
run.py                   # Web server: DemoState + DemoHTTPRequestHandler (3183 lines)
```

**Primary Source Layer (canonical):** `ENGINEERING/source/femc/`

The three-layer domain split is:
1. **`models.py`** — Typed dataclasses + enums, no logic
2. **`repositories.py`** — In-memory dict-backed state stores
3. **`services.py`** — Domain logic, authorization, business rules
4. **`api.py`** — Orchestration facade; the only public interface used by routes and tests

---

## C. Test Baseline — Confirmed

```
pytest ENGINEERING/tests/ -v
200 passed, 2 failed
```

**Failing tests** (both in `ENGINEERING/tests/test_femc_transaction_memory.py`):
- `test_delete_transaction_survives_entity_deletion` (line 57)
- `test_share_and_revoke_transactions_recorded` (line 132)

---

## D. Transaction Ordering Contract — Root Cause Analysis

### Canonical Ordering Contract
`TransactionMemoryRepository.list_transactions()` (repositories.py ~line 372):
```python
results.sort(key=lambda x: x.timestamp, reverse=True)
```
**Declared order: newest-first (reverse chronological).**

### What the Failing Tests Expect
Both tests follow this pattern:
1. Record action A (e.g. `CREATE` or `SHARE`)
2. Record action B (e.g. `DELETE` or `REVOKE_SHARE`)
3. Call `get_resource_history_for_session()`
4. Assert `history[0].action_type == <newest action>`

This is **consistent with the declared reverse-chronological contract** (`history[0]` = newest).

### Root Cause: Timestamp Collision at Sub-Microsecond Resolution

`TransactionRecord.timestamp` is assigned via:
```python
# models.py line 161
timestamp: datetime.datetime = field(default_factory=_utc_now)

# models.py line 15-16
def _utc_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
```

When two `record_transaction_for_session()` calls are made **in the same Python test function**, sequentially without sleep, they can resolve to the **identical microsecond timestamp** (Python's `datetime.now()` resolution is OS-dependent; on Windows it can be as coarse as 15ms).

When `sort(..., reverse=True)` encounters equal keys, Python's Timsort preserves the **original insertion order** (stable sort). The repository appends records to a list on each `record_transaction()` call. Therefore:

**With equal timestamps:**
- Record 0 = `CREATE` (appended first) → stays at index 0 after stable sort
- Record 1 = `DELETE` (appended second) → stays at index 1

But the test asserts `history[0].action_type == ActionType.DELETE` (newest first).

**Result:** `AssertionError: assert <ActionType.CREATE> == <ActionType.DELETE>`

### Summary of the Two Failures

| Test | Expected `history[0]` | Got `history[0]` | Why |
|---|---|---|---|
| `test_delete_transaction_survives_entity_deletion` line 93 | `ActionType.DELETE` | `ActionType.CREATE` | Timestamps equal → stable sort preserves insertion (oldest first) |
| `test_share_and_revoke_transactions_recorded` lines 159–160 | `ActionType.REVOKE_SHARE` at `[0]`, `ActionType.SHARE` at `[1]` | Reversed | Same timestamp collision |

### Decision Required (not modified per audit-only constraint)

Two valid resolution paths exist:

**Option A — Fix the repository sort to be stable by adding a tiebreaker:**
```python
results.sort(key=lambda x: (x.timestamp, id(x)), reverse=True)
# OR: use a monotonic sequence counter in TransactionRecord
```

**Option B — Fix the tests to remove positional ordering dependence:**
```python
# Use set-based assertions, e.g.:
action_types = {r.action_type for r in history}
assert ActionType.DELETE in action_types
assert ActionType.CREATE in action_types
# And separately assert the newest by max(timestamp)
```

**Recommendation:** Option A (stable tiebreaker) is preferable because it locks the contract at the repository level and preserves the semantics the tests were authored to verify. A monotonic counter per-`FamilyContext` appended to `TransactionRecord` is the cleanest fix.

---

## E. Canonical State Ownership Map

### Primary State: `CanonicalRepository`
Holds all authoritative entity state in-memory dicts:

| Store | Key | Value |
|---|---|---|
| `_persons` | `str` (id) | `Person` |
| `_accounts` | `str` (id) | `Account` |
| `_sessions` | `str` (session_id) | `AuthenticatedSession` |
| `_relationships` | `str` (id) | `Relationship` |
| `_family_contexts` | `str` (id) | `FamilyContext` |
| `_events` | `str` (id) | `Event` |
| `_memories` | `str` (id) | `Memory` |
| `_media_items` | `str` (id) | `MediaItem` |
| `_media_albums` | `str` (id) | `MediaAlbum` |
| `_notifications` | `str` (id) | `Notification` |
| `_reminders` | `str` (id) | `ReminderConfig` |
| `_celebration_artifacts` | `str` (id) | `CelebrationArtifact` |
| `_share_links` | `str` (id) | `ShareLink` |
| `_proposals` | `str` (id) | `ActionProposal` |
| `_places` | `str` (id) | `Place` |

### Audit Trail: `TransactionMemoryRepository`
```
_records: List[TransactionRecord]   # append-only; sorted newest-first on retrieval
```

### Derived/Projection State: `DerivedRepository`
Holds computed projections (calendar entries, dashboard summaries, timeline projections).
These are rebuilt from canonical state on demand. They are the only state that can be safely discarded and rebuilt by the Guardian repair system.

---

## F. API Route Architecture

**Public surface:** `FEMCApi` (`api.py`) — single entry point.

**Server:** `DemoHTTPRequestHandler` (run.py, line 2714) — plain `BaseHTTPRequestHandler` subclass.
- `do_GET` (line 2715): ~30 route branches
- `do_POST` (line 2851): ~25 route branches

All routes access `demo_state.api` (a global `DemoState` instance at run.py:376).

**API Service Delegation Map:**

| `FEMCApi` sub-object | Service/Repository | Responsibility |
|---|---|---|
| `api.identity` | `IdentityService` | Persons, accounts, relationships, family context |
| `api.events` | `EventService` | Event CRUD, recurrence, milestone detection |
| `api.memories` | `MemoryService` | Memory CRUD, narrative |
| `api.media` | `MediaService` | MediaItem, MediaAlbum CRUD |
| `api.celebrations` | `CelebrationService` | Artifact generation |
| `api.reminders` | `ReminderService` | Reminder config management |
| `api.notifications` | `NotificationService` | Notification CRUD |
| `api.sharing` | `ShareLinkService` | Token generation, revocation |
| `api.guardian` | `GuardianService` | Anomaly detection, repair proposals |
| `api.transaction_memory` | `TransactionMemoryService` | Audit trail queries |
| `api.mayil` | `MayilService` | Insight analysis, proposals |
| `api.guided_experience` | `MayilGuidedExperienceService` | Guided tours, practice world |
| `api.canonical` | `CanonicalRepository` | Direct canonical read (used by DemoState UI routes) |
| `api.derived` | `DerivedRepository` | Projection queries |

---

## G. Mayil Implementation Map

### `MayilService` (services.py)
- **Role:** Primary AI reasoning surface
- **Methods:** `analyze_family_insights`, `generate_proposal`, `approve_proposal`, `reject_proposal`, `explain_resource_history`
- **Integration:** Accesses `CanonicalRepository` and `TransactionMemoryRepository` via service injections
- **No duplicate:** Single canonical implementation

### `MayilGuidedExperienceService` (services.py)
- **Role:** Learn-by-doing / watch journey guided sessions + Practice World seeding
- **Key models:** `GuideSessionState`, `MayilPracticeWorld`, `SceneDefinition` (all in models.py lines 665–722)
- **Methods:** Session creation, scene advancement, practice world seed/teardown, transaction verification per scene
- **No duplicate:** Single canonical implementation
- **Boundary with production:** PracticeWorld creates isolated entity sets that do NOT pollute the production `CanonicalRepository` — they are stored as dicts within `MayilPracticeWorld.simulated_*` lists

---

## H. Model Inventory (models.py — 729 lines)

### Enums (17 total)
`VisibilityLevel`, `EventStatus`, `EventCategory`, `DashboardEntryType`, `CelebrationArtifactType`, `MediaType`, `TimelineItemType`, `NotificationType`, `NotificationStatus`, `ShareResourceType`, `RecurrenceFrequency`, `ReminderType`, `ReminderStatus`, `ActionType` (17 values), `ResourceType` (15 values), `RelationshipType`, `Confidence`, `ProvenanceSourceType`, `ProposalStatus`, `ProposalType`, `AnomalySeverity`, `AnomalyType`, `RepairClassification`, `ContextType`, `AgeGroup`, `Language`, `GuideMode`

### Dataclasses (26 total)
`TransactionRecord`, `RecurrenceRule`, `ProvenanceMetadata` (frozen), `Person`, `Account`, `AuthenticatedSession`, `Relationship`, `FamilyContext`, `Consent`, `Place`, `Event`, `ReminderConfig`, `RichEventDetail`, `RichPersonDetail`, `DashboardProjectionEntry`, `DashboardSummary`, `CelebrationArtifact`, `Memory`, `MediaItem`, `MediaAlbum`, `SearchResultEntry`, `CalendarProjectionEntry`, `TimelineProjectionEntry`, `EventWithMemories`, `ContextDiscoveryResult`, `FamilyTopologyMember`, `FamilyTopologyResult`, `Notification`, `ShareLink`, `DataExportResult`, `ExportValidationResult`, `ActionProposal`, `InsightAnalysis`, `RepairProposal`, `AuditAnomaly`, `ValidationReport`, `SceneDefinition`, `GuideSessionState`, `MayilPracticeWorld`

### Utility Functions
- `_new_id()` → `uuid.uuid4()` string
- `_utc_now()` → `datetime.now(UTC).replace(tzinfo=None)` (⚠️ strips tzinfo after acquiring UTC — naïve datetime)

---

## I. Guided Experience / Practice World Boundary

### Boundary Definition
The `MayilGuidedExperienceService` maintains two distinct runtime modes:

| Mode | Data Destination | Affects Production? |
|---|---|---|
| `LEARN_BY_DOING` | Real `CanonicalRepository` | **YES** — user actions are real |
| `WATCH_JOURNEY` | `MayilPracticeWorld.simulated_*` lists | **NO** — isolated simulation |

### Protection Mechanism
Practice World data is stored exclusively as `Dict[str, Any]` lists within the `MayilPracticeWorld` dataclass instance (models.py lines 714–721). These are never written to `CanonicalRepository._events`, `._memories`, etc.

### Risk Flag (Audit Finding)
In `LEARN_BY_DOING` mode, scene completion produces real canonical entities and real `TransactionRecord` entries tagged with `source="guided_experience"`. These persist alongside user-generated data. **No cleanup mechanism for guided session artifacts was identified in the current codebase.** This is a known design gap, not a bug, but warrants future specification.

---

## J. DemoState Architecture (run.py)

`DemoState` (run.py, lines 56–373) is the runtime demo fixture:
- Instantiated once as `demo_state = DemoState()` at module load (line 376)
- `reset()` creates a fresh `FEMCApi()` and seeds: 3 persons, 3 accounts, family context, 4 events, 1 memory, 4 media items, 1 album, 1 reminder, 1 notification, 2 celebration artifacts, 2 share links, 1 insight
- `seed_demo_transactions()` populates the audit trail with a 7-step demonstration journey chain
- `switch_session()` and `onboard_member()` are UI helpers for the demo web server

---

## K. Guardian System

- `GuardianService` detects anomalies (`AuditAnomaly`) and proposes repairs (`RepairProposal`)
- Anomaly types: `DANGLING_REFERENCE`, `PROJECTION_DESYNC`, `PROVENANCE_MISSING`, `PRIVACY_INVARIANT_VIOLATION`, `TOPOLOGY_INCONSISTENCY`
- Repair classification: `DERIVED_ONLY` (safe, auto-executable) vs `CANONICAL_REPAIR` (requires human approval)
- Guardian repair actions are themselves recorded as `ActionType.GUARDIAN_REPAIR` transactions — full auditability confirmed

---

## L. Privacy / Authorization Architecture

- `AuthorizationService` enforces `VisibilityLevel` at read boundaries
- `PRIVATE` resources: only visible to the owner account
- `FAMILY`: visible to all `FamilyContext.member_ids`
- `PUBLIC`: unrestricted within context
- Transaction history applies the same authorization via `TransactionMemoryService.can_view_transaction()`
- Privacy isolation test (`test_privacy_authorization_isolation_bob_cannot_see_alice_private_transactions`) **PASSES** — confirming the authorization layer is correctly implemented

---

## M. Data Export / Import

- `api.export_family_context_for_session()` returns `DataExportResult` with `records` dict
- Export includes `"transactions"` key with full transaction audit trail
- Confirmed by passing test: `test_data_export_includes_transaction_history`
- Schema version: `"1.0"`

---

## N. Correlation Chain Tracing

- `TransactionRecord.correlation_id: Optional[str]` enables grouping related actions into a journey chain
- `api.transaction_memory.get_correlation_chain(account_id, fc_id, correlation_id)` retrieves all linked records
- Test `test_correlation_chain_tracing` **PASSES** (3 records in chain confirmed)

---

## O. Action Type Completeness (17 ActionTypes)

| ActionType | Coverage |
|---|---|
| CREATE, UPDATE, DELETE | Core CRUD |
| ATTACH, DETACH | Media linkage |
| GENERATE | Celebration artifact generation |
| SHARE, REVOKE_SHARE | Share link lifecycle |
| DOWNLOAD, IMPORT, EXPORT | Data portability |
| RESTORE | Recovery |
| REMINDER_CREATE, REMINDER_UPDATE, REMINDER_COMPLETE | Reminder lifecycle |
| NOTIFICATION_CREATE, NOTIFICATION_READ | Notification lifecycle |
| MAYIL_PROPOSAL, MAYIL_APPROVE, MAYIL_REJECT | AI proposal flow |
| PRIVACY_CHANGE | Consent/visibility modification |
| PERSPECTIVE_SWITCH | UI POV change |
| GUARDIAN_DETECT, GUARDIAN_REPAIR | Audit/repair cycle |

All 17 action types have corresponding `if/elif` dispatch paths in `api.py` or are passed through generically via `record_transaction_for_session()`.

---

## P. Open Items and Decisions Required

| # | Item | Priority | Decision Needed |
|---|---|---|---|
| 1 | **Timestamp collision bug** in `TransactionMemoryRepository.list_transactions()` causing 2 test failures | **HIGH** | Choose Option A (monotonic counter) or Option B (test-only fix) |
| 2 | `_utc_now()` strips tzinfo — all `TransactionRecord.timestamp` values are naïve datetimes | MEDIUM | Standardize on tz-aware or clarify convention |
| 3 | Guided Experience `LEARN_BY_DOING` creates persistent canonical artifacts with no cleanup | LOW | Decide if guided session artifacts need a separate cleanup API |
| 4 | `DemoState.reset()` creates fresh `FEMCApi()` but module-level `demo_state` is not thread-safe | LOW | Accept current single-threaded demo constraint or add locking |

---

## Q. Files Unchanged and Protected

The following files are **protected** per this audit. No modifications were made to any production code or test:

- `ENGINEERING/source/femc/models.py`
- `ENGINEERING/source/femc/repositories.py`
- `ENGINEERING/source/femc/services.py`
- `ENGINEERING/source/femc/api.py`
- `ENGINEERING/tests/test_femc_transaction_memory.py`
- `run.py`

---

*Audit performed at commit `ffe8105` on branch `reconcile/femc-execution-plan`. Audit is complete. No code was modified.*
