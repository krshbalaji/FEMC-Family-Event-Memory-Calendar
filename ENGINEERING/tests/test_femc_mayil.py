import datetime
import pytest
from ENGINEERING.source.femc.api import FEMCApi
from ENGINEERING.source.femc.models import ProposalStatus, ProposalType, ProvenanceSourceType, VisibilityLevel


def test_mayil_read_only_isolation():
    api = FEMCApi()

    person = api.identity.create_person("Alice Member")
    account = api.identity.create_account("alice", "alice@example.com", person.id)
    session = api.create_session(account.id)

    context = api.identity.create_family_context("Mayil Family", member_ids=[account.id], created_by_id=account.id)

    # Initial canonical event count
    events_before = len(api.canonical.list_events())

    # Generate insights and proposals
    insight = api.analyze_family_insights_for_session(session.session_id, context.id)
    proposal = api.propose_event_recommendation_for_session(
        session.session_id, context.id, "Annual Picnic", "Recommend scheduling annual picnic"
    )

    events_after = len(api.canonical.list_events())

    # Canonical domain state MUST remain unmutated prior to human approval
    assert events_before == events_after == 0
    assert insight.id is not None
    assert proposal.status == ProposalStatus.PROPOSED


def test_mayil_proposal_approval_flow():
    api = FEMCApi()

    person = api.identity.create_person("Bob Member")
    account = api.identity.create_account("bob", "bob@example.com", person.id)
    session = api.create_session(account.id)

    context = api.identity.create_family_context("Approval Family", member_ids=[account.id], created_by_id=account.id)

    # Propose event recommendation
    proposal = api.propose_event_recommendation_for_session(
        session.session_id, context.id, "Family Reunion", "Suggested reunion event"
    )
    assert proposal.status == ProposalStatus.PROPOSED
    assert len(api.canonical.list_events()) == 0

    # Authorized human approves proposal
    approved = api.approve_action_proposal_for_session(session.session_id, proposal.id)

    # Status must transition to EXECUTED
    assert approved.status == ProposalStatus.EXECUTED
    assert any("approved-from-mayil-proposal" in entry for entry in approved.provenance.audit_trail)

    # Event MUST now exist in canonical repository created via EventService
    canonical_events = api.canonical.list_events()
    assert len(canonical_events) == 1
    assert canonical_events[0].title == "Family Reunion"
    assert canonical_events[0].owner_id == account.id


def test_mayil_proposal_rejection():
    api = FEMCApi()

    person = api.identity.create_person("Charlie Member")
    account = api.identity.create_account("charlie", "charlie@example.com", person.id)
    session = api.create_session(account.id)

    context = api.identity.create_family_context("Rejection Family", member_ids=[account.id], created_by_id=account.id)

    proposal = api.propose_event_recommendation_for_session(
        session.session_id, context.id, "Unwanted Trip", "Suggested trip"
    )

    # Reject proposal
    rejected = api.reject_action_proposal_for_session(session.session_id, proposal.id)

    assert rejected.status == ProposalStatus.REJECTED
    assert len(api.canonical.list_events()) == 0
    assert any("rejected-from-mayil-proposal" in entry for entry in rejected.provenance.audit_trail)


def test_mayil_privacy_filtration():
    api = FEMCApi()

    alice_person = api.identity.create_person("Alice")
    alice_account = api.identity.create_account("alice_priv", "alice_priv@example.com", alice_person.id)
    alice_session = api.create_session(alice_account.id)

    bob_person = api.identity.create_person("Bob")
    bob_account = api.identity.create_account("bob_priv", "bob_priv@example.com", bob_person.id)
    bob_session = api.create_session(bob_account.id)

    context = api.identity.create_family_context(
        "Privacy Family", member_ids=[alice_account.id, bob_account.id], created_by_id=alice_account.id
    )

    # Bob creates a PRIVATE event
    api.create_event_for_session(
        bob_session.session_id,
        "Bob Secret Event",
        "Top secret",
        context.id,
        datetime.datetime(2026, 11, 1, 10, 0),
        None,
        visibility=VisibilityLevel.PRIVATE,
    )

    # Alice creates a FAMILY event
    api.create_event_for_session(
        alice_session.session_id,
        "Alice Family Event",
        "Public to family",
        context.id,
        datetime.datetime(2026, 11, 2, 10, 0),
        None,
        visibility=VisibilityLevel.FAMILY,
    )

    # Alice requests Mayil analysis -> MUST analyze 1 event for Alice (excluding Bob's private event)
    alice_analysis = api.analyze_family_insights_for_session(alice_session.session_id, context.id)
    assert "Analyzed 1 events" in alice_analysis.analysis_summary

    # Bob requests Mayil analysis -> MUST analyze 2 events for Bob (includes Bob's private event + Alice's family event)
    bob_analysis = api.analyze_family_insights_for_session(bob_session.session_id, context.id)
    assert "Analyzed 2 events" in bob_analysis.analysis_summary


def test_mayil_unauthorized_proposal_access():
    api = FEMCApi()

    owner_person = api.identity.create_person("Owner")
    owner_account = api.identity.create_account("owner_p", "owner_p@example.com", owner_person.id)
    owner_session = api.create_session(owner_account.id)

    outsider_person = api.identity.create_person("Outsider")
    outsider_account = api.identity.create_account("outsider_p", "outsider_p@example.com", outsider_person.id)
    outsider_session = api.create_session(outsider_account.id)

    context = api.identity.create_family_context("Owner Family", member_ids=[owner_account.id], created_by_id=owner_account.id)

    proposal = api.propose_event_recommendation_for_session(
        owner_session.session_id, context.id, "Owner Event", "Description"
    )

    # Outsider cannot approve owner's proposal
    with pytest.raises(PermissionError):
        api.approve_action_proposal_for_session(outsider_session.session_id, proposal.id)

    # Outsider cannot reject owner's proposal
    with pytest.raises(PermissionError):
        api.reject_action_proposal_for_session(outsider_session.session_id, proposal.id)


def test_mayil_provenance():
    api = FEMCApi()

    person = api.identity.create_person("Prov Member")
    account = api.identity.create_account("prov", "prov@example.com", person.id)
    session = api.create_session(account.id)

    context = api.identity.create_family_context("Prov Family", member_ids=[account.id], created_by_id=account.id)

    proposal = api.propose_event_recommendation_for_session(
        session.session_id, context.id, "Prov Event", "Description"
    )

    assert proposal.provenance is not None
    assert proposal.provenance.source_type == ProvenanceSourceType.SYSTEM
    assert proposal.provenance.source_id == "mayil-ai-engine"
    assert "proposal-created" in proposal.provenance.audit_trail


def test_mayil_proposal_status_lifecycle():
    api = FEMCApi()

    person = api.identity.create_person("Lifecycle Member")
    account = api.identity.create_account("life", "life@example.com", person.id)
    session = api.create_session(account.id)

    context = api.identity.create_family_context("Lifecycle Family", member_ids=[account.id], created_by_id=account.id)

    # 1. Proposal 1: PROPOSED -> EXECUTED
    prop1 = api.propose_event_recommendation_for_session(
        session.session_id, context.id, "Life Event 1", "Desc 1"
    )
    assert prop1.status == ProposalStatus.PROPOSED

    app1 = api.approve_action_proposal_for_session(session.session_id, prop1.id)
    assert app1.status == ProposalStatus.EXECUTED

    # Attempting to re-approve executed proposal fails
    with pytest.raises(ValueError):
        api.approve_action_proposal_for_session(session.session_id, prop1.id)

    # 2. Proposal 2: PROPOSED -> REJECTED
    prop2 = api.propose_event_recommendation_for_session(
        session.session_id, context.id, "Life Event 2", "Desc 2"
    )
    assert prop2.status == ProposalStatus.PROPOSED

    rej2 = api.reject_action_proposal_for_session(session.session_id, prop2.id)
    assert rej2.status == ProposalStatus.REJECTED

    # Attempting to approve rejected proposal fails
    with pytest.raises(ValueError):
        api.approve_action_proposal_for_session(session.session_id, prop2.id)


def test_mayil_export_portability_compatibility():
    api = FEMCApi()

    person = api.identity.create_person("Export Member")
    account = api.identity.create_account("exp_m", "exp_m@example.com", person.id)
    session = api.create_session(account.id)

    context = api.identity.create_family_context("Mayil Export Family", member_ids=[account.id], created_by_id=account.id)

    api.analyze_family_insights_for_session(session.session_id, context.id)
    api.propose_event_recommendation_for_session(session.session_id, context.id, "Export Event", "Desc")

    export = api.export_family_context_for_session(session.session_id, context.id)

    assert "action_proposals" in export.records
    assert "insight_analyses" in export.records
    assert len(export.records["action_proposals"]) == 1
    assert len(export.records["insight_analyses"]) == 1

    # Secret exclusion check
    for acc in export.records["accounts"]:
        assert "password_hash" not in acc

    # Validation check
    export_payload = {
        "export_id": export.export_id,
        "family_context_id": export.family_context_id,
        "exported_at": export.exported_at.isoformat(),
        "schema_version": export.schema_version,
        "provenance": {
            "source_type": export.provenance.source_type.value,
            "source_id": export.provenance.source_id,
            "created_by_id": export.provenance.created_by_id,
            "audit_trail": export.provenance.audit_trail,
        },
        "records": export.records,
    }
    val_res = api.validate_data_export(export_payload)
    assert val_res.is_valid is True
    assert val_res.record_counts["action_proposals"] == 1


def test_mayil_approval_atomicity():
    api = FEMCApi()

    person = api.identity.create_person("Atom Member")
    account = api.identity.create_account("atom_m", "atom_m@example.com", person.id)
    session = api.create_session(account.id)

    context = api.identity.create_family_context("Atom Family", member_ids=[account.id], created_by_id=account.id)

    proposal = api.propose_event_recommendation_for_session(session.session_id, context.id, "Fail Event", "Desc")

    # Corrupt proposal changes to force domain execution failure
    proposal.proposed_changes["start_time"] = "invalid-date-format"

    with pytest.raises(Exception):
        api.approve_action_proposal_for_session(session.session_id, proposal.id)

    # Proposal MUST NOT remain in APPROVED or EXECUTED state if creation fails
    assert proposal.status == ProposalStatus.PROPOSED

