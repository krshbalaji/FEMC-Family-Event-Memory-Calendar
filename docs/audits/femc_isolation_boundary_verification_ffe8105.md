# FEMC Isolation Boundary Verification Report
**Audit Reference Commit:** `ffe8105`<br>
**Classification:** Technical Audit<br>
**Boundary Status: 🔴 RED (NON-ISOLATED)**

---

## Executive Summary
This audit report documents the forensic verification of the boundary isolation mechanism in the FEMC "Learn-By-Doing" guided experience mode.

The audit establishes that the **"Learn-By-Doing" (Guided Tour) mode has ZERO database isolation in the backend**. Interactive steps designed to let users practice scheduling events, adding memories, or uploading media actually execute on the production databases (`CanonicalRepository` and `DerivedRepository`). These actions persist indefinitely and are not rolled back on tour exit or page reset.

Conversely, the **"Practice World" (Safe Simulation Experience)** is fully isolated via a segregated in-memory sandbox (`MayilPracticeWorld`) that prevents any production writes.

---

## Detailed Operation Tracing
The table below traces the execution paths for the 8 core operations under both simulated and guided modes:

| Operation | Learn-By-Doing (Guided Tour) Execution Path | Practice World Sandbox Execution Path | Boundary Leak Risk |
| :--- | :--- | :--- | :--- |
| **1. Create Person** | Client calls standard `/api/family/onboard` $\to$ delegates to `demo_state.onboard_member()` $\to$ registers person globally in `CanonicalRepository`. | Clients call `/api/guide/practice/action` (Action: `CREATE`, Resource: `PERSON`) $\to$ appends to `pw.simulated_persons` list. | **🔴 LEAK** (Saves real person) |
| **2. Create Event** | Client calls standard `/api/events/create` $\to$ delegates to `api.create_event_for_session(...)` $\to$ writes to global `canonical.events` and calendars. | Clients call `/api/guide/practice/action` (Action: `CREATE`, Resource: `EVENT`) $\to$ appends to `pw.simulated_events` list. | **🔴 LEAK** (Saves real event) |
| **3. Create Memory** | Client calls standard `/api/memories/create` $\to$ delegates to `api.create_memory_for_session(...)` $\to$ writes to global `canonical.memories`. | Clients call `/api/guide/practice/action` (Action: `CREATE`, Resource: `MEMORY`) $\to$ appends to `pw.simulated_memories` list. | **🔴 LEAK** (Saves real memory) |
| **4. Create Media** | Client calls standard `/api/media/create` $\to$ delegates to `api.create_media_for_session(...)` $\to$ writes to global `canonical.media_items`. | Clients call `/api/guide/practice/action` (Action: `CREATE`, Resource: `MEDIA`) $\to$ appends to `pw.simulated_media_items` list. | **🔴 LEAK** (Saves real media metadata) |
| **5. Create Celebration** | Client calls standard `/api/celebrations/generate` $\to$ delegates to `api.generate_celebration_artifact(...)` $\to$ writes to `derived.celebration_artifacts`. | Clients call `/api/guide/practice/action` (Action: `CREATE`, Resource: `CELEBRATION_ARTIFACT`) $\to$ appends to `pw.simulated_celebrations`. | **🔴 LEAK** (Saves real celebration) |
| **6. Share Link** | Client calls standard `/api/sharing/create` $\to$ delegates to `api.create_share_link(...)` $\to$ writes to global `canonical.share_links`. | Clients call `/api/guide/practice/action` (Action: `CREATE`, Resource: `SHARE_LINK`) $\to$ appends to `pw.simulated_share_links`. | **🔴 LEAK** (Saves live share token) |
| **7. Revoke Share** | Client calls standard `/api/sharing/revoke` $\to$ delegates to `api.revoke_share_link(...)` $\to$ modifies `canonical.share_links` globally. | Clients call `/api/guide/practice/action` (Action: `REVOKE`, Resource: `SHARE_LINK`) $\to$ removes from `pw.simulated_share_links`. | **🔴 LEAK** (Mutates live share token) |
| **8. Export** | Client calls standard `/api/export` $\to$ returns full real production database history from the live repositories. | Client calls `/api/guide/practice/history` $\to$ prints summary from `pw.simulated_transactions` list only. | **🟢 SAFE** (Read-only, but reads real data in LBD) |

---

## The Critical Experiment
To mathematically verify state leak, we performed the following counts audit:
1. Seeded the system state.
2. Initialized `LEARN_BY_DOING` (Guided Tour) mode.
3. Executed a single Learn-by-Doing exercise: Event Creation (simulating Step 3 of the guided onboarding).
4. Inspected the live repository database counts.
5. Called guided tour exit and reset methods, then inspected the counts again.

### Counts Log Result
```
COUNTS: BEFORE Entering Learn-by-Doing
  persons:       3
  events:        4
  memories:      1
  media:         4
  celebrations:  2
  share links:   2
  transactions:  0
  [Simulated] State: Not Initialized

--- Creating Event (LBD Action) ---
  Created Event ID: 91d02848-a0bd-4c50-ae6b-85178bd42f5f

COUNTS: AFTER LBD Event Creation
  persons:       3
  events:        5            <-- Real Event count increased!
  memories:      1
  media:         4
  celebrations:  2
  share links:   2
  transactions:  0            <-- User transaction counter remained unchanged
  [Simulated] persons:       5
  [Simulated] events:        2
  [Simulated] memories:      1
  [Simulated] media:         1
  [Simulated] celebrations:  1
  [Simulated] share links:   1
  [Simulated] transactions:  1

--- Exiting & Resetting Guided Experience ---

COUNTS: AFTER Exit & Reset
  persons:       3
  events:        5            <-- Real Event creation persists!
  memories:      1
  media:         4
  celebrations:  2
  share links:   2
  transactions:  0
```

### Experiment Conclusion
Any data mutated during `LEARN_BY_DOING` mode directly alters the production datastore. **There is no sandboxing context check, write interception, or rollback.** The data remains in the database even after the user exits or resets the guided experience.

---

## Dynamic Property Initialization Defect
During the audit, we uncovered a backend crash risk when executing `api.exit_practice_world_for_session` or calling helper properties prior to a practice world's initialization:

### Code Snippet (`services.py:L3300-3301`)
```python
    def get_or_create_practice_world(...):
        if not hasattr(self, "practice_worlds"):
            self.practice_worlds: Dict[str, MayilPracticeWorld] = {}
```

*   **Root Cause:** The `practice_worlds` instance dictionary is lazily initialized only when `get_or_create_practice_world` is invoked.
*   **Crash Vector:** If a client initiates a Guided Tour session (which does not start the practice world) and subsequently invokes `/api/guide/practice/exit` (which calls `exit_practice_world`), the python interpreter raises:
    `AttributeError: 'MayilGuidedExperienceService' object has no attribute 'practice_worlds'`
*   **Recommendation:** Move `self.practice_worlds: Dict[str, MayilPracticeWorld] = {}` to the `__init__` constructor of `MayilGuidedExperienceService` to guarantee safe property availability.

---

## Architectural Recommendation
To resolve this split personality:
1. **Redirection of REST APIs:** If the active session state has `GuideMode.LEARN_BY_DOING`, standard mutations in `run.py` should be redirected to target `execute_simulated_action` rather than the live service APIs.
2. **Explicit Naming:** The user interface should clearly segment between "Watch Tour", "Safe Simulation Sandbox" (Practice World), and "Active Trial writes" so that users are never misled about when they are altering real family records.
