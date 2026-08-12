# FEMC Open Capability Gate & Integration Contract

## Executive Overview
The **FEMC Open Capability Gate** establishes lightweight architectural contracts and principles ensuring that new product capabilities (e.g. Mayil AI, Vel Guardian, Future Seed Clusters) can seamlessly integrate with the FEMC system without requiring rewrites or introducing tight coupling to existing capabilities.

This contract relies on lightweight, reusable conventions enforced across canonical models, domain services, authorization boundaries, provenance metadata, derived projections, and application API surfaces.

---

## 1. Object Classification Schema
Every persistent or transient object within FEMC MUST be classified into one of four architectural tiers:

1. **Canonical**: Authoritative, primary state stored in `CanonicalRepository` (e.g. `Person`, `Account`, `FamilyContext`, `Event`, `Memory`, `Place`, `MediaItem`, `MediaAlbum`, `Notification`, `ShareLink`).
2. **Derived**: Rebuildable projections, indexes, or aggregated views stored in `DerivedRepository` (e.g. `CalendarProjectionEntry`, `TimelineProjectionEntry`, `SearchEntry`).
3. **Intelligence/Proposal**: Non-authoritative AI/recommendation proposals (e.g. Mayil AI suggestions). Must require explicit human approval before mutating canonical state.
4. **Governance/Audit**: Invariant validation results, security audits, and repair proposals (e.g. Vel Guardian audit reports). Must remain read-only/observational unless explicit repair workflows are invoked.

---

## 2. Open Capability Principles

All present and future capabilities MUST adhere to the following 11 core principles:

1. **Canonical Authoritativeness**: Canonical state remains the single source of truth; projections must never become canonical stores.
2. **Domain Service Encapsulation**: Domain services strictly own business rules and mutations for their respective capability.
3. **Unified Application Façade**: `FEMCApi` serves as the sole entry point for client/session interactions.
4. **Mandatory Authorization**: Every user/context operation must be authorized through `AuthorizationService`.
5. **Mandatory Provenance**: Every canonical record creation or mutation must carry `ProvenanceMetadata`.
6. **Rebuildable Derived Projections**: All derived projections must be deterministically rebuildable from canonical state.
7. **Decoupled Capabilities**: Capabilities must interact via clean API/service boundaries without direct cross-service private state access.
8. **Proposal-Only AI (Mayil AI)**: AI intelligence must remain strictly proposal/recommendation-based until explicitly approved by human action.
9. **Non-Mutating Guardian (Vel Guardian)**: Security and integrity validation must remain cross-cutting and observational, without silent canonical mutations.
10. **Inspectable & Exportable**: Capability state must expose data portability definitions allowing authorized export.
11. **Regression Integrity**: Integration of new capabilities must maintain 100% test suite pass rate across all existing capabilities.

---

## 3. Capability Integration Contract

When adding a new capability to FEMC, the integration MUST satisfy the standard vertical slice contract:

```
Capability 
  → Canonical Model (if required)
  → Repository (if required)
  → Domain Service
  → Authorization
  → Provenance
  → Derived Projection (if required)
  → FEMCApi
  → Deterministic Tests
```

### Contract Specification Matrix

| Aspect | Integration Requirement |
|---|---|
| **Capability Ownership** | Single domain service owns business operations (e.g. `DataPortabilityService`, `MediaService`). |
| **Inputs / Consumers** | Consumes authenticated session ID, target context ID, or canonical entity parameters. |
| **Outputs / API Surface** | Exposes clean methods on `FEMCApi` delegating to the domain service; returns structured DTOs. |
| **Authorization Boundary** | Enforces session authentication and context membership via `AuthorizationService`. |
| **Canonical vs Derived** | Canonical models added to `CanonicalRepository` if stateful; projections added to `DerivedRepository` if view-only. |
| **Provenance** | Attaches `ProvenanceMetadata` with appropriate `ProvenanceSourceType` and audit trace. |
| **Test Responsibility** | Minimum 5 deterministic unit tests covering creation, retrieval, privacy, authorization, and edge cases. |
| **Guardian Validation** | Exposes inspectable invariants for Vel Guardian to check without state mutation. |
| **Data Portability** | Registers canonical entities into `DataPortabilityService` export dictionary. |

---

## 4. Seed Cluster 5 (Data Portability) Audit Against Open Capability Gate

The `DataPortabilityService` was audited against the 9 validation criteria of the Open Capability Gate:

1. **Read-Only Export**: `export_family_context_for_account` gathers records without calling any mutation methods on `CanonicalRepository` or `DerivedRepository`. (**PASS**)
2. **Authorization Respect**: Verifies session validity and context membership (`account_id in context.member_ids`). Throws `PermissionError` for unauthorized access. (**PASS**)
3. **Private Data Protection**: Evaluates `can_view_event`, `can_view_memory`, `can_view_place`, `can_view_media_item`, `can_view_media_album` so private records of other members are excluded from the export. (**PASS**)
4. **Stable ID References**: Entity IDs (`id`, `event_id`, `place_id`, `owner_id`, `person_id`) are preserved intact across records. (**PASS**)
5. **Representable Relationships**: `relationships` items preserve `source_person_id`, `target_person_id`, and `relationship_type`. (**PASS**)
6. **Preserved Provenance**: Attaches system `ProvenanceMetadata` with `source_id="femc-data-portability"`. (**PASS**)
7. **Exclusion of Secrets**: Account password hashes, session tokens, and credentials are explicitly omitted from export dictionaries. (**PASS**)
8. **Non-Mutating Validation**: `validate_data_export` performs purely structural and schema validation on JSON payloads without altering system state. (**PASS**)
9. **Extensibility for Future Capabilities**: New canonical capability records (e.g. future seed clusters) can be added simply by registering a new record category key in `DataPortabilityService.export_family_context_for_account` without altering the portability framework architecture. (**PASS**)

---

## Summary
The **FEMC Open Capability Gate** is officially established and validated against Seed Cluster 5.
