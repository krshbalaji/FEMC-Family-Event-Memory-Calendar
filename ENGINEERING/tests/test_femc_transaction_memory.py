import datetime
import pytest
from ENGINEERING.source.femc.models import (
    ActionType,
    ResourceType,
    TransactionRecord,
    VisibilityLevel,
    EventCategory,
    MediaType,
    ShareResourceType,
)
from ENGINEERING.source.femc.api import FEMCApi
from run import DemoState


def test_transaction_recording_create_event():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    rec = api.record_transaction_for_session(
        session_id=sess_id,
        family_context_id=fc_id,
        action_type=ActionType.CREATE,
        resource_type=ResourceType.EVENT,
        resource_id=state.event1.id,
        resource_label_snapshot="Alice Birthday Party",
        operation="Scheduled event for Aug 20",
        visibility=VisibilityLevel.FAMILY,
    )
    assert rec.transaction_id is not None
    assert rec.action_type == ActionType.CREATE
    assert rec.resource_type == ResourceType.EVENT


def test_update_transaction_records_changed_fields():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    rec = api.record_transaction_for_session(
        session_id=sess_id,
        family_context_id=fc_id,
        action_type=ActionType.UPDATE,
        resource_type=ResourceType.EVENT,
        resource_id=state.event1.id,
        resource_label_snapshot="Alice Birthday Party",
        operation="Updated event date and visibility",
        changed_fields={"date": {"before": "2026-08-20", "after": "2026-08-21"}, "visibility": {"before": "family", "after": "private"}},
        visibility=VisibilityLevel.PRIVATE,
    )
    assert rec.changed_fields["date"]["after"] == "2026-08-21"


def test_delete_transaction_survives_entity_deletion():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    # Create memory & record creation
    mem = api.create_memory_for_session(
        session_id=sess_id,
        event_id=state.event1.id,
        narrative="This story will be deleted.",
    )
    api.record_transaction_for_session(
        session_id=sess_id,
        family_context_id=fc_id,
        action_type=ActionType.CREATE,
        resource_type=ResourceType.MEMORY,
        resource_id=mem.id,
        resource_label_snapshot=mem.narrative,
        operation="Created memory story",
    )

    # Record deletion
    api.record_transaction_for_session(
        session_id=sess_id,
        family_context_id=fc_id,
        action_type=ActionType.DELETE,
        resource_type=ResourceType.MEMORY,
        resource_id=mem.id,
        resource_label_snapshot=mem.narrative,
        operation="Deleted memory story by user request",
    )

    # Query history: deletion transaction survives even if canonical data is cleared/deleted
    history = api.get_resource_history_for_session(sess_id, fc_id, ResourceType.MEMORY, mem.id)
    assert len(history) == 2
    assert history[0].action_type == ActionType.DELETE


def test_attach_media_transaction_recorded():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    rec = api.record_transaction_for_session(
        session_id=sess_id,
        family_context_id=fc_id,
        action_type=ActionType.ATTACH,
        resource_type=ResourceType.MEDIA,
        resource_id=state.media1.id,
        resource_label_snapshot="Birthday Dinner Photo",
        operation="Attached photo to event and memory",
    )
    assert rec.action_type == ActionType.ATTACH


def test_generate_celebration_transaction_recorded():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    rec = api.record_transaction_for_session(
        session_id=sess_id,
        family_context_id=fc_id,
        action_type=ActionType.GENERATE,
        resource_type=ResourceType.CELEBRATION_ARTIFACT,
        resource_id="card-123",
        resource_label_snapshot="Alice Birthday Card",
        operation="Generated celebration artifact card",
    )
    assert rec.action_type == ActionType.GENERATE


def test_share_and_revoke_transactions_recorded():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    api.record_transaction_for_session(
        session_id=sess_id,
        family_context_id=fc_id,
        action_type=ActionType.SHARE,
        resource_type=ResourceType.SHARE_LINK,
        resource_id="tok-abc",
        resource_label_snapshot="Tokenized Share Link",
        operation="Created share link",
    )
    api.record_transaction_for_session(
        session_id=sess_id,
        family_context_id=fc_id,
        action_type=ActionType.REVOKE_SHARE,
        resource_type=ResourceType.SHARE_LINK,
        resource_id="tok-abc",
        resource_label_snapshot="Tokenized Share Link",
        operation="Revoked share link",
    )

    history = api.get_resource_history_for_session(sess_id, fc_id, ResourceType.SHARE_LINK, "tok-abc")
    assert len(history) == 2
    assert history[0].action_type == ActionType.REVOKE_SHARE
    assert history[1].action_type == ActionType.SHARE


def test_mayil_proposal_approval_rejection_recorded():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    api.record_transaction_for_session(
        session_id=sess_id,
        family_context_id=fc_id,
        action_type=ActionType.MAYIL_PROPOSAL,
        resource_type=ResourceType.MAYIL_INTERACTION,
        resource_id="prop-1",
        resource_label_snapshot="Calendar Optimization Proposal",
        operation="Mayil proposed reminder adjustment",
    )
    api.record_transaction_for_session(
        session_id=sess_id,
        family_context_id=fc_id,
        action_type=ActionType.MAYIL_APPROVE,
        resource_type=ResourceType.MAYIL_INTERACTION,
        resource_id="prop-1",
        resource_label_snapshot="Calendar Optimization Proposal",
        operation="User approved proposal",
    )

    history = api.get_resource_history_for_session(sess_id, fc_id, ResourceType.MAYIL_INTERACTION, "prop-1")
    assert len(history) == 2


def test_correlation_chain_tracing():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id
    cid = "journey-chain-99"

    api.record_transaction_for_session(
        session_id=sess_id, family_context_id=fc_id, action_type=ActionType.CREATE,
        resource_type=ResourceType.EVENT, resource_id="ev-1", resource_label_snapshot="Event",
        operation="Created event", correlation_id=cid
    )
    api.record_transaction_for_session(
        session_id=sess_id, family_context_id=fc_id, action_type=ActionType.ATTACH,
        resource_type=ResourceType.MEDIA, resource_id="media-1", resource_label_snapshot="Photo",
        operation="Attached photo", correlation_id=cid
    )
    api.record_transaction_for_session(
        session_id=sess_id, family_context_id=fc_id, action_type=ActionType.GENERATE,
        resource_type=ResourceType.CELEBRATION_ARTIFACT, resource_id="art-1", resource_label_snapshot="Album",
        operation="Generated album", correlation_id=cid
    )

    chain = api.transaction_memory.get_correlation_chain(state.session_alice.account_id, fc_id, cid)
    assert len(chain) == 3


def test_privacy_authorization_isolation_bob_cannot_see_alice_private_transactions():
    state = DemoState()
    api = state.api
    alice_sess = state.session_alice.session_id
    bob_sess = state.session_bob.session_id
    fc_id = state.family_context.id

    # Alice records a PRIVATE transaction
    api.record_transaction_for_session(
        session_id=alice_sess,
        family_context_id=fc_id,
        action_type=ActionType.CREATE,
        resource_type=ResourceType.MEMORY,
        resource_id="private-mem-1",
        resource_label_snapshot="Alice Secret Diary",
        operation="Created private memory entry",
        visibility=VisibilityLevel.PRIVATE,
    )

    # Alice can see her private transaction
    alice_hist = api.get_transaction_history_for_session(alice_sess, fc_id)
    assert any(r.resource_id == "private-mem-1" for r in alice_hist)

    # Bob CANNOT see Alice's private transaction
    bob_hist = api.get_transaction_history_for_session(bob_sess, fc_id)
    assert not any(r.resource_id == "private-mem-1" for r in bob_hist)


def test_mayil_explainability_facts_vs_interpretation():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    api.record_transaction_for_session(
        session_id=sess_id,
        family_context_id=fc_id,
        action_type=ActionType.CREATE,
        resource_type=ResourceType.EVENT,
        resource_id=state.event1.id,
        resource_label_snapshot="Alice Birthday",
        operation="Scheduled event",
    )

    explanation = api.explain_resource_history_for_session(sess_id, fc_id, ResourceType.EVENT, state.event1.id)
    assert "recorded_facts" in explanation
    assert "current_state" in explanation
    assert "mayil_interpretation" in explanation
    assert len(explanation["recorded_facts"]) >= 1
    assert "RECORDED FACT" in explanation["recorded_facts"][0]


def test_data_export_includes_transaction_history():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    api.record_transaction_for_session(
        session_id=sess_id,
        family_context_id=fc_id,
        action_type=ActionType.CREATE,
        resource_type=ResourceType.EVENT,
        resource_id=state.event1.id,
        resource_label_snapshot="Alice Birthday",
        operation="Scheduled event",
    )

    export_res = api.export_family_context_for_session(sess_id, fc_id)
    data = export_res.records
    assert "transactions" in data
    assert len(data["transactions"]) >= 1


def test_perspective_switch_records_transaction():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    api.record_transaction_for_session(
        session_id=sess_id,
        family_context_id=fc_id,
        action_type=ActionType.PERSPECTIVE_SWITCH,
        resource_type=ResourceType.ACCOUNT,
        resource_id=state.session_bob.account_id,
        resource_label_snapshot="Bob Smith",
        operation="Switched perspective to Bob Smith",
    )

    history = api.get_transaction_history_for_session(sess_id, fc_id)
    assert any(r.action_type == ActionType.PERSPECTIVE_SWITCH for r in history)


def test_guardian_repair_recorded_in_transactions():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    api.record_transaction_for_session(
        session_id=sess_id,
        family_context_id=fc_id,
        action_type=ActionType.GUARDIAN_REPAIR,
        resource_type=ResourceType.GUARDIAN_EVENT,
        resource_id="repair-1",
        resource_label_snapshot="Rebuilt Calendar Projections",
        operation="Executed repair proposal for projection desync",
    )

    history = api.get_transaction_history_for_session(sess_id, fc_id, resource_type=ResourceType.GUARDIAN_EVENT)
    assert len(history) >= 1
    assert history[0].action_type == ActionType.GUARDIAN_REPAIR
