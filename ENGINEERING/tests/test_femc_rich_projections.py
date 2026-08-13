import datetime
import pytest

from ENGINEERING.source.femc.api import FEMCApi
from ENGINEERING.source.femc.models import (
    DashboardEntryType,
    DashboardProjectionEntry,
    DashboardSummary,
    EventCategory,
    EventStatus,
    MediaType,
    RecurrenceFrequency,
    RecurrenceRule,
    Relationship,
    ReminderType,
    RepairClassification,
    RichEventDetail,
    RichPersonDetail,
    VisibilityLevel,
)


def _setup_baseline_context():
    api = FEMCApi()
    p1 = api.identity.create_person(name="Alice", birth_date=datetime.date(1990, 5, 15))
    acc1 = api.identity.create_account(username="alice", email="alice@family.org", person_id=p1.id)

    p2 = api.identity.create_person(name="Bob", birth_date=datetime.date(1988, 10, 20))
    acc2 = api.identity.create_account(username="bob", email="bob@family.org", person_id=p2.id)

    fc = api.identity.create_family_context("Smith Family", member_ids=[acc1.id, acc2.id], created_by_id=acc1.id)
    s1 = api.create_session(acc1.id)
    s2 = api.create_session(acc2.id)

    return api, acc1, acc2, p1, p2, fc, s1, s2


def test_create_event_with_cluster9_attributes():
    api, acc1, acc2, p1, p2, fc, s1, s2 = _setup_baseline_context()
    now = datetime.datetime.utcnow()
    anchor = datetime.date(2000, 1, 1)

    event = api.create_event_for_session(
        session_id=s1.session_id,
        title="25th Anniversary",
        description="Silver jubilee celebration",
        family_context_id=fc.id,
        start_time=now,
        end_time=now + datetime.timedelta(hours=3),
        category=EventCategory.ANNIVERSARY,
        target_person_ids=[p1.id, p2.id],
        milestone_anchor_date=anchor,
    )

    assert event.category == EventCategory.ANNIVERSARY
    assert event.target_person_ids == [p1.id, p2.id]
    assert event.milestone_anchor_date == anchor


def test_build_rich_event_detail_basic():
    api, acc1, acc2, p1, p2, fc, s1, s2 = _setup_baseline_context()
    now = datetime.datetime.utcnow()

    event = api.create_event_for_session(
        session_id=s1.session_id,
        title="Family Reunion",
        description="Annual gathering",
        family_context_id=fc.id,
        start_time=now,
        end_time=now + datetime.timedelta(hours=4),
        target_person_ids=[p1.id],
    )

    place = api.create_place_for_session(
        session_id=s1.session_id,
        name="Grand Hall",
        address="123 Main St",
        family_context_id=fc.id,
    )
    event.place_id = place.id

    memory = api.create_memory_for_session(
        session_id=s1.session_id,
        event_id=event.id,
        narrative="Had a great time at reunion",
    )

    media = api.media.create_media_item(
        owner_id=acc1.id,
        uri="https://media.org/photo1.jpg",
        media_type=MediaType.PHOTO,
        caption="Group photo",
        family_context_id=fc.id,
        event_id=event.id,
    )

    reminder = api.configure_reminder_for_session(
        session_id=s1.session_id,
        event_id=event.id,
        offset_minutes=30,
        reminder_type=ReminderType.EVENT_START,
    )

    detail = api.build_rich_event_detail_for_session(s1.session_id, event.id)
    assert isinstance(detail, RichEventDetail)
    assert detail.event.id == event.id
    assert detail.place.id == place.id
    assert len(detail.memories) == 1
    assert detail.memories[0].id == memory.id
    assert len(detail.media_items) == 1
    assert len(detail.reminders) == 1
    assert len(detail.target_persons) == 1
    assert detail.target_persons[0].id == p1.id


def test_build_rich_event_detail_unauthorized():
    api, acc1, acc2, p1, p2, fc, s1, s2 = _setup_baseline_context()
    now = datetime.datetime.utcnow()

    p3 = api.identity.create_person(name="Stranger")
    acc3 = api.identity.create_account(username="stranger", email="stranger@other.org", person_id=p3.id)
    s3 = api.create_session(acc3.id)

    event = api.create_event_for_session(
        session_id=s1.session_id,
        title="Private Dinner",
        description="Secret event",
        family_context_id=fc.id,
        start_time=now,
        end_time=now + datetime.timedelta(hours=2),
        visibility=VisibilityLevel.PRIVATE,
    )

    with pytest.raises(PermissionError):
        api.build_rich_event_detail_for_session(s3.session_id, event.id)


def test_build_rich_event_detail_deterministic_milestone_year():
    api, acc1, acc2, p1, p2, fc, s1, s2 = _setup_baseline_context()
    now = datetime.datetime(2026, 6, 1, 10, 0, 0)
    anchor = datetime.date(2001, 6, 1)

    event = api.create_event_for_session(
        session_id=s1.session_id,
        title="Silver Jubilee",
        description="25 year milestone",
        family_context_id=fc.id,
        start_time=now,
        end_time=now + datetime.timedelta(hours=2),
        category=EventCategory.MILESTONE,
        milestone_anchor_date=anchor,
    )

    detail = api.build_rich_event_detail_for_session(s1.session_id, event.id)
    assert detail.milestone_year == 25


def test_build_rich_event_detail_milestone_derivation_from_target_person():
    api, acc1, acc2, p1, p2, fc, s1, s2 = _setup_baseline_context()
    now = datetime.datetime(2026, 5, 15, 10, 0, 0)

    event = api.create_event_for_session(
        session_id=s1.session_id,
        title="Alice's Birthday",
        description="Birthday party",
        family_context_id=fc.id,
        start_time=now,
        end_time=now + datetime.timedelta(hours=2),
        category=EventCategory.BIRTHDAY,
        target_person_ids=[p1.id],
    )

    detail = api.build_rich_event_detail_for_session(s1.session_id, event.id)
    assert detail.milestone_year == 36


def test_build_rich_event_detail_upcoming_occurrences():
    api, acc1, acc2, p1, p2, fc, s1, s2 = _setup_baseline_context()
    now = datetime.datetime(2026, 1, 1, 9, 0, 0)
    rrule = RecurrenceRule(frequency=RecurrenceFrequency.WEEKLY, interval=1)

    event = api.create_event_for_session(
        session_id=s1.session_id,
        title="Weekly Meeting",
        description="Sync meeting",
        family_context_id=fc.id,
        start_time=now,
        end_time=now + datetime.timedelta(hours=1),
        recurrence_rule=rrule,
    )

    detail = api.build_rich_event_detail_for_session(s1.session_id, event.id)
    assert len(detail.upcoming_occurrences) > 1
    assert detail.upcoming_occurrences[0] == datetime.date(2026, 1, 1)


def test_build_rich_person_detail_basic():
    api, acc1, acc2, p1, p2, fc, s1, s2 = _setup_baseline_context()
    now = datetime.datetime.utcnow()

    rel = api.identity.canonical.add_relationship(
        Relationship(source_person_id=p1.id, target_person_id=p2.id)
    )

    event = api.create_event_for_session(
        session_id=s1.session_id,
        title="Person Event",
        description="Targeted event",
        family_context_id=fc.id,
        start_time=now,
        end_time=now + datetime.timedelta(hours=2),
        category=EventCategory.MILESTONE,
        target_person_ids=[p1.id],
    )

    memory = api.create_memory_for_session(
        session_id=s1.session_id,
        event_id=event.id,
        narrative="Memory for person event",
    )

    media_item = api.media.create_media_item(
        owner_id=acc1.id,
        uri="http://example.com/photo.jpg",
        caption="Photo of person event",
        event_id=event.id,
        family_context_id=fc.id,
    )

    detail = api.build_rich_person_detail_for_session(s1.session_id, p1.id)
    assert isinstance(detail, RichPersonDetail)
    assert detail.person.id == p1.id
    assert detail.account.id == acc1.id
    assert len(detail.relationships) >= 1
    assert len(detail.events) >= 1
    assert len(detail.milestones) == 1
    assert len(detail.memories) >= 1
    assert len(detail.media_items) >= 1


def test_build_rich_person_detail_unauthorized():
    api, acc1, acc2, p1, p2, fc, s1, s2 = _setup_baseline_context()
    with pytest.raises(ValueError):
        api.build_rich_person_detail_for_session(s1.session_id, "non-existent-person-id")


def test_build_rich_person_detail_milestones_filter():
    api, acc1, acc2, p1, p2, fc, s1, s2 = _setup_baseline_context()
    now = datetime.datetime.utcnow()

    ev1 = api.create_event_for_session(
        session_id=s1.session_id,
        title="Regular Lunch",
        description="Just lunch",
        family_context_id=fc.id,
        start_time=now,
        end_time=now + datetime.timedelta(hours=1),
        category=EventCategory.GENERAL,
        target_person_ids=[p1.id],
    )

    ev2 = api.create_event_for_session(
        session_id=s1.session_id,
        title="Graduation",
        description="College graduation",
        family_context_id=fc.id,
        start_time=now,
        end_time=now + datetime.timedelta(hours=2),
        category=EventCategory.MILESTONE,
        target_person_ids=[p1.id],
    )

    detail = api.build_rich_person_detail_for_session(s1.session_id, p1.id)
    assert len(detail.events) == 2
    assert len(detail.milestones) == 1
    assert detail.milestones[0].id == ev2.id


def test_generate_dashboard_summary_basic():
    api, acc1, acc2, p1, p2, fc, s1, s2 = _setup_baseline_context()
    now = datetime.datetime.utcnow()

    api.create_event_for_session(
        session_id=s1.session_id,
        title="Birthday Party",
        description="Celebrate birthday",
        family_context_id=fc.id,
        start_time=now,
        end_time=now + datetime.timedelta(hours=2),
        category=EventCategory.BIRTHDAY,
    )

    summary = api.get_dashboard_summary_for_session(s1.session_id, fc.id)
    assert isinstance(summary, DashboardSummary)
    assert summary.member_count == 2
    assert len(summary.upcoming_events) == 1
    assert len(summary.celebration_highlights) == 1


def test_generate_dashboard_summary_unauthorized():
    api, acc1, acc2, p1, p2, fc, s1, s2 = _setup_baseline_context()
    p3 = api.identity.create_person(name="Outsider")
    acc3 = api.identity.create_account(username="outsider", email="outsider@test.org", person_id=p3.id)
    s3 = api.create_session(acc3.id)

    with pytest.raises(PermissionError):
        api.get_dashboard_summary_for_session(s3.session_id, fc.id)


def test_project_dashboard_entries():
    api, acc1, acc2, p1, p2, fc, s1, s2 = _setup_baseline_context()
    now = datetime.datetime.utcnow()

    ev = api.create_event_for_session(
        session_id=s1.session_id,
        title="Project Meeting",
        description="Discussion",
        family_context_id=fc.id,
        start_time=now,
        end_time=now + datetime.timedelta(hours=1),
    )

    projected = api.project_dashboard_entries_for_session(s1.session_id, fc.id)
    assert len(projected) >= 1
    assert any(p.ref_id == ev.id for p in projected)


def test_get_dashboard_projection_filtering():
    api, acc1, acc2, p1, p2, fc, s1, s2 = _setup_baseline_context()
    now = datetime.datetime.utcnow()

    api.create_event_for_session(
        session_id=s1.session_id,
        title="Event 1",
        description="Desc 1",
        family_context_id=fc.id,
        start_time=now,
        end_time=now + datetime.timedelta(hours=1),
    )

    entries = api.get_dashboard_projection_for_session(s1.session_id, fc.id)
    assert len(entries) >= 1
    assert isinstance(entries[0], DashboardProjectionEntry)


def test_dashboard_entry_types_enum():
    assert DashboardEntryType.UPCOMING_EVENT.value == "upcoming_event"
    assert DashboardEntryType.RECURRING_EVENT.value == "recurring_event"
    assert DashboardEntryType.DUE_REMINDER.value == "due_reminder"
    assert DashboardEntryType.RECENT_MEMORY.value == "recent_memory"
    assert DashboardEntryType.ACTIVE_NOTIFICATION.value == "active_notification"
    assert DashboardEntryType.CELEBRATION_HIGHLIGHT.value == "celebration_highlight"


def test_event_category_enum_values():
    assert EventCategory.BIRTHDAY.value == "birthday"
    assert EventCategory.ANNIVERSARY.value == "anniversary"
    assert EventCategory.MILESTONE.value == "milestone"
    assert EventCategory.HOLIDAY.value == "holiday"
    assert EventCategory.GENERAL.value == "general"


def test_api_build_rich_event_detail_for_session():
    api, acc1, acc2, p1, p2, fc, s1, s2 = _setup_baseline_context()
    now = datetime.datetime.utcnow()
    ev = api.create_event_for_session(
        session_id=s1.session_id,
        title="Test Event",
        description="Detail test",
        family_context_id=fc.id,
        start_time=now,
        end_time=now + datetime.timedelta(hours=1),
    )
    detail = api.build_rich_event_detail_for_session(s1.session_id, ev.id)
    assert detail.event.id == ev.id


def test_api_build_rich_person_detail_for_session():
    api, acc1, acc2, p1, p2, fc, s1, s2 = _setup_baseline_context()
    detail = api.build_rich_person_detail_for_session(s1.session_id, p1.id)
    assert detail.person.id == p1.id


def test_api_get_dashboard_summary_for_session():
    api, acc1, acc2, p1, p2, fc, s1, s2 = _setup_baseline_context()
    summary = api.get_dashboard_summary_for_session(s1.session_id, fc.id)
    assert summary.family_context.id == fc.id


def test_api_project_and_get_dashboard_projection_for_session():
    api, acc1, acc2, p1, p2, fc, s1, s2 = _setup_baseline_context()
    p_entries = api.project_dashboard_entries_for_session(s1.session_id, fc.id)
    g_entries = api.get_dashboard_projection_for_session(s1.session_id, fc.id)
    assert len(g_entries) == len(p_entries)


def test_data_portability_cluster9_integration():
    api, acc1, acc2, p1, p2, fc, s1, s2 = _setup_baseline_context()
    now = datetime.datetime.utcnow()

    api.create_event_for_session(
        session_id=s1.session_id,
        title="Exportable Milestone",
        description="Portability check",
        family_context_id=fc.id,
        start_time=now,
        end_time=now + datetime.timedelta(hours=2),
        category=EventCategory.MILESTONE,
        target_person_ids=[p1.id],
    )

    export_res = api.data_portability.export_family_context_for_account(acc1.id, fc.id)
    assert "events" in export_res.records
    ev_records = export_res.records["events"]
    assert len(ev_records) == 1


def test_mayil_read_only_cluster9_integration():
    api, acc1, acc2, p1, p2, fc, s1, s2 = _setup_baseline_context()
    insights = api.mayil.generate_insights(acc1.id, fc.id)
    assert insights.id is not None
    # Confirm canonical repository count remains unchanged after read-only analysis
    assert len(api.canonical.list_action_proposals()) == 0


def test_vel_guardian_derived_dashboard_repair():
    api, acc1, acc2, p1, p2, fc, s1, s2 = _setup_baseline_context()
    now = datetime.datetime.utcnow()

    api.create_event_for_session(
        session_id=s1.session_id,
        title="Guardian Event",
        description="Audit target",
        family_context_id=fc.id,
        start_time=now,
        end_time=now + datetime.timedelta(hours=1),
    )

    api.dashboard.project_dashboard_entries(acc1.id, fc.id)
    # Clear derived dashboard entries to simulate desync
    api.derived.clear_dashboard_entries(fc.id)

    # Rebuild via Guardian derived repair
    prop = api.guardian._create_repair_proposal(
        "rebuild_derived_projections", "DashboardProjection", fc.id, fc.id, classification=RepairClassification.DERIVED_ONLY
    )

    executed = api.guardian.execute_repair_proposal(acc1.id, prop.id)
    assert executed.is_executed is True
    rebuilt = api.derived.get_dashboard_entries(fc.id)
    assert len(rebuilt) >= 1


def test_dashboard_reminder_privacy_semantics():
    api, acc1, acc2, p1, p2, fc, s1, s2 = _setup_baseline_context()
    now = datetime.datetime.utcnow()

    priv_event = api.create_event_for_session(
        session_id=s1.session_id,
        title="Private Doctor Visit",
        description="Confidential",
        family_context_id=fc.id,
        start_time=now,
        end_time=now + datetime.timedelta(hours=1),
        visibility=VisibilityLevel.PRIVATE,
    )
    rem_priv = api.reminder.create_reminder(
        created_by_id=acc1.id,
        event_id=priv_event.id,
        reminder_type=ReminderType.EVENT_START,
    )

    fam_event = api.create_event_for_session(
        session_id=s1.session_id,
        title="Family Dinner",
        description="Shared dinner",
        family_context_id=fc.id,
        start_time=now,
        end_time=now + datetime.timedelta(hours=2),
        visibility=VisibilityLevel.FAMILY,
    )
    rem_fam = api.reminder.create_reminder(
        created_by_id=acc1.id,
        event_id=fam_event.id,
        reminder_type=ReminderType.EVENT_START,
    )

    sum1 = api.dashboard.generate_dashboard_summary(acc1.id, fc.id)
    rem_ids_1 = [r.id for r in sum1.due_reminders]
    assert rem_priv.id in rem_ids_1
    assert rem_fam.id in rem_ids_1

    sum2 = api.dashboard.generate_dashboard_summary(acc2.id, fc.id)
    rem_ids_2 = [r.id for r in sum2.due_reminders]
    assert rem_priv.id not in rem_ids_2
    assert rem_fam.id in rem_ids_2
