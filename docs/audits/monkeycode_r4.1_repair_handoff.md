# FEMC R4.1 — Browser-Proven Repair Handoff

## Starting branch
`reconcile/femc-builder-monkeycode`

## Starting commit
`cbf2f45d7221619c68cbe77b593b1f2d367b77ae`

## Repair branch
`reconcile/femc-r4.1-browser-repair`

## Mission

Take the MonkeyCode R4 implementation and finish the product against the FEMC R4 Target Specimen contract. This is a repair pass, not a fresh redesign.

The real Windows browser is the acceptance authority. Do not claim GREEN from pytest alone.

## Authoritative references

Read first:

- `docs/specimens/r4/README.md`
- `docs/specimens/r4/target/README.md`
- `docs/specimens/r4/target/00-master-build-prompt.md`
- `docs/specimens/r4/target/target-contract.md`
- `docs/specimens/r4/target/00-master-target-board.png`
- GitHub Issue #1: `R4 consolidated browser defects from local MonkeyCode verification`

## Verified browser defects to repair

### P0/P1

1. **Memory** — browser error: `generate_media_download_filename is not defined`.
2. **Media** — screen remains unusable/error along the same runtime path.
3. **Exact Event Share** — generated link opens Home instead of exact Event detail.
4. **Exact Memory / Media / Celebration Share** — cannot be accepted until upstream resource paths work and exact-resource navigation is proven.
5. **Celebration artifacts** — Card / Album / Person Highlight generate, but linked artifact/file handling is incomplete.
6. **Mayil visual** — old assistant presentation remains; bring it toward the target specimen.
7. **Mayil voice** — current observed state is English female, Tamil male, Hindi silent; required contract is one coherent feminine identity across all three languages.
8. **Family Edit** — must be clearly available, functional, and persistent through navigation + refresh.
9. **Mobile** — verify responsive behavior around 375x812 with no destructive overflow.

## Preserve known working behavior

Do not regress:

- Trial entry
- Trial refresh behavior
- Trial exit to Real mode
- Practice/Real isolation
- Revoked share rejection
- Calendar listing/detail
- Family Add
- VEL Guardian branding
- TransactionMemory boundary
- Trial Observer boundary

## Required acceptance chain

For every repaired flow:

`ACTION → STATE → PROJECTION → VISIBLE RESULT → UNDERSTANDING`

## Practice dataset

Keep the Practice dataset small and coherent:

- 2–3 meaningful memories
- 3–5 linked media assets

Reuse existing FEMC domain relationships. Do not create a parallel data model or bulk filler gallery.

## Required browser verification

Run the real application in the Windows browser and verify:

1. Memory
2. Media
3. Family Edit
4. Calendar Event Detail
5. Celebration Card
6. Celebration Album
7. Person Highlight
8. Exact Event Share in a new tab
9. Exact Memory Share in a new tab
10. Exact Media Share in a new tab
11. Exact Celebration Share in a new tab
12. Revoked Share
13. Trial Entry
14. Trial Refresh
15. Trial Exit → Real
16. Mayil English
17. Mayil Tamil
18. Mayil Hindi
19. VEL Guardian
20. Mobile 375×812

## Required automated checks

```text
python -m pytest -q
git diff --check
```

Also run JavaScript syntax checks where applicable.

## Browser evidence

Capture new verification screenshots under:

`docs/specimens/r4/target/verification/`

Do not overwrite or replace the immutable baseline evidence.

## Deliverable

Create:

`docs/audits/monkeycode_r4.1_browser_repair_report.md`

Include:

- branch name
- starting commit
- repair commit SHA
- files changed
- automated test results
- browser environments
- screenshot evidence
- target specimen matrix
- remaining P0/P1/P2 defects
- final technical / engineering / experience verdict
- experience score /10
- recommendation: `MERGE`, `REPAIR AGAIN`, or `REJECT`

## Guardrails

- Work only on `reconcile/femc-r4.1-browser-repair`.
- Do not modify or push the canonical branch.
- Do not hide exceptions merely to make the screen appear successful.
- Do not introduce a parallel architecture.
- Do not claim browser success without browser evidence.
