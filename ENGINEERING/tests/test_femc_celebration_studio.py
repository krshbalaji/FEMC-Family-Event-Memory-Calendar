import datetime
import pytest

from ENGINEERING.source.femc.api import FEMCApi
from ENGINEERING.source.femc.models import (
    CelebrationArtifact,
    CelebrationArtifactType,
    EventCategory,
    MediaType,
    RecurrenceFrequency,
    RecurrenceRule,
    RepairClassification,
    ShareResourceType,
    VisibilityLevel,
)


def _setup_baseline_context():
    api = FEMCApi()
    p1 = api.identity.create_person(name="Alice Member", birth_date=datetime.date(1990, 5, 15))
    acc1 = api.identity.create_account(username="alice", email="alice@family.org", person_id=p1.id)

    p2 = api.identity.create_person(name="Bob Member", birth_date=datetime.date(1988, 10, 20))
    acc2 = api.identity.create_account(username="bob", email="bob@family.org", person_id=p2.id)

    p3 = api.identity.create_person(name="Stranger")
    acc3 = api.identity.create_account(username="stranger", email="stranger@other.org", person_id=p3.id)

    fc = api.identity.create_family_context("Smith Family", member_ids=[acc1.id, acc2.id], created_by_id=acc1.id)
    s1 = api.create_session(acc1.id)
    s2 = api.create_session(acc2.id)
    s3 = api.create_session(acc3.id)

    return api, acc1, acc2, acc3, p1, p2, p3, fc, s1, s2, s3


def test_celebration_artifact_type_semantics():
    assert CelebrationArtifactType.BIRTHDAY_CARD.value == "birthday_card"
    assert CelebrationArtifactType.ANNIVERSARY_CARD.value == "anniversary_card"
    assert CelebrationArtifactType.MILESTONE_CARD.value == "milestone_card"
    assert CelebrationArtifactType.FAMILY_MEMORY_CARD.value == "family_memory_card"
    assert CelebrationArtifactType.EVENT_HIGHLIGHT.value == "event_highlight"
    assert CelebrationArtifactType.CELEBRATION_ALBUM.value == "celebration_album"


def test_birthday_artifact_generation():
    api, acc1, acc2, acc3, p1, p2, p3, fc, s1, s2, s3 = _setup_baseline_context()
    now = datetime.datetime.utcnow()

    event = api.create_event_for_session(
        session_id=s1.session_id,
        title="Alice's 36th Birthday",
        description="Celebrate Alice turning 36",
        family_context_id=fc.id,
        start_time=now,
        end_time=now + datetime.timedelta(hours=2),
        category=EventCategory.BIRTHDAY,
        target_person_ids=[p1.id],
    )

    artifact = api.build_celebration_artifact_for_event_for_session(s1.session_id, event.id)
    assert isinstance(artifact, CelebrationArtifact)
    assert artifact.artifact_type == CelebrationArtifactType.BIRTHDAY_CARD
    assert "Birthday Celebration" in artifact.title
    assert artifact.source_event_id == event.id
    assert artifact.source_person_id == p1.id


def test_anniversary_artifact_generation():
    api, acc1, acc2, acc3, p1, p2, p3, fc, s1, s2, s3 = _setup_baseline_context()
    now = datetime.datetime.utcnow()

    event = api.create_event_for_session(
        session_id=s1.session_id,
        title="Silver Anniversary",
        description="25 years together",
        family_context_id=fc.id,
        start_time=now,
        end_time=now + datetime.timedelta(hours=3),
        category=EventCategory.ANNIVERSARY,
        target_person_ids=[p1.id, p2.id],
        milestone_year=25,
    )

    artifact = api.build_celebration_artifact_for_event_for_session(s1.session_id, event.id)
    assert artifact.artifact_type == CelebrationArtifactType.ANNIVERSARY_CARD
    assert "25 Years" in artifact.title
    assert artifact.source_event_id == event.id


def test_milestone_artifact_generation():
    api, acc1, acc2, acc3, p1, p2, p3, fc, s1, s2, s3 = _setup_baseline_context()
    now = datetime.datetime.utcnow()

    event = api.create_event_for_session(
        session_id=s1.session_id,
        title="Graduation Milestone",
        description="Graduated college",
        family_context_id=fc.id,
        start_time=now,
        end_time=now + datetime.timedelta(hours=2),
        category=EventCategory.MILESTONE,
        target_person_ids=[p1.id],
    )

    artifact = api.build_celebration_artifact_for_event_for_session(s1.session_id, event.id)
    assert artifact.artifact_type == CelebrationArtifactType.MILESTONE_CARD
    assert artifact.source_event_id == event.id


def test_family_memory_artifact_generation():
    api, acc1, acc2, acc3, p1, p2, p3, fc, s1, s2, s3 = _setup_baseline_context()
    now = datetime.datetime.utcnow()
    event = api.create_event_for_session(
        session_id=s1.session_id,
        title="Summer Camp 2015",
        description="Camp memory event",
        family_context_id=fc.id,
        start_time=now,
        end_time=now + datetime.timedelta(hours=2),
    )
    memory = api.create_memory_for_session(
        session_id=s1.session_id,
        event_id=event.id,
        narrative="A beautiful memory of summer camp in 2015",
    )

    artifact = api.build_celebration_artifact_for_memory_for_session(s1.session_id, memory.id)
    assert artifact.artifact_type == CelebrationArtifactType.FAMILY_MEMORY_CARD
    assert artifact.source_memory_id == memory.id
    assert "A beautiful memory" in artifact.subtitle


def test_deterministic_artifact_generation():
    api, acc1, acc2, acc3, p1, p2, p3, fc, s1, s2, s3 = _setup_baseline_context()
    now = datetime.datetime(2026, 8, 1, 12, 0, 0)

    event = api.create_event_for_session(
        session_id=s1.session_id,
        title="Deterministic Milestone",
        description="Static desc",
        family_context_id=fc.id,
        start_time=now,
        end_time=now + datetime.timedelta(hours=2),
        category=EventCategory.MILESTONE,
    )

    art1 = api.build_celebration_artifact_for_event_for_session(s1.session_id, event.id)
    art2 = api.build_celebration_artifact_for_event_for_session(s1.session_id, event.id)

    assert art1.rendered_content == art2.rendered_content
    assert art1.content_hash == art2.content_hash
    assert len(art1.content_hash) == 64  # SHA256 hex string length


def test_event_person_source_linkage():
    api, acc1, acc2, acc3, p1, p2, p3, fc, s1, s2, s3 = _setup_baseline_context()
    artifact = api.build_celebration_artifact_for_person_for_session(s1.session_id, p1.id, fc.id)
    assert artifact.source_person_id == p1.id
    assert artifact.family_context_id == fc.id


def test_media_item_integration():
    api, acc1, acc2, acc3, p1, p2, p3, fc, s1, s2, s3 = _setup_baseline_context()
    now = datetime.datetime.utcnow()

    event = api.create_event_for_session(
        session_id=s1.session_id,
        title="Photo Event",
        description="Event with artifact media",
        family_context_id=fc.id,
        start_time=now,
        end_time=now + datetime.timedelta(hours=2),
    )

    artifact = api.build_celebration_artifact_for_event_for_session(s1.session_id, event.id, attach_as_media=True)
    assert artifact.media_item_id is not None

    # Retrieve media item directly from media service
    media_item = api.media.get_media_item_for_account(artifact.media_item_id, acc1.id)
    assert media_item is not None
    assert media_item.event_id == event.id
    assert media_item.uri.startswith("celebration://")


def test_visibility_and_privacy():
    api, acc1, acc2, acc3, p1, p2, p3, fc, s1, s2, s3 = _setup_baseline_context()
    now = datetime.datetime.utcnow()

    event = api.create_event_for_session(
        session_id=s1.session_id,
        title="Private Celebration",
        description="Private description",
        family_context_id=fc.id,
        start_time=now,
        end_time=now + datetime.timedelta(hours=2),
        visibility=VisibilityLevel.PRIVATE,
    )

    artifact = api.build_celebration_artifact_for_event_for_session(s1.session_id, event.id)
    assert artifact.visibility == VisibilityLevel.PRIVATE

    # Owner can view
    retrieved = api.get_celebration_artifact_for_session(s1.session_id, artifact.id)
    assert retrieved.id == artifact.id

    # Non-owner in same family context cannot view private artifact
    with pytest.raises(PermissionError):
        api.get_celebration_artifact_for_session(s2.session_id, artifact.id)


def test_unauthorized_access_prevention():
    api, acc1, acc2, acc3, p1, p2, p3, fc, s1, s2, s3 = _setup_baseline_context()
    now = datetime.datetime.utcnow()

    event = api.create_event_for_session(
        session_id=s1.session_id,
        title="Family Gathering",
        description="Family only",
        family_context_id=fc.id,
        start_time=now,
        end_time=now + datetime.timedelta(hours=2),
    )

    # Stranger (s3) cannot build artifact for family event
    with pytest.raises(PermissionError):
        api.build_celebration_artifact_for_event_for_session(s3.session_id, event.id)


def test_target_person_authorization():
    api, acc1, acc2, acc3, p1, p2, p3, fc, s1, s2, s3 = _setup_baseline_context()
    # Stranger (s3) cannot build person celebration artifact for Smith family member
    with pytest.raises(PermissionError):
        api.build_celebration_artifact_for_person_for_session(s3.session_id, p1.id, fc.id)


def test_recurring_event_handling_without_canonical_duplication():
    api, acc1, acc2, acc3, p1, p2, p3, fc, s1, s2, s3 = _setup_baseline_context()
    now = datetime.datetime(2026, 9, 1, 10, 0)
    rule = RecurrenceRule(frequency=RecurrenceFrequency.YEARLY, interval=1)

    initial_event_count = len(api.canonical.list_events())

    ev = api.create_event_for_session(
        session_id=s1.session_id,
        title="Annual Reunion",
        description="Every year",
        family_context_id=fc.id,
        start_time=now,
        end_time=now + datetime.timedelta(hours=2),
        recurrence_rule=rule,
        category=EventCategory.ANNIVERSARY,
    )

    assert len(api.canonical.list_events()) == initial_event_count + 1

    art = api.build_celebration_artifact_for_event_for_session(s1.session_id, ev.id)
    assert art.source_event_id == ev.id

    # Confirm canonical events dictionary count is unchanged after generating artifact
    assert len(api.canonical.list_events()) == initial_event_count + 1


def test_sharing_integration_via_media_item():
    api, acc1, acc2, acc3, p1, p2, p3, fc, s1, s2, s3 = _setup_baseline_context()
    now = datetime.datetime.utcnow()

    event = api.create_event_for_session(
        session_id=s1.session_id,
        title="Shareable Celebration",
        description="Share with family link",
        family_context_id=fc.id,
        start_time=now,
        end_time=now + datetime.timedelta(hours=2),
        visibility=VisibilityLevel.FAMILY,
    )

    artifact = api.build_celebration_artifact_for_event_for_session(s1.session_id, event.id, attach_as_media=True)
    assert artifact.media_item_id is not None

    # Share via existing ShareResourceType.MEDIA_ITEM
    share_link = api.create_share_link_for_session(
        session_id=s1.session_id,
        resource_type=ShareResourceType.MEDIA_ITEM,
        resource_id=artifact.media_item_id,
        family_context_id=fc.id,
    )

    assert share_link.token is not None
    assert share_link.resource_id == artifact.media_item_id


def test_data_portability_compatibility():
    api, acc1, acc2, acc3, p1, p2, p3, fc, s1, s2, s3 = _setup_baseline_context()
    now = datetime.datetime.utcnow()

    ev = api.create_event_for_session(
        session_id=s1.session_id,
        title="Portable Event",
        description="Export check",
        family_context_id=fc.id,
        start_time=now,
        end_time=now + datetime.timedelta(hours=2),
        category=EventCategory.MILESTONE,
    )

    api.build_celebration_artifact_for_event_for_session(s1.session_id, ev.id, attach_as_media=True)

    export_res = api.data_portability.export_family_context_for_account(acc1.id, fc.id)
    assert "events" in export_res.records
    assert "media_items" in export_res.records
    assert len(export_res.records["events"]) == 1
    assert len(export_res.records["media_items"]) == 1


def test_mayil_read_only_behavior():
    api, acc1, acc2, acc3, p1, p2, p3, fc, s1, s2, s3 = _setup_baseline_context()
    now = datetime.datetime.utcnow()

    ev = api.create_event_for_session(
        session_id=s1.session_id,
        title="Mayil Target",
        description="Mayil proposal test",
        family_context_id=fc.id,
        start_time=now,
        end_time=now + datetime.timedelta(hours=2),
        category=EventCategory.BIRTHDAY,
    )

    initial_event_count = len(api.canonical.list_events())

    proposal = api.mayil.propose_celebration_artifact_recommendation(acc1.id, fc.id, ev.id)
    assert proposal.id is not None
    assert proposal.proposed_changes["action"] == "build_celebration_artifact"
    assert proposal.proposed_changes["event_id"] == ev.id

    # Confirm canonical event count remains unchanged (Mayil is read-only)
    assert len(api.canonical.list_events()) == initial_event_count


def test_vel_guardian_dangling_source_validation():
    api, acc1, acc2, acc3, p1, p2, p3, fc, s1, s2, s3 = _setup_baseline_context()
    now = datetime.datetime.utcnow()

    ev = api.create_event_for_session(
        session_id=s1.session_id,
        title="Temporary Event",
        description="To be deleted",
        family_context_id=fc.id,
        start_time=now,
        end_time=now + datetime.timedelta(hours=2),
    )

    artifact = api.build_celebration_artifact_for_event_for_session(s1.session_id, ev.id)
    assert artifact.source_event_id == ev.id

    # Simulate canonical deletion resulting in dangling reference
    del api.canonical.events[ev.id]

    report = api.run_integrity_audit_for_session(s1.session_id, fc.id)
    assert report.is_valid is False
    dangling_anomalies = [a for a in report.anomalies if a.affected_entity_id == artifact.id]
    assert len(dangling_anomalies) >= 1
    assert dangling_anomalies[0].repair_proposal.classification == RepairClassification.DERIVED_ONLY


def test_vel_guardian_derived_repair_execution():
    api, acc1, acc2, acc3, p1, p2, p3, fc, s1, s2, s3 = _setup_baseline_context()
    now = datetime.datetime.utcnow()

    ev = api.create_event_for_session(
        session_id=s1.session_id,
        title="Repair Event",
        description="Derived repair target",
        family_context_id=fc.id,
        start_time=now,
        end_time=now + datetime.timedelta(hours=2),
        category=EventCategory.MILESTONE,
    )

    api.build_celebration_artifact_for_event_for_session(s1.session_id, ev.id)
    assert len(api.derived.get_celebration_artifacts(fc.id)) == 1

    # Desync: Clear derived celebration artifacts
    api.derived.clear_celebration_artifacts(fc.id)
    assert len(api.derived.get_celebration_artifacts(fc.id)) == 0

    # Create repair proposal and execute
    proposal = api.guardian._create_repair_proposal(
        "rebuild_derived_projections", "CelebrationArtifact", ev.id, fc.id, classification=RepairClassification.DERIVED_ONLY
    )

    executed = api.execute_repair_proposal_for_session(s1.session_id, proposal.id)
    assert executed.is_executed is True

    # Confirm derived celebration artifacts rebuilt
    rebuilt = api.derived.get_celebration_artifacts(fc.id)
    assert len(rebuilt) >= 1


def test_canonical_immutability_during_artifact_generation():
    api, acc1, acc2, acc3, p1, p2, p3, fc, s1, s2, s3 = _setup_baseline_context()
    now = datetime.datetime.utcnow()

    ev = api.create_event_for_session(
        session_id=s1.session_id,
        title="Immutable Event",
        description="Check immutability",
        family_context_id=fc.id,
        start_time=now,
        end_time=now + datetime.timedelta(hours=2),
    )

    ev_title_before = ev.title
    ev_desc_before = ev.description

    art = api.build_celebration_artifact_for_event_for_session(s1.session_id, ev.id)
    assert art.id is not None

    assert ev.title == ev_title_before
    assert ev.description == ev_desc_before


def test_malformed_dangling_source_handling():
    api, acc1, acc2, acc3, p1, p2, p3, fc, s1, s2, s3 = _setup_baseline_context()
    with pytest.raises(ValueError):
        api.build_celebration_artifact_for_event_for_session(s1.session_id, "non-existent-event-id")
    with pytest.raises(ValueError):
        api.build_celebration_artifact_for_person_for_session(s1.session_id, "non-existent-person-id", fc.id)
    with pytest.raises(ValueError):
        api.build_celebration_artifact_for_memory_for_session(s1.session_id, "non-existent-memory-id")
