# FEMC R4 — TARGET-SPECIMEN MASTER BUILD PROMPT

## Mission

Build the existing FEMC repository into the completed product represented by the **FEMC R4 Target Specimen Pack**.

The target specimen pack is a visual/product contract. It is not a claim about current implementation.

Use:
- the existing FEMC repository and its current architecture;
- `docs/specimens/r4/target/00-master-target-board.png` as the primary visual reference;
- the target contracts in this folder as the behavioral reference.

## Non-Negotiable Principles

1. Inspect the repository before editing.
2. Preserve existing domain models, services, routing, Practice/Real isolation, TransactionMemory, and Trial Observer unless a change is strictly required to satisfy a target contract.
3. Do not build a parallel architecture just to reproduce a screen.
4. Do not treat HTTP 200, unit-test success, or source inspection as user-experience acceptance.
5. Acceptance is: **ACTION → STATE → PROJECTION → VISIBLE RESULT → UNDERSTANDING**.
6. Real browser verification is mandatory for completed candidate work.
7. Do not claim GREEN without browser evidence.
8. Work only on the assigned builder branch. Do not modify the canonical branch.

## Target Experience

The completed FEMC product should feel warm, premium, family-centered, emotionally meaningful, trustworthy, calm, modern, and human. Avoid generic admin-console styling, childish visuals, excessive decoration, and unrelated redesign.

## Core Target Areas

### Home
Clear FEMC purpose, coherent family content, obvious primary navigation, and clear entry into Practice Trial.

### Family
Family members with relationship/context, Add Member, and clear Edit actions. Changes remain visible after navigation and refresh.

### Calendar
Family events are visible and understandable. Opening an event reaches the appropriate event detail.

### Memory
Use only a small coherent Practice dataset: 2–3 meaningful memories and roughly 3–5 linked media assets. A memory is a real story object with title, narrative, date/event context, people/context, and related media. The memory detail view should show the story and its actual related media.

### Media
Media are tied to valid FEMC memory/event context. Do not create a giant gallery or parallel media model. Practice media remain isolated from canonical Real data.

### Celebration Studio
A single Studio surface is acceptable, but Card, Album, and Person Highlight must be substantively different flows and resulting artifacts, not merely different headings.

### Reminders
Readable family-oriented reminders and upcoming items.

### Mayil
One coherent mature feminine identity across English, Tamil, and Hindi. The experience should feel warm, elegant, calm, confident, and premium, with restrained arrival, breathing, speaking, thinking, and success states.

### VEL Guardian
Use the exact user-facing name **VEL Guardian**. The user should understand within seconds that it protects family privacy, safety, and data consistency in the background.

### Sharing
Human-readable resource identity. A share token is an internal mechanism, not the user's primary resource identity.

**Exact-resource rule:**
- Event share → exact Event detail
- Memory share → exact Memory detail
- Media share → exact Media detail
- Celebration share → exact Celebration detail

Never resolve a share link to the Home page, a generic section, or a search page.

A valid share flow is:
`token → exact resource resolution → authorization → exact resource detail`

Revoked tokens must fail, and token A must never resolve resource B.

### Trial / Practice
Clear entry into Practice Mode with an obvious but elegant safety indicator. Practice actions must not mutate canonical Real data.

### Mobile
Responsive behavior with no destructive overflow and preserved action hierarchy.

## Build Method

For each target specimen:
1. identify current implementation;
2. trace the user action end-to-end;
3. implement the minimum safe change needed;
4. add focused regression coverage where appropriate;
5. run the full automated suite;
6. verify the real browser flow;
7. capture evidence of the resulting state;
8. record remaining defects honestly.

## Required Verification

Run at minimum:

```text
python -m pytest -q
git diff --check
```

For browser acceptance, test the critical target journeys end-to-end, including:
- Family add/edit
- Calendar event creation/detail
- Memory creation/detail/persistence
- Media display/creation where supported
- Celebration Card / Album / Person Highlight
- Exact-resource sharing in a new browser tab
- Revoked share rejection
- Mayil English/Tamil/Hindi behavior
- VEL Guardian comprehension
- Trial entry and Practice isolation
- refresh, back navigation, and mobile width where relevant

## Target Dataset Constraints

For seeded Practice memory/media, do not create bulk content. Prefer a coherent set of 2–3 memories and 3–5 media assets, reusing existing domain relationships and existing seed assets where suitable.

## Deliverable

Every builder must produce:

`docs/audits/<AI_NAME>_r4_build_report.md`

with:
- branch name
- commit SHA
- files changed
- tests executed and results
- browser evidence
- target specimen matrix
- known P0/P1/P2 defects
- final technical / engineering / experience verdict
- experience score /10

## Final Rule

The target screenshots define what the completed product should look and feel like. The existing repository defines the architecture and available domain capabilities. The builder's job is to bring the two together without sacrificing safety or correctness.

Do not commit to or push the canonical branch.
