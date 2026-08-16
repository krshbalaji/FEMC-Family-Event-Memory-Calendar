# FEMC R4 — Experience Specimen Pack

## Purpose

This folder is a frozen UX reference pack for independent FEMC builders and red-team reviewers.

These specimens capture the current local Practice/Trial experience and the user-visible defects discovered during manual testing. They are **reference evidence**, not final acceptance screenshots.

## Acceptance rule

Every major capability must satisfy:

**USER ACTION → STATE CHANGE → PROJECTION → VISIBLE RESULT → USER UNDERSTANDING**

A backend `200 OK` or passing unit test is not sufficient for experience acceptance.

## Specimen map

| File | Surface | What to evaluate |
|---|---|---|
| `01-home.png` | Home | First impression and obvious start point |
| `02-family.png` | Family | Member visibility, add/edit continuity |
| `03-calendar.png` | Calendar | Event creation, visibility and detail |
| `04-memory.png` | Memories | Existing stories, creation, projection and media |
| `05-media.png` | Media | Media creation, rendering and exact resource behavior |
| `06-celebrations.png` | Celebrations | Card / Album / Person Highlight differentiation |
| `07-reminders.png` | Reminders | Clear alerts and understandable state |
| `08-mayil.png` | Mayil | Character, voice, elegance and guidance |
| `09-vel-guardian.png` | VEL Guardian | Immediate understanding of purpose |
| `10-sharing.png` | Sharing | Human-readable context, token handling and deep links |
| `11-activity.png` | Activity | Transaction/history clarity |
| `12-settings.png` | Settings / Data | Export/schema truthfulness |
| `13-trial-entry.png` | Trial | Practice entry and visible Practice Mode |
| `14-exact-share.png` | Exact share destination | Copied share URL must open the exact shared resource |

## Important notes

1. Several screenshots intentionally show broken or incomplete behavior. Do not reproduce a defect merely because it appears in a specimen.
2. Improve the underlying experience while preserving the existing FEMC domain model and Practice/Real isolation.
3. Do not create bulk fake content. For the Practice memory experience, use only **2–3 coherent memories** and approximately **3–5 total media assets**.
4. Reuse existing FEMC `Memory`, `MediaItem`, `Event`, `MediaAlbum`, `ShareLink`, and related domain relationships wherever possible.
5. Share links may contain opaque internal tokens, but the visible UX must identify the shared resource by title/caption/context.
6. A share URL must resolve to the **exact authorized resource**, not merely to Home, a generic section, or a search page.
7. Reopening a revoked share token must fail safely.
8. Do not expose personal information, secrets, credentials, or real private family content in any new specimen or implementation.

## Builder deliverable

Every independent builder should create its own branch, implement the improvements, run automated tests, perform real browser verification, and submit a branch report including:

- files changed
- tests run and results
- browser evidence
- specimen-by-specimen PASS/FAIL
- experience score /10
- remaining P0/P1/P2 issues
- final commit SHA

## Baseline observation

The current manual experience score reported during the R4 cycle was approximately **5/10**. Known defects include Memory/Media loading failures, insufficient Celebration differentiation, missing Family edit, weak share deep-linking, opaque share context, and Mayil presentation/voice polish gaps.
