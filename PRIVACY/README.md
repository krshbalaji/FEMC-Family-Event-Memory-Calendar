# PRIVACY — Navigation and Area Mapping

Purpose
- Provide a canonical navigation note for the `PRIVACY/` area and document existing numeric prefix usage.

Authority
- Privacy policies and controls are governed by constitutional and architectural guidance.
- Conceptual authority model:

  CONSTITUTION
    ↓
  ARCHITECTURE
    ↓
  cross-cutting offices / domain offices
    ├── ENGINEERING — implementation authority
    ├── PRIVACY — privacy policy/control authority
    ├── MEMORY
    ├── MEDIA
    ├── CALENDAR
    ├── EVENTS
    └── other domain offices

- `PRIVACY` is a cross-cutting policy and control authority and is a peer to `ENGINEERING`. Treat privacy responsibilities as distinct from engineering implementation responsibilities.

Numbering collisions
- Some numeric prefixes appear multiple times in `PRIVACY/` and represent distinct responsibilities. Do not rename or conflate these folders automatically.

Duplicated numeric prefixes (documented — do not rename):
- 002:
  - `002-FAMILY-DATA-GOVERNANCE`
  - `002-FAMILY-PRIVACY-AND-CONSENT`
- 003:
  - `003-PRIVACY-ASSURANCE-AND-CLOSURE`
  - `003-PRIVACY-BY-DESIGN-AND-ASSURANCE`

Guidance
- Refer to the full folder names when citing privacy areas to avoid ambiguity. Add local `README.md` files inside folders that require explicit owner or contact information.

See also
- `CONSTITUTION/ACA_PACK000-CONSTITUTIONAL_MASTER_INDEX.md`
- `ARCHITECTURE/README.md`
