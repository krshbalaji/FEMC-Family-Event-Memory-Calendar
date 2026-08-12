import datetime
import json
import pytest
from ENGINEERING.source.femc.api import FEMCApi
from ENGINEERING.source.femc.models import MediaType, ProvenanceSourceType, VisibilityLevel


def test_authorized_family_export_and_contents():
    api = FEMCApi()

    # Create Family Context and Members
    member_a_person = api.identity.create_person("Alice Member")
    member_a_account = api.identity.create_account("alice", "alice@example.com", member_a_person.id)
    session_a = api.create_session(member_a_account.id)

    member_b_person = api.identity.create_person("Bob Member")
    member_b_account = api.identity.create_account("bob", "bob@example.com", member_b_person.id)

    context = api.identity.create_family_context(
        "Portability Family", member_ids=[member_a_account.id, member_b_account.id], created_by_id=member_a_account.id
    )

    # Add Relationship
    api.identity.create_relationship(member_a_person.id, member_b_person.id, "parent", context.id)

    # Add Place, Event, Memory, Media
    place = api.create_place_for_session(session_a.session_id, "Home Base", "123 Main St", context.id)
    event = api.create_event_for_session(
        session_a.session_id,
        "Family Gathering",
        "Reunion event",
        context.id,
        datetime.datetime(2026, 10, 1, 12, 0),
        None,
        place_id=place.id,
    )
    memory = api.create_memory_for_session(session_a.session_id, event.id, "Wonderful dinner together")
    media = api.create_media_item_for_session(
        session_a.session_id, "https://example.com/reunion.jpg", MediaType.PHOTO, "Photo of reunion", context.id, event_id=event.id
    )

    # Execute Export
    export = api.export_family_context_for_session(session_a.session_id, context.id)

    assert export.export_id is not None
    assert export.family_context_id == context.id
    assert export.schema_version == "1.0"

    # Test 5: Provenance included
    assert export.provenance is not None
    assert export.provenance.source_type == ProvenanceSourceType.SYSTEM
    assert export.provenance.source_id == "femc-data-portability"

    records = export.records
    assert len(records["family_contexts"]) == 1
    assert records["family_contexts"][0]["id"] == context.id
    assert len(records["accounts"]) == 2
    assert len(records["persons"]) == 2
    assert len(records["relationships"]) == 1
    assert len(records["events"]) == 1
    assert len(records["memories"]) == 1
    assert len(records["places"]) == 1
    assert len(records["media_items"]) == 1

    # Test 4: Stable cross-record references
    assert records["events"][0]["place_id"] == place.id
    assert records["memories"][0]["event_id"] == event.id
    assert records["media_items"][0]["event_id"] == event.id

    # Test 6: Credentials/session secrets absent
    for acc_record in records["accounts"]:
        assert "password_hash" not in acc_record
        assert "session_token" not in acc_record
        assert "auth_token" not in acc_record


def test_unauthorized_family_export_blocked():
    api = FEMCApi()

    owner_person = api.identity.create_person("Owner")
    owner_account = api.identity.create_account("owner", "owner@example.com", owner_person.id)
    context = api.identity.create_family_context("Private Family", member_ids=[owner_account.id], created_by_id=owner_account.id)

    outsider_person = api.identity.create_person("Outsider")
    outsider_account = api.identity.create_account("outsider", "outsider@example.com", outsider_person.id)
    outsider_session = api.create_session(outsider_account.id)

    with pytest.raises(PermissionError):
        api.export_family_context_for_session(outsider_session.session_id, context.id)


def test_privacy_filtering_in_export():
    api = FEMCApi()

    alice_person = api.identity.create_person("Alice")
    alice_account = api.identity.create_account("alice_p", "alice_p@example.com", alice_person.id)
    alice_session = api.create_session(alice_account.id)

    bob_person = api.identity.create_person("Bob")
    bob_account = api.identity.create_account("bob_p", "bob_p@example.com", bob_person.id)
    bob_session = api.create_session(bob_account.id)

    context = api.identity.create_family_context(
        "Shared Context", member_ids=[alice_account.id, bob_account.id], created_by_id=alice_account.id
    )

    # Bob creates a PRIVATE event
    bob_private_event = api.create_event_for_session(
        bob_session.session_id,
        "Bob's Private Thoughts",
        "Secret",
        context.id,
        datetime.datetime(2026, 10, 2, 10, 0),
        None,
        visibility=VisibilityLevel.PRIVATE,
    )

    # Alice creates a FAMILY event
    alice_family_event = api.create_event_for_session(
        alice_session.session_id,
        "Alice's Family Event",
        "Open to family",
        context.id,
        datetime.datetime(2026, 10, 2, 14, 0),
        None,
        visibility=VisibilityLevel.FAMILY,
    )

    # Alice exports context -> Bob's private event MUST be excluded from Alice's export
    alice_export = api.export_family_context_for_session(alice_session.session_id, context.id)
    exported_event_ids = [e["id"] for e in alice_export.records["events"]]

    assert alice_family_event.id in exported_event_ids
    assert bob_private_event.id not in exported_event_ids


def test_deterministic_json_compatibility():
    api = FEMCApi()

    person = api.identity.create_person("JSON User")
    account = api.identity.create_account("json_user", "json@example.com", person.id)
    context = api.identity.create_family_context("JSON Family", member_ids=[account.id], created_by_id=account.id)
    session = api.create_session(account.id)

    api.create_event_for_session(
        session.session_id,
        "JSON Event",
        "Test JSON serialization",
        context.id,
        datetime.datetime(2026, 10, 5, 9, 0),
        None,
    )

    export = api.export_family_context_for_session(session.session_id, context.id)

    # Serialize to JSON dictionary
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

    json_str = json.dumps(export_payload)
    assert len(json_str) > 0
    parsed = json.loads(json_str)
    assert parsed["schema_version"] == "1.0"


def test_malformed_export_validation():
    api = FEMCApi()

    # 1. Valid export payload validation
    valid_payload = {
        "export_id": "exp-123",
        "family_context_id": "ctx-456",
        "exported_at": "2026-10-05T10:00:00",
        "schema_version": "1.0",
        "provenance": {"source_type": "system", "source_id": "femc-data-portability", "audit_trail": []},
        "records": {"events": [{"id": "ev-1"}]},
    }
    val_res = api.validate_data_export(valid_payload)
    assert val_res.is_valid is True
    assert val_res.record_counts["events"] == 1

    # 2. Invalid schema version
    invalid_schema = dict(valid_payload, schema_version="99.0")
    val_invalid = api.validate_data_export(invalid_schema)
    assert val_invalid.is_valid is False
    assert any("schema_version" in err for err in val_invalid.errors)

    # 3. Missing required field
    missing_id = dict(valid_payload)
    del missing_id["export_id"]
    val_missing = api.validate_data_export(missing_id)
    assert val_missing.is_valid is False
    assert any("export_id" in err for err in val_missing.errors)


def test_export_does_not_mutate_canonical_repository():
    api = FEMCApi()

    person = api.identity.create_person("Pure User")
    account = api.identity.create_account("pure", "pure@example.com", person.id)
    context = api.identity.create_family_context("Pure Family", member_ids=[account.id], created_by_id=account.id)
    session = api.create_session(account.id)

    api.create_event_for_session(
        session.session_id,
        "Pure Event",
        "No mutation",
        context.id,
        datetime.datetime(2026, 10, 5, 9, 0),
        None,
    )

    events_before = len(api.canonical.list_events())
    contexts_before = len(api.canonical.list_family_contexts())

    # Perform export
    api.export_family_context_for_session(session.session_id, context.id)

    events_after = len(api.canonical.list_events())
    contexts_after = len(api.canonical.list_family_contexts())

    assert events_before == events_after
    assert contexts_before == contexts_after
