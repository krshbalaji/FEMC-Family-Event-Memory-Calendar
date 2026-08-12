import datetime
import pytest
from ENGINEERING.source.femc.api import FEMCApi
from ENGINEERING.source.femc.models import EventStatus, VisibilityLevel


def test_calendar_date_range_filtering():
    api = FEMCApi()

    person = api.identity.create_person("Calendar User")
    account = api.identity.create_account("cal_user", "cal@example.com", person.id)
    context = api.identity.create_family_context("Range Family", member_ids=[account.id], created_by_id=account.id)
    session = api.create_session(account.id)

    # Create event in March 2026
    event_march = api.create_event_for_session(
        session.session_id,
        title="March Birthday Party",
        description="Celebrating in March",
        family_context_id=context.id,
        start_time=datetime.datetime(2026, 3, 15, 14, 0),
        end_time=datetime.datetime(2026, 3, 15, 17, 0),
    )

    # Create event in April 2026
    event_april = api.create_event_for_session(
        session.session_id,
        title="April Picnic",
        description="Spring picnic in April",
        family_context_id=context.id,
        start_time=datetime.datetime(2026, 4, 10, 11, 0),
        end_time=datetime.datetime(2026, 4, 10, 15, 0),
    )

    # Query full calendar
    full_cal = api.get_calendar_for_session(session.session_id, context.id)
    assert len(full_cal) == 2

    # Query March only (2026-03-01 to 2026-03-31)
    march_cal = api.get_calendar_for_session(
        session.session_id,
        context.id,
        start_date=datetime.date(2026, 3, 1),
        end_date=datetime.date(2026, 3, 31),
    )
    assert len(march_cal) == 1
    assert march_cal[0].event_id == event_march.id

    # Query April only (2026-04-01 to 2026-04-30)
    april_cal = api.get_calendar_for_session(
        session.session_id,
        context.id,
        start_date=datetime.date(2026, 4, 1),
        end_date=datetime.date(2026, 4, 30),
    )
    assert len(april_cal) == 1
    assert april_cal[0].event_id == event_april.id


def test_event_status_transition_and_projection_sync():
    api = FEMCApi()

    person = api.identity.create_person("Organizer")
    account = api.identity.create_account("organizer", "org@example.com", person.id)
    context = api.identity.create_family_context("Event Family", member_ids=[account.id], created_by_id=account.id)
    session = api.create_session(account.id)

    event = api.create_event_for_session(
        session.session_id,
        title="Family Reunion",
        description="Annual reunion",
        family_context_id=context.id,
        start_time=datetime.datetime(2026, 5, 1, 10, 0),
        end_time=None,
    )
    assert event.status == EventStatus.PLANNED

    cal_entries = api.get_calendar_for_session(session.session_id, context.id)
    assert len(cal_entries) == 1
    assert cal_entries[0].status == EventStatus.PLANNED

    # Transition to CONFIRMED
    updated_event = api.update_event_status_for_session(session.session_id, event.id, EventStatus.CONFIRMED)
    assert updated_event.status == EventStatus.CONFIRMED

    cal_entries = api.get_calendar_for_session(session.session_id, context.id)
    assert len(cal_entries) == 1
    assert cal_entries[0].status == EventStatus.CONFIRMED

    # Transition to CANCELLED
    updated_event = api.update_event_status_for_session(session.session_id, event.id, EventStatus.CANCELLED)
    assert updated_event.status == EventStatus.CANCELLED

    cal_entries = api.get_calendar_for_session(session.session_id, context.id)
    assert len(cal_entries) == 1
    assert cal_entries[0].status == EventStatus.CANCELLED


def test_unauthorized_status_transition_blocked():
    api = FEMCApi()

    owner_person = api.identity.create_person("Owner")
    owner_account = api.identity.create_account("owner", "owner@example.com", owner_person.id)
    context = api.identity.create_family_context("Owner Family", member_ids=[owner_account.id], created_by_id=owner_account.id)
    owner_session = api.create_session(owner_account.id)

    event = api.create_event_for_session(
        owner_session.session_id,
        title="Private Planning",
        description="Family event",
        family_context_id=context.id,
        start_time=datetime.datetime(2026, 6, 1, 10, 0),
        end_time=None,
        visibility=VisibilityLevel.FAMILY,
    )

    outsider_person = api.identity.create_person("Outsider")
    outsider_account = api.identity.create_account("outsider", "outsider@example.com", outsider_person.id)
    outsider_session = api.create_session(outsider_account.id)

    with pytest.raises(PermissionError):
        api.update_event_status_for_session(outsider_session.session_id, event.id, EventStatus.CONFIRMED)
