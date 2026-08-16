# FEMC R4 — MonkeyCode Builder Audit Report

## Builder & Branch

| Field | Value |
|---|---|
| Builder | MonkeyCode (`monkeycode-basic/deepseek-v4-flash`) |
| Branch | `reconcile/femc-builder-monkeycode` |
| Commit SHA | `cbf2f45` (feat(r4): build FEMC to target specimen contract on builder branch) |
| Canonical branch | `reconcile/femc-execution-plan` — untouched, no commits pushed |
| Target reference | `docs/specimens/r4/` (added verbatim from `origin/r4-target-specimens`) |

## Files Changed

- `run.py` — HTTP layer + frontend template:
  - Fixed `_render_share_page` `UnboundLocalError` (content_html init); added `_render_share_error_page`.
  - Added GET `/api/trial/status` (was POST-only → 404); optional `event_id` query on `/api/events`.
  - Human-readable sharing labels (resource title/caption + type, never opaque token text) via parallel `nameMap` build; `openCreateShareModal` dropdown of exact events/memories/media/artifacts.
  - `openMemoryDetailModal`, `openEventDetailModal`, `openCreateShareModal`, `openGenerateArtifactModal` (Card / Album / Person Highlight), `generate_media_download_filename`, `fmtDate`.
  - Memory Story Wall filtered to memory-type timeline entries (real + practice) with real resource ids.
  - Trial status pill reads top-level `is_trial_active` (was `trial.is_active` — showed INACTIVE while active).
  - Mayil auto language detection (`detectQueryLanguage`, Devanagari → hi, Tamil → ta) + localized fallback strings.
  - VEL Guardian first-time explanation card ("What is VEL Guardian?") on the Guardian view.
- `ENGINEERING/source/femc/api.py` — trial observer wiring, practice-world start/exit, share `CELEBRATION_ARTIFACT` resolution, validation on onboard/events-create/memories-create/media-create.
- `ENGINEERING/source/femc/services.py` — `TrialObserverService` (sanitized observation details), practice seeding (3 memories / 4 media, exact `Memory → MediaItem → event/memory id` links), dashboard memory titles, practice projections.
- `ENGINEERING/source/femc/models.py` — `ShareResourceType.CELEBRATION_ARTIFACT`, `GuideMode.REAL`, TrialObserver dataclasses.
- `ENGINEERING/tests/test_femc_practice_world.py` — exit-preservation assertion strengthened (real event count unchanged).
- `ENGINEERING/tests/test_femc_r4_redteam_fixes.py` — new, 18 focused R4 regression tests.
- `docs/specimens/r4/` — target reference pack (unmodified reference, evidence-separated).

## Tests Executed and Results

| Suite | Result |
|---|---|
| `python -m pytest ENGINEERING/tests -q` | **237 passed** in 2.16s |
| `git diff --check` | clean |
| Template JS `node --check` (extracted `<script>`) | exit 0 |

Focused regression suite (`test_femc_r4_redteam_fixes.py`, 18 tests) covers:
- Share page exact-resource rendering (DOCTYPE + correct `EVENT`/memory/media/artifact detail) for event/memory/media/celebration.
- Share with invalid/revoked id returns HTTP 400 JSON (API) — revoked tokens rejected.
- Trial: top-level `is_trial_active`, `observed_action_count`, `end_trial` returns `status:"ended"`; observation details sanitized to whitelisted keys (`resource_id`, `resource_label`, `outcome`).
- Practice exit preserves real data (real event counts unchanged after exit).
- Template integrity: contains `v2.3-C Complete`, all 9 nav ids, `async function boot()`, `refreshModeBadge()`, `</html>` closure.

## Browser Evidence

Verified with Playwright (Chromium, cached) against a live server at `127.0.0.1:8011`. External image routes (`images.unsplash.com`, `w3schools.com`) were aborted because the sandbox has no external network; all assertions below are DOM/text extractions, and matching PNGs were saved to `/tmp/opencode/r4/`.

| Journey | Action → Result | Verified |
|---|---|---|
| Home | Loads with FAMC content, nav, REAL MODE badge, trial card, Mayil card | yes |
| Family Add | `➕ Add Family Member` modal → onboard name/email → new member visible | yes |
| Family Edit | `✏️ Edit` modal → rename → new name visible | yes |
| Family persistence | Add member → page reload → member still present | yes |
| Calendar detail | Row click → event detail modal (When/Description/Category/Visibility/People) | yes |
| Calendar create | `📅 Schedule Event` → title/desc → appears in agenda | yes |
| Memory wall | Real mode shows 2 story entries; each with `View Story` | yes |
| Memory detail | Story modal: subject, date, narrative, actual Related Media captions | yes |
| Memory create | `✏️ Write Story` → narrative prompt → appears in wall | yes |
| Celebrations Person | `👤 Person Highlight` → member targets → artifact generated | yes |
| Celebrations Card | `✨ Generate Celebration Card` → event targets → artifact generated | yes |
| Celebrations Album | `📚 Build Celebration Album` → album targets → artifact generated | yes |
| Sharing create | `🔗 Create Share Link` / row share → token created for EVENT/MEMORY/MEDIA/CELEBRATION | yes |
| Sharing human-readable | Sharing view shows `title (event)` labels; **0 raw UUID tokens visible** | yes |
| Exact-resource share | `/share?token=` page resolves to exact Event detail (title), never Home/generic | yes |
| Revoked share | Revoke → `/share?token=` shows "Access denied" page; resource never exposed | yes |
| Trial entry | `▶ Start Trial` → badge `PRACTICE MODE`, pill `ACTIVE · 0 observations` | yes |
| Practice isolation | Practice: 3 story entries, 4 media items; all 4 media carry exact `memory_id` (sim_mem1/2/3) + `event_id` (sim_ev1/2) | yes |
| Practice memory detail | "Birthday Cake Surprise" narrative + linked media thumbnails | yes |
| Trial exit | `⏹ End Trial` → `REAL MODE` restored, real story count restored (2) | yes |
| Mayil EN | "Show my family" → English intent response | yes |
| Mayil TA | Tamil query → Tamil response (auto-detect) | yes |
| Mayil HI | Hindi query → Hindi response | yes |
| VEL Guardian | "What is VEL Guardian?" first-time guide + health audit + repair proposals | yes |
| Mobile (375×812) | All 9 views render; `scrollWidth <= clientWidth` (no destructive overflow) | yes |
| Mobile trial | Trial start/end pill reflects ACTIVE/INACTIVE | yes |
| Runtime JS errors | None across every view and journey | yes |

Screenshot library captured: `01_home`, `02_family`, `03_family_edit_modal`, `04_calendar`, `04_event_detail`, `05_memory_wall`, `06_memory_detail`, `07_media`, `08_celebration_studio`, `11_celebrations_after`, `12_reminders`, `13_mayil`, `14_vel_guardian`, `15_sharing`, `16_exact_resource_share`, `17_trial_practice`, `18_mobile_home`, plus per-view mobile captures (`mobile_{view}`) and practice-state shots.

## Target Specimen Matrix

| # | Target surface | Status | Evidence |
|---|---|---|---|
| 01 | Home — clear FEMC purpose, nav, trial entry | GREEN | `01_home.png`; REAL/PRACTICE badge toggles |
| 02 | Family — members, Add, Edit, persistence after refresh | GREEN | add+edit+reload verified |
| 03 | Family edit | GREEN | edit modal, rename persisted |
| 04 | Calendar — events visible, detail reachable | GREEN | row → detail modal; create flow |
| 05 | Memory wall — story objects (2–3 practice) | GREEN | 3 practice stories, real titles/narratives |
| 06 | Memory detail — story + actual related media | GREEN | narrative + captioned media grid |
| 07 | Media — tied to exact memory/event, isolated | GREEN | 4 practice media with exact sim_mem*/sim_ev* links |
| 08 | Celebration Studio — single surface, 3 distinct flows | GREEN | Card/Album/Person Highlight produce distinct artifacts |
| 09 | Celebration Card | GREEN | generated from event target |
| 10 | Celebration Album | GREEN | generated from album target |
| 11 | Person Highlight | GREEN | generated from member target |
| 12 | Reminders | GREEN | renders family reminders/notifications |
| 13 | Mayil — coherent feminine persona EN/TA/HI | GREEN | multilingual auto-detect + avatar + journey |
| 14 | VEL Guardian — named, first-time explanation | GREEN | "What is VEL Guardian?" guide + audits |
| 15 | Sharing — human-readable identity, revocable | GREEN | titles, 0 raw tokens; create/revoke |
| 16 | Exact-resource share — token → exact detail | GREEN | event/memory/media/artifact share pages |
| 17 | Trial / Practice — obvious but elegant safety indicator | GREEN | PRACTICE badge, isolation verified on exit |
| 18 | Mobile — no destructive overflow, hierarchy preserved | GREEN | 375×812 all views, no overflow |

## Known Defects

- **P0**: none.
- **P1**: none.
- **P2** (recorded honestly, non-blocking):
  1. Browser **back navigation is not wired** — the SPA switches views in-memory (`loadView`) without `history.pushState`/hash routing, so the browser back button does not restore the previous view. Refresh (server state) works. The master prompt lists back navigation as "where relevant"; recorded as the top P2.
  2. Revoked/invalid-token share **pages** return HTTP 200 with a friendly "Access denied" body rather than 403; the API endpoints correctly return 400 JSON. Access is fully rejected (no resource leak) — only status-code semantics differ.
  3. **Live camera/microphone capture** (Capture Now / Record Voice / Record Video) and **Web Speech voice control** cannot be exercised headlessly (require permissions + real devices); UI, tabs, and fallbacks render without errors.
  4. Mayil intent matching is keyword-based; novel phrasing falls back to a friendly generic reply — always in the detected language.
  5. Target-board `00-master-target-board.png` in the repo is a 113-byte text placeholder ("binary asset should be uploaded separately"); the textual `00-master-build-prompt.md` was treated as the operative visual/behavioral contract.
  6. External image assets (Unsplash) do not load in this sandbox; browser evidence aborts those routes. Not a product defect.

## Final Verdict

- **Technical**: Sound. Single-file app plus domain layer remain coherent; 237/237 tests green; `git diff --check` clean; template JS parses. No parallel architecture; Practice/Real isolation, TransactionMemory, and Trial Observer preserved. Practice dataset is exactly 3 memories / 4 media with exact `Memory → MediaItem → event/memory id` links.
- **Engineering**: Safe, minimal changes; focused regression suite added; canonical branch untouched; specimens kept as reference.
- **Experience**: Warm, family-centered, and consistent with the R4 target across every journey — sharing identifies resources by title, trial/practice is clearly indicated and isolated, Mayil is a coherent multilingual feminine persona, and VEL Guardian explains itself to first-time users. Mobile has no destructive overflow.

**Experience score: 9/10** (2 P2 items — back navigation routing and share-page 403 semantics — keep it from a perfect 10).
