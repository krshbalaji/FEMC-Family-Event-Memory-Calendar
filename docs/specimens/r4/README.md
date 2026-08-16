# FEMC R4 — Target Specimens

These artifacts are **TARGET DESIGN REFERENCES** for the completed FEMC R4 product. They are not screenshots of the current implementation and must not be treated as evidence that the current repository already behaves this way.

## Purpose

The target specimen pack communicates the visual and behavioral outcome expected from the existing FEMC repository after R4 implementation.

## Builder contract

Builders must use the existing FEMC repository, domain models, services, routes, seeded content, and safety boundaries. The specimen pack is the visual/UX target; the repository is the implementation base.

Acceptance chain:

`USER ACTION → STATE CHANGE → PROJECTION → VISIBLE RESULT → UNDERSTANDING`

Passing backend tests alone is not sufficient.

## Core requirements

- Practice/Real isolation remains intact.
- Practice memories: 2–3 only.
- Practice media assets: 3–5 total only.
- Reuse existing FEMC relationships: `Memory → MediaItem → exact resource ID`.
- No bulk gallery filler or parallel media model.
- Exact-resource sharing is mandatory: token → exact resource → authorization → exact detail.
- Revoked links must fail.
- Token A must never resolve Resource B.
- User-facing sharing should identify the resource by title/caption/context, not opaque token text.
- Mayil remains one coherent mature, warm, elegant feminine character across supported languages.
- VEL Guardian must be clearly explained to a first-time user.

## Specimen status

This branch contains the target-specimen reference only. It does not modify the product implementation.

## Evidence separation

- `docs/specimens/r4/` = target references
- `docs/specimens/r4/target/` may hold future target-state iterations
- Baseline/runtime evidence must never be overwritten or mixed with target references.
