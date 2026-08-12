import datetime
import pytest
from ENGINEERING.source.femc.api import FEMCApi
from ENGINEERING.source.femc.models import (
    AnomalySeverity,
    AnomalyType,
    ProvenanceMetadata,
    ProvenanceSourceType,
    RepairClassification,
    ShareLink,
    ShareResourceType,
    VisibilityLevel,
)


def test_dangling_reference_detection():
    api = FEMCApi()

    person = api.identity.create_person("Guardian Member")
    account = api.identity.create_account("guard_1", "guard_1@example.com", person.id)
    session = api.create_session(account.id)

    context = api.identity.create_family_context("Dangling Family", member_ids=[account.id], created_by_id=account.id)

    event = api.create_event_for_session(
        session.session_id, "Dangling Event", "Desc", context.id, datetime.datetime(2026, 12, 1, 10, 0), None
    )

    # Manually inject dangling place_id
    event.place_id = "non-existent-place-id"

    report = api.run_integrity_audit_for_session(session.session_id, context.id)
    assert report.is_valid is False
    assert any(a.anomaly_type == AnomalyType.DANGLING_REFERENCE for a in report.anomalies)


def test_calendar_projection_desync_detection():
    api = FEMCApi()

    person = api.identity.create_person("Cal Member")
    account = api.identity.create_account("cal_m", "cal_m@example.com", person.id)
    session = api.create_session(account.id)

    context = api.identity.create_family_context("Cal Desync Family", member_ids=[account.id], created_by_id=account.id)

    event = api.create_event_for_session(
        session.session_id, "Desync Event", "Desc", context.id, datetime.datetime(2026, 12, 2, 10, 0), None
    )

    # Clear derived calendar entries to simulate desync
    api.derived.calendar_entries.clear()

    report = api.run_integrity_audit_for_session(session.session_id, context.id)
    assert report.is_valid is False
    desync_anomalies = [a for a in report.anomalies if a.anomaly_type == AnomalyType.PROJECTION_DESYNC]
    assert len(desync_anomalies) > 0
    assert any(a.affected_entity_id == event.id for a in desync_anomalies)


def test_timeline_projection_desync_detection():
    api = FEMCApi()

    person = api.identity.create_person("Timeline Member")
    account = api.identity.create_account("tl_m", "tl_m@example.com", person.id)
    session = api.create_session(account.id)

    context = api.identity.create_family_context("TL Desync Family", member_ids=[account.id], created_by_id=account.id)

    event = api.create_event_for_session(
        session.session_id, "TL Event", "Desc", context.id, datetime.datetime(2026, 12, 3, 10, 0), None
    )

    # Clear derived timeline entries
    api.derived.clear_timeline_entries()

    report = api.run_integrity_audit_for_session(session.session_id, context.id)
    assert report.is_valid is False
    tl_anomalies = [a for a in report.anomalies if a.affected_entity_id == event.id]
    assert len(tl_anomalies) > 0


def test_missing_provenance_detection():
    api = FEMCApi()

    person = api.identity.create_person("Prov Member")
    account = api.identity.create_account("prov_m", "prov_m@example.com", person.id)
    session = api.create_session(account.id)

    context = api.identity.create_family_context("Prov Family", member_ids=[account.id], created_by_id=account.id)

    event = api.create_event_for_session(
        session.session_id, "No Prov Event", "Desc", context.id, datetime.datetime(2026, 12, 4, 10, 0), None
    )

    # Remove provenance metadata
    object.__setattr__(event, "provenance", None)

    report = api.run_integrity_audit_for_session(session.session_id, context.id)
    assert report.is_valid is False
    prov_anomalies = [a for a in report.anomalies if a.anomaly_type == AnomalyType.PROVENANCE_MISSING]
    assert len(prov_anomalies) == 1
    assert prov_anomalies[0].severity == AnomalySeverity.CRITICAL


def test_privacy_invariant_detection():
    api = FEMCApi()

    person = api.identity.create_person("Privacy Member")
    account = api.identity.create_account("priv_m", "priv_m@example.com", person.id)
    session = api.create_session(account.id)

    context = api.identity.create_family_context("Privacy Family", member_ids=[account.id], created_by_id=account.id)

    event = api.create_event_for_session(
        session.session_id, "Private Secret", "Desc", context.id, datetime.datetime(2026, 12, 5, 10, 0), None, visibility=VisibilityLevel.PRIVATE
    )

    # Create share link manually targeting private event
    prov = ProvenanceMetadata(source_type=ProvenanceSourceType.USER, source_id="test", created_by_id=account.id)
    link = ShareLink(token="priv-tok-123", resource_type=ShareResourceType.EVENT, resource_id=event.id, family_context_id=context.id, created_by_id=account.id, provenance=prov)
    api.canonical.add_share_link(link)

    report = api.run_integrity_audit_for_session(session.session_id, context.id)
    assert report.is_valid is False
    priv_anomalies = [a for a in report.anomalies if a.anomaly_type == AnomalyType.PRIVACY_INVARIANT_VIOLATION]
    assert len(priv_anomalies) == 1


def test_topology_inconsistency_detection():
    api = FEMCApi()

    person = api.identity.create_person("Self Rel Person")
    account = api.identity.create_account("top_m", "top_m@example.com", person.id)
    session = api.create_session(account.id)

    context = api.identity.create_family_context("Topology Family", member_ids=[account.id], created_by_id=account.id)

    # Self-relationship
    api.identity.create_relationship(person.id, person.id, "parent", context.id)

    report = api.run_integrity_audit_for_session(session.session_id, context.id)
    assert report.is_valid is False
    top_anomalies = [a for a in report.anomalies if a.anomaly_type == AnomalyType.TOPOLOGY_INCONSISTENCY]
    assert len(top_anomalies) == 1


def test_repair_proposal_classification():
    api = FEMCApi()

    person = api.identity.create_person("Classify Member")
    account = api.identity.create_account("clf_m", "clf_m@example.com", person.id)
    session = api.create_session(account.id)

    context = api.identity.create_family_context("Classify Family", member_ids=[account.id], created_by_id=account.id)

    event = api.create_event_for_session(
        session.session_id, "Desync Event", "Desc", context.id, datetime.datetime(2026, 12, 6, 10, 0), None
    )
    event.place_id = "dangling-place"
    api.derived.calendar_entries.clear()

    api.run_integrity_audit_for_session(session.session_id, context.id)
    proposals = api.get_repair_proposals_for_session(session.session_id, context.id)

    derived_prop = next(p for p in proposals if p.proposed_repair_action == "rebuild_derived_projections")
    canon_prop = next(p for p in proposals if p.proposed_repair_action == "dangling_place_id")

    assert derived_prop.classification == RepairClassification.DERIVED_ONLY
    assert derived_prop.requires_human_approval is False

    assert canon_prop.classification == RepairClassification.CANONICAL_REPAIR
    assert canon_prop.requires_human_approval is True


def test_canonical_repair_execution_deferred():
    api = FEMCApi()

    person = api.identity.create_person("Deferred Member")
    account = api.identity.create_account("def_m", "def_m@example.com", person.id)
    session = api.create_session(account.id)

    context = api.identity.create_family_context("Deferred Family", member_ids=[account.id], created_by_id=account.id)

    event = api.create_event_for_session(
        session.session_id, "Deferred Event", "Desc", context.id, datetime.datetime(2026, 12, 8, 10, 0), None
    )
    event.place_id = "dangling-id"

    api.run_integrity_audit_for_session(session.session_id, context.id)
    proposals = api.get_repair_proposals_for_session(session.session_id, context.id)

    canon_prop = next(p for p in proposals if p.classification == RepairClassification.CANONICAL_REPAIR)

    with pytest.raises(NotImplementedError):
        api.execute_repair_proposal_for_session(session.session_id, canon_prop.id)

    assert canon_prop.is_executed is False


def test_safe_derived_projection_repair():
    api = FEMCApi()

    person = api.identity.create_person("Repair Member")
    account = api.identity.create_account("rep_m", "rep_m@example.com", person.id)
    session = api.create_session(account.id)

    context = api.identity.create_family_context("Repair Family", member_ids=[account.id], created_by_id=account.id)

    api.create_event_for_session(
        session.session_id, "Repair Event", "Desc", context.id, datetime.datetime(2026, 12, 7, 10, 0), None
    )

    # Clear derived entries
    api.derived.calendar_entries.clear()
    api.derived.clear_timeline_entries()

    # Audit & get repair proposals
    api.run_integrity_audit_for_session(session.session_id, context.id)
    proposals = api.get_repair_proposals_for_session(session.session_id, context.id)

    derived_prop = next(p for p in proposals if p.proposed_repair_action == "rebuild_derived_projections")
    assert derived_prop.is_executed is False

    # Execute derived projection repair
    executed_prop = api.execute_repair_proposal_for_session(session.session_id, derived_prop.id)

    assert executed_prop.is_executed is True
    assert len(api.derived.get_calendar_entries(context.id)) == 1
    assert len(api.derived.get_timeline_entries(context.id)) == 1


def test_repair_replay_protection():
    api = FEMCApi()

    person = api.identity.create_person("Replay Member")
    account = api.identity.create_account("rep_p", "rep_p@example.com", person.id)
    session = api.create_session(account.id)

    context = api.identity.create_family_context("Replay Family", member_ids=[account.id], created_by_id=account.id)

    api.create_event_for_session(
        session.session_id, "Replay Event", "Desc", context.id, datetime.datetime(2026, 12, 9, 10, 0), None
    )
    api.derived.calendar_entries.clear()

    api.run_integrity_audit_for_session(session.session_id, context.id)
    proposals = api.get_repair_proposals_for_session(session.session_id, context.id)

    derived_prop = proposals[0]
    api.execute_repair_proposal_for_session(session.session_id, derived_prop.id)

    # Attempting second execution must fail with ValueError
    with pytest.raises(ValueError):
        api.execute_repair_proposal_for_session(session.session_id, derived_prop.id)


def test_guardian_cannot_execute_mayil_proposals():
    api = FEMCApi()

    person = api.identity.create_person("Mayil Isolation Member")
    account = api.identity.create_account("m_iso", "m_iso@example.com", person.id)
    session = api.create_session(account.id)

    context = api.identity.create_family_context("Mayil Iso Family", member_ids=[account.id], created_by_id=account.id)

    # Mayil generates an ActionProposal
    mayil_prop = api.mayil.propose_event_recommendation(account.id, context.id, "Mayil Rec", "Desc")
    assert mayil_prop is not None

    # Guardian execute must reject Mayil proposal ID
    with pytest.raises(ValueError):
        api.execute_repair_proposal_for_session(session.session_id, mayil_prop.id)


def test_unauthorized_audit_repair_access():
    api = FEMCApi()

    owner_person = api.identity.create_person("Owner")
    owner_account = api.identity.create_account("owner_g", "owner_g@example.com", owner_person.id)
    owner_session = api.create_session(owner_account.id)

    outsider_person = api.identity.create_person("Outsider")
    outsider_account = api.identity.create_account("outsider_g", "outsider_g@example.com", outsider_person.id)
    outsider_session = api.create_session(outsider_account.id)

    context = api.identity.create_family_context("Owner Family", member_ids=[owner_account.id], created_by_id=owner_account.id)

    with pytest.raises(PermissionError):
        api.run_integrity_audit_for_session(outsider_session.session_id, context.id)

    with pytest.raises(PermissionError):
        api.get_repair_proposals_for_session(outsider_session.session_id, context.id)


def test_guardian_provenance():
    api = FEMCApi()

    person = api.identity.create_person("Guardian Prov")
    account = api.identity.create_account("g_prov", "g_prov@example.com", person.id)
    session = api.create_session(account.id)

    context = api.identity.create_family_context("Guardian Prov Family", member_ids=[account.id], created_by_id=account.id)

    api.create_event_for_session(
        session.session_id, "Prov Event", "Desc", context.id, datetime.datetime(2026, 12, 9, 10, 0), None
    )
    api.derived.calendar_entries.clear()

    api.run_integrity_audit_for_session(session.session_id, context.id)
    proposals = api.get_repair_proposals_for_session(session.session_id, context.id)

    prov = proposals[0].provenance
    assert prov is not None
    assert prov.source_type == ProvenanceSourceType.SYSTEM
    assert prov.source_id == "vel-guardian-engine"
    assert "vel-integrity-audit" in prov.audit_trail
    assert "repair-proposed" in prov.audit_trail


def test_guardian_data_portability_compatibility():
    api = FEMCApi()

    person = api.identity.create_person("Portability Member")
    account = api.identity.create_account("port_m", "port_m@example.com", person.id)
    session = api.create_session(account.id)

    context = api.identity.create_family_context("Portability Family", member_ids=[account.id], created_by_id=account.id)

    api.create_event_for_session(
        session.session_id, "Desync Event", "Desc", context.id, datetime.datetime(2026, 12, 10, 10, 0), None
    )
    api.derived.calendar_entries.clear()

    api.run_integrity_audit_for_session(session.session_id, context.id)

    export_result = api.export_family_context_for_session(session.session_id, context.id)
    assert "repair_proposals" in export_result.records
    assert len(export_result.records["repair_proposals"]) > 0
    assert export_result.records["repair_proposals"][0]["classification"] == "DERIVED_ONLY"

