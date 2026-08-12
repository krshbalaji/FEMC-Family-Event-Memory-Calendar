# ENGINEERING — Navigation and Authority

Purpose
- Provide a canonical navigation and authority note for the `ENGINEERING/` area.
- Explain how to interpret the numeric prefixes and the existing sub-area structure without renaming or moving any folders.

Authority
- Engineering guidance and implementation practices are subordinate to `ARCHITECTURE` and `CONSTITUTION`.
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

- `ENGINEERING` is a cross-cutting implementation authority and is a peer to `PRIVACY`. Use the full folder name when referencing areas to avoid ambiguity.

Numbering and collisions
- The repository uses numeric prefixes on `ENGINEERING/` subfolders. Several numeric prefixes intentionally appear more than once and represent distinct responsibilities rather than duplicates. Do not renumber or merge automatically.

Duplicated numeric prefixes (documented — do not rename):
- 002:
  - `002-ENGINEERING-DELIVERY-AND-QUALITY`
  - `002-IMPLEMENTATION-GOVERNANCE`
- 003:
  - `003-ENGINEERING-REPOSITORY-AND-DEVELOPMENT`
  - `003-QUALITY-ENGINEERING`
- 004:
  - `004-DOMAIN-IMPLEMENTATION-DESIGN`
  - `004-TESTING-AUTOMATION-AND-CI`
- 005:
  - `005-DATA-IMPLEMENTATION-DESIGN`
  - `005-RELEASE-DEPLOYMENT-AND-OPERATIONS`
- 006:
  - `006-ENGINEERING-ASSURANCE-AND-CLOSURE`
  - `006-SECURITY-IMPLEMENTATION`
- 007:
  - `007-API-AND-INTEGRATION-IMPLEMENTATION`
  - `007-OBSERVABILITY-PERFORMANCE-AND-RELIABILITY`
- 008:
  - `008-AI-IMPLEMENTATION-GOVERNANCE`
  - `008-MAINTENANCE-TECHNICAL-DEBT-AND-DEPENDENCIES`
- 009:
  - `009-ENGINEERING-CLOSURE-AND-CONTINUOUS-EVOLUTION`
  - `009-MEDIA-AND-SEARCH-IMPLEMENTATION`

Guidance
- Treat each folder as a distinct responsibility area. When referencing an engineering area, use the full folder name (including the descriptive suffix) to avoid ambiguity.
- If a canonical owner is required for a numbered area, document it at the folder level by adding a `README.md` inside that folder listing owner and responsibilities.
- This `ENGINEERING/README.md` is a navigation aid and does not change any file or folder.
- Engineering and Privacy are peer cross-cutting authorities; do not treat privacy as a subdomain of engineering or vice versa.

See also
- `CONSTITUTION/ACA_PACK000-CONSTITUTIONAL_MASTER_INDEX.md`
- `ARCHITECTURE/README.md`
