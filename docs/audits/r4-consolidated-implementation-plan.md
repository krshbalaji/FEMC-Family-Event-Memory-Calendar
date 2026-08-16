# FEMC R4 Consolidated Implementation Plan

## Candidate branch
`reconcile/femc-r4-consolidated`

## Objective
Bring the running FEMC experience toward the R4 target specimen while preserving the existing canonical domain architecture and Practice/Real isolation boundary.

## Workstreams

1. Memory/media experience: eliminate browser runtime errors; seed 2–3 coherent Practice memories and 3–5 linked media assets; expose memory detail and related media using existing domain relationships.
2. Exact sharing: resolve token to exact authorized Event, Memory, MediaItem, or Celebration destination; support copied-link/new-tab flow; revocation must fail closed.
3. Family edit: add/edit member flow in Practice mode with immediate projection and refresh continuity.
4. Calendar continuity: create event, project it, open exact event detail, preserve through navigation/refresh.
5. Celebrations: preserve one Studio entry point but make Card, Album, and Person Highlight produce distinct artifact types and presentation.
6. VEL Guardian: explain its purpose in plain language and keep branding consistent.
7. Mayil: improve visual presence and maintain one warm mature feminine identity across English, Tamil, and Hindi; avoid claiming a particular browser voice quality without verification.
8. Trial: reliable Practice entry and clear Practice Mode indication.
9. Settings/Activity: remove misleading invalid/empty states where the underlying Practice export/history is valid.
10. Hygiene/tests: focused regressions, full pytest, diff check, and real browser verification in the user's Windows checkout.

## Evidence rule
No GREEN claim without real browser evidence. Backend/API/pytest success is necessary but insufficient.

## Architecture rule
Prefer thin presentation/read-model changes. Do not create parallel domain or persistence models.
