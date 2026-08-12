# FEMC Reconciliation Execution Plan

This execution plan records the approved BM decisions for reconciling the FEMC architecture repository. It is a plan only: no file changes, renames, moves, merges, deletes, archives, commits, or pushes should be executed until this plan is formally reviewed.

## A. Exact safe changes approved by BM

1. Remove only the exact wrong-domain duplicate media copies in the `MEMORY` domain:
   - `MEMORY/004-MEDIA-PROCESSING-ALBUMS-AND-DISCOVERY/MEDIA_ALBUM_AND_COLLECTION_MODEL.md`
   - `MEMORY/004-MEDIA-PROCESSING-ALBUMS-AND-DISCOVERY/MEDIA_PROCESSING_AND_TRANSCODING_MODEL.md`
   - `MEMORY/004-MEDIA-PROCESSING-ALBUMS-AND-DISCOVERY/MEDIA_SEARCH_AND_DISCOVERY_MODEL.md`
   - `MEMORY/005-MEDIA-INTELLIGENCE-AND-SHARING/MEDIA_ACCESSIBLE_PRESENTATION_MODEL.md`
   - `MEMORY/005-MEDIA-INTELLIGENCE-AND-SHARING/MEDIA_AI_ANALYSIS_AND_TRANSFORMATION_GOVERNANCE.md`
   - `MEMORY/005-MEDIA-INTELLIGENCE-AND-SHARING/MEDIA_SHARING_AND_EXTERNAL_DELIVERY_MODEL.md`
   - `MEMORY/006-MEDIA-ASSURANCE-AND-CLOSURE/MEDIA_CLOSURE_AND_CONTINUOUS_EVOLUTION.md`
   - `MEMORY/006-MEDIA-ASSURANCE-AND-CLOSURE/MEDIA_NEGATIVE_TESTING_EXPANDED.md`
   - `MEMORY/006-MEDIA-ASSURANCE-AND-CLOSURE/MEDIA_PROVIDER_MIGRATION_AND_RECOVERY.md`
   - `MEMORY/006-MEDIA-ASSURANCE-AND-CLOSURE/MEDIA_STORAGE_SCALE_AND_COST_MODEL.md`

2. Preserve genuine `MEMORY` domain content in:
   - `MEMORY/004-MEMORY-CAPTURE-AND-CURATION/`
   - `MEMORY/005-MEMORY-SEARCH-STORYTELLING-AND-LEGACY/`
   - `MEMORY/006-MEMORY-ASSURANCE-AND-CLOSURE/`

3. Preserve canonical `MEDIA` content in:
   - `MEDIA/004-MEDIA-PROCESSING-ALBUMS-AND-DISCOVERY/`
   - `MEDIA/005-MEDIA-INTELLIGENCE-AND-SHARING/`
   - `MEDIA/006-MEDIA-ASSURANCE-AND-CLOSURE/`

4. Archive `CALENDAR/003` closure content, preserving it as historical reference; do not delete it.
5. Archive `SEARCH/003` closure content, preserving it as historical reference; do not delete it.
6. Keep both `AI/002-FAMILY-INTELLIGENCE-AND-AI-DOMAIN/FAMILY_INTELLIGENCE_MODEL.md` and `FAMILY/005-FAMILY-INTELLIGENCE-AND-CONTINUITY/FAMILY_INTELLIGENCE_MODEL.md`.
7. Keep both architectural principles documents in `ARCHITECTURE/001` and `CONSTITUTION/004`.
8. Keep both architecture office orientation documents in `ARCHITECTURE/001` and `CONSTITUTION/072`.
9. Keep both domain evolution rule documents in `CONSTITUTION/003` and `CONSTITUTION/054`.
10. Keep both data architecture constitution documents in `CONSTITUTION/013` and `CONSTITUTION/056`.
11. Keep both data lifecycle and retention documents in `CONSTITUTION/013` and `ENGINEERING/005`.
12. Keep both portability contract principles documents in `CONSTITUTION/014` and `CONSTITUTION/048`.
13. Keep both localization principles documents in `CONSTITUTION/017` and `CONSTITUTION/067`.
14. Keep both performance engineering model documents in `ENGINEERING/007` and `ENGINEERING/014`.
15. Preserve all `ENGINEERING/002` through `ENGINEERING/009` folders and files intact.
16. Preserve all `PRIVACY/002` and `PRIVACY/003` folders and files intact.
17. Do not update `ARCHITECTURE/README.md` until the canonical architecture map is established.

## B. Exact source → target/archive paths

### Memory duplicate removals

These files are approved for removal as wrong-domain duplicates:
- `MEMORY/004-MEDIA-PROCESSING-ALBUMS-AND-DISCOVERY/MEDIA_ALBUM_AND_COLLECTION_MODEL.md`
- `MEMORY/004-MEDIA-PROCESSING-ALBUMS-AND-DISCOVERY/MEDIA_PROCESSING_AND_TRANSCODING_MODEL.md`
- `MEMORY/004-MEDIA-PROCESSING-ALBUMS-AND-DISCOVERY/MEDIA_SEARCH_AND_DISCOVERY_MODEL.md`
- `MEMORY/005-MEDIA-INTELLIGENCE-AND-SHARING/MEDIA_ACCESSIBLE_PRESENTATION_MODEL.md`
- `MEMORY/005-MEDIA-INTELLIGENCE-AND-SHARING/MEDIA_AI_ANALYSIS_AND_TRANSFORMATION_GOVERNANCE.md`
- `MEMORY/005-MEDIA-INTELLIGENCE-AND-SHARING/MEDIA_SHARING_AND_EXTERNAL_DELIVERY_MODEL.md`
- `MEMORY/006-MEDIA-ASSURANCE-AND-CLOSURE/MEDIA_CLOSURE_AND_CONTINUOUS_EVOLUTION.md`
- `MEMORY/006-MEDIA-ASSURANCE-AND-CLOSURE/MEDIA_NEGATIVE_TESTING_EXPANDED.md`
- `MEMORY/006-MEDIA-ASSURANCE-AND-CLOSURE/MEDIA_PROVIDER_MIGRATION_AND_RECOVERY.md`
- `MEMORY/006-MEDIA-ASSURANCE-AND-CLOSURE/MEDIA_STORAGE_SCALE_AND_COST_MODEL.md`

### Calendar archive targets

Proposed archive destination for historical calendar closure files:
- `CALENDAR/003-CALENDAR-ASSURANCE-AND-CLOSURE/CALENDAR_CLOSURE_AND_CONTINUOUS_EVOLUTION.md`
  → `docs/ARCHITECTURE_HISTORICAL_ARCHIVE/CALENDAR/003-CALENDAR-ASSURANCE-AND-CLOSURE/CALENDAR_CLOSURE_AND_CONTINUOUS_EVOLUTION.md`

### Search archive targets

Proposed archive destination for historical search closure files:
- `SEARCH/003-SEARCH-ASSURANCE-AND-CLOSURE/SEARCH_CLOSURE_AND_CONTINUOUS_EVOLUTION.md`
  → `docs/ARCHITECTURE_HISTORICAL_ARCHIVE/SEARCH/003-SEARCH-ASSURANCE-AND-CLOSURE/SEARCH_CLOSURE_AND_CONTINUOUS_EVOLUTION.md`

> Note: The archive destination above is a proposed path only. No archive folder should be created or changed until execution is authorized.

## C. Files and folders that must remain untouched

### Preserve unchanged
- All files under `ARCHITECTURE/` except the planned audit of `ARCHITECTURE/README.md` later.
- All files under `CONSTITUTION/`.
- All files under `ENGINEERING/002-ENGINEERING-DELIVERY-AND-QUALITY` through `ENGINEERING/009-MEDIA-AND-SEARCH-IMPLEMENTATION`.
- All files under `PRIVACY/002-FAMILY-DATA-GOVERNANCE`, `PRIVACY/002-FAMILY-PRIVACY-AND-CONSENT`, `PRIVACY/003-PRIVACY-ASSURANCE-AND-CLOSURE`, and `PRIVACY/003-PRIVACY-BY-DESIGN-AND-ASSURANCE`.
- All canonical `MEDIA/004`, `MEDIA/005`, and `MEDIA/006` files.
- All genuine `MEMORY/004-MEMORY-CAPTURE-AND-CURATION`, `MEMORY/005-MEMORY-SEARCH-STORYTELLING-AND-LEGACY`, and `MEMORY/006-MEMORY-ASSURANCE-AND-CLOSURE` files.
- `ARCHITECTURE/README.md` until the canonical architecture map is complete.
- All files referenced in `docs/ARCHITECTURE_RECONCILIATION_AUDIT.md` and `docs/ARCHITECTURE_HUMAN_DECISION_MATRIX.md` as kept.

### Must not be altered during this plan
- `AI/002-FAMILY-INTELLIGENCE-AND-AI-DOMAIN/FAMILY_INTELLIGENCE_MODEL.md`
- `FAMILY/005-FAMILY-INTELLIGENCE-AND-CONTINUITY/FAMILY_INTELLIGENCE_MODEL.md`
- `ARCHITECTURE/001-ARCHITECTURE-OFFICE-FOUNDATION/ARCHITECTURAL_PRINCIPLES.md`
- `CONSTITUTION/004-PRODUCT-ARCHITECTURE/ARCHITECTURAL_PRINCIPLES.md`
- `ARCHITECTURE/001-ARCHITECTURE-OFFICE-FOUNDATION/ARCHITECTURE_OFFICE_ORIENTATION.md`
- `CONSTITUTION/072-ARCHITECTURE-OFFICE-HANDOFF/ARCHITECTURE_OFFICE_ORIENTATION.md`
- `CONSTITUTION/003-DOMAIN-MODEL/DOMAIN_EVOLUTION_RULES.md`
- `CONSTITUTION/054-DOMAIN-MODEL-GOVERNANCE/DOMAIN_EVOLUTION_RULES.md`
- `CONSTITUTION/013-DATA-ARCHITECTURE/DATA_ARCHITECTURE_CONSTITUTION.md`
- `CONSTITUTION/056-DATA-ARCHITECTURE/DATA_ARCHITECTURE_CONSTITUTION.md`
- `CONSTITUTION/013-DATA-ARCHITECTURE/DATA_LIFECYCLE_AND_RETENTION.md`
- `ENGINEERING/005-DATA-IMPLEMENTATION-DESIGN/DATA_LIFECYCLE_AND_RETENTION.md`
- `CONSTITUTION/014-INTEROPERABILITY/PORTABILITY_CONTRACT_PRINCIPLES.md`
- `CONSTITUTION/048-FAMILY-PORTABILITY/PORTABILITY_CONTRACT_PRINCIPLES.md`
- `CONSTITUTION/017-GLOBAL-FAMILY/LOCALIZATION_PRINCIPLES.md`
- `CONSTITUTION/067-INTERNATIONALIZATION-LOCALIZATION/LOCALIZATION_PRINCIPLES.md`
- `ENGINEERING/007-OBSERVABILITY-PERFORMANCE-AND-RELIABILITY/PERFORMANCE_ENGINEERING_MODEL.md`
- `ENGINEERING/014-PLATFORM-SCALABILITY-AND-PERFORMANCE/PERFORMANCE_ENGINEERING_MODEL.md`

## D. Engineering numbering redesign proposal options

Presenting alternatives only; do not choose a design yet.

### Option 1: Parallel stream suffixes
- Keep existing numeric prefixes and add suffix letters to distinguish parallel streams.
- Example: `002A-ENGINEERING-DELIVERY-AND-QUALITY`, `002B-IMPLEMENTATION-GOVERNANCE`.
- Consequence: preserves existing sequence while clarifying both folders are separate streams; minimal relocation; still leaves numeric duplication visible in history.

### Option 2: Separate contiguous numbering ranges by engineering domain
- Reassign folder prefixes to dedicated ranges, e.g. `010-019` for delivery/governance, `020-029` for repository/quality, `030-039` for implementation/testing, etc.
- Consequence: removes duplicate prefixes and improves sequential clarity, but requires broader renumbering and consistent mapping documentation.

### Option 3: Topic-based folder identifiers with no shared numeric prefix
- Replace numeric prefix authority with topic-driven folder structure, e.g. `ENGINEERING/DELIVERY-AND-QUALITY/`, `ENGINEERING/IMPLEMENTATION-GOVERNANCE/`, `ENGINEERING/REPOSITORY-AND-DEVELOPMENT/`.
- Consequence: eliminates numbering ambiguity entirely, but is a larger structural change and may require updates to references and navigation.

### Option 4: Keep current numbering and add an explicit mapping table
- Retain existing folder names as-is and create a reconciliation table that declares each duplicate prefix as a separate engineering stream.
- Consequence: minimal file disruption and maximum backward compatibility; the duplicate numbering remains but is explicitly documented.

## E. Privacy numbering redesign proposal options

Do not choose a numbering solution yet. Presenting alternatives only.

### Option 1: Parallel stream suffixes
- Keep existing `002` and `003` prefixes and distinguish them as `002A/002B` and `003A/003B`.
- Example: `002A-FAMILY-DATA-GOVERNANCE`, `002B-FAMILY-PRIVACY-AND-CONSENT`.
- Consequence: preserves existing structure and makes parallel streams explicit.

### Option 2: Separate contiguous numbering ranges
- Reassign folder prefixes to separate ranges based on stream type, e.g. `002-004` for family data and consent, `005-007` for assurance/design.
- Consequence: resolves duplicate numbering but requires renumbering and reference updates.

### Option 3: Topic-based folder identifiers
- Move to descriptive topic names without relying on numeric prefix order.
- Example: `PRIVACY/FAMILY-DATA-GOVERNANCE/`, `PRIVACY/FAMILY-PRIVACY-AND-CONSENT/`, `PRIVACY/PRIVACY-ASSURANCE-AND-CLOSURE/`, `PRIVACY/PRIVACY-BY-DESIGN-AND-ASSURANCE/`.
- Consequence: eliminates prefix collision; may require a repository-wide navigation update.

### Option 4: Preserve current numbering with a reconciliation mapping
- Keep current folders unchanged and publish a table linking duplicate prefixes to separate conceptual streams.
- Consequence: safest short-term approach; preserves all content while deferring structural redesign.

## F. Authority hierarchy

The following hierarchy is the approved authority model for this reconciliation:

1. **Constitutional documents** (`CONSTITUTION/`)
   - Highest authority for product meaning, family domain, trust, privacy, data, and portability principles.
   - Examples: `CONSTITUTION/004-PRODUCT-ARCHITECTURE/ARCHITECTURAL_PRINCIPLES.md`, `CONSTITUTION/013-DATA-ARCHITECTURE/`, `CONSTITUTION/014-INTEROPERABILITY/`, `CONSTITUTION/017-GLOBAL-FAMILY/`.

2. **Architectural documents** (`ARCHITECTURE/` and architecture handoff documents under `CONSTITUTION/072`)
   - Translate constitutional authority into system structure, architectural boundaries, and architecture office ownership.
   - Examples: `ARCHITECTURE/001-ARCHITECTURE-OFFICE-FOUNDATION/`, `CONSTITUTION/072-ARCHITECTURE-OFFICE-HANDOFF/`.

3. **Engineering documents** (`ENGINEERING/`)
   - Provide implementation design, delivery, quality, data implementation, operations, and assurance guidance.
   - Must preserve and respect constitutional and architectural authority.
   - Examples: `ENGINEERING/005-DATA-IMPLEMENTATION-DESIGN/`, `ENGINEERING/007-OBSERVABILITY-PERFORMANCE-AND-RELIABILITY/`.

4. **Domain-specific canonical documents** (`MEDIA/`, `MEMORY/`, `CALENDAR/`, `SEARCH/`, `PRIVACY/`, `AI/`, `FAMILY/`, etc.)
   - Represent domain content that must align with the higher authority levels.

## G. Validation checks after execution

1. Confirm the only removed files are the 10 exact wrong-domain duplicate `MEMORY/00X-MEDIA-*` files listed above.
2. Confirm `MEMORY/004-MEMORY-CAPTURE-AND-CURATION/`, `MEMORY/005-MEMORY-SEARCH-STORYTELLING-AND-LEGACY/`, and `MEMORY/006-MEMORY-ASSURANCE-AND-CLOSURE/` remain intact.
3. Confirm all canonical `MEDIA/004`, `MEDIA/005`, and `MEDIA/006` files remain intact.
4. Confirm `CALENDAR/006-CALENDAR-ASSURANCE-AND-CLOSURE/CALENDAR_CLOSURE_AND_CONTINUOUS_EVOLUTION.md` remains in place.
5. Confirm `SEARCH/006-SEARCH-ASSURANCE-AND-CLOSURE/SEARCH_CLOSURE_AND_CONTINUOUS_EVOLUTION.md` remains in place.
6. Confirm `CALENDAR/003/...` and `SEARCH/003/...` historical closure files have been moved to the agreed archive path without content changes.
7. Confirm all approved retained variant documents remain unchanged.
8. Confirm `ARCHITECTURE/README.md` is still untouched.
9. Perform a `git status` check to ensure only intended file removals and archive moves appear.
10. Perform a targeted diff or content hash check on the relevant files to ensure no unintended edits.

## H. Git rollback strategy

1. Perform all work in a dedicated feature branch, e.g. `reconcile/femc-execution-plan`.
2. Stage and review only the intended changes before committing.
3. If a local change must be undone before commit, use:
   - `git restore -- <file>` for unwanted file edits or moves
   - `git restore --staged -- <file>` for unwanted staged changes
4. If the plan is committed and later needs rollback, use:
   - `git revert <commit>` to undo the specific reconciliation commit
   - or `git reset --hard <commit>` if the entire feature branch must be discarded (only after confirming no needed work exists)
5. Keep a clean working tree before starting by using `git status` and `git diff`.
6. If archive moves are used, preserve the original paths in the branch history until the final reconciliation is verified.

## I. Ordered execution sequence

1. Open a dedicated branch for reconciliation work.
2. Create and review the archival destination plan in writing; do not create archive directories yet.
3. Prepare an exact removal list for the 10 wrong-domain duplicate `MEMORY/00X-MEDIA-*` files.
4. Validate that the files to be removed are exact duplicates of `MEDIA/004-006` content.
5. Remove the approved `MEMORY/00X-MEDIA-*` files.
6. Move `CALENDAR/003` closure files to the agreed archive target.
7. Move `SEARCH/003` closure files to the agreed archive target.
8. Run the validation checklist in section G.
9. Document the reconciliation result and review with BM before any renumbering or redesign work.
10. Prepare separate proposals for engineering and privacy numbering redesign based on the options in sections D and E.

---

> This plan is execution guidance only. No structural changes should be made until the plan is formally authorized and the work is performed in a controlled branch.
