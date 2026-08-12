from __future__ import annotations

import datetime
import pytest

from ENGINEERING.source.femc.api import FEMCApi
from ENGINEERING.source.femc.models import (
    Account,
    EventStatus,
    Person,
    RecurrenceFrequency,
    RecurrenceRule,
    ReminderStatus,
    ReminderType,
    VisibilityLevel,
)



def _setup_context_and_sessions(api: FEMCApi):
    p1 = api.canonical.add_person(Person(name="Alice Member"))
    a1 = api.canonical.add_account(Account(username="alice", email="alice@family.org", person_id=p1.id))
    s1 = api.create_session(a1.id)

    p2 = api.canonical.add_person(Person(name="Bob Member"))
    a2 = api.canonical.add_account(Account(username="bob", email="bob@family.org", person_id=p2.id))
    s2 = api.create_session(a2.id)

    p3 = api.canonical.add_person(Person(name="Stranger"))
    a3 = api.canonical.add_account(Account(username="stranger", email="stranger@other.org", person_id=p3.id))
    s3 = api.create_session(a3.id)

    context = api.identity.create_family_context("Smith Family", [a1.id, a2.id], created_by_id=a1.id)
    return a1, s1, a2, s2, a3, s3, context


def test_daily_recurrence_and_calendar_expansion():
    api = FEMCApi()
    a1, s1, a2, s2, a3, s3, fc = _setup_context_and_sessions(api)

    start_dt = datetime.datetime(2026, 9, 1, 10, 0)
    rule = RecurrenceRule(frequency=RecurrenceFrequency.DAILY, interval=2)
    ev = api.create_event_for_session(
        session_id=s1.session_id,
        title="Daily Workout",
        description="Every 2 days",
        family_context_id=fc.id,
        start_time=start_dt,
        end_time=None,
        recurrence_rule=rule,
    )

    # Query calendar for first week of September
    cal = api.get_calendar_for_session(
        session_id=s1.session_id,
        family_context_id=fc.id,
        start_date=datetime.date(2026, 9, 1),
        end_date=datetime.date(2026, 9, 7),
    )
    dates = [entry.date for entry in cal if entry.event_id == ev.id]
    assert dates == [
        datetime.date(2026, 9, 1),
        datetime.date(2026, 9, 3),
        datetime.date(2026, 9, 5),
        datetime.date(2026, 9, 7),
    ]


def test_weekly_recurrence():
    api = FEMCApi()
    a1, s1, a2, s2, a3, s3, fc = _setup_context_and_sessions(api)

    start_dt = datetime.datetime(2026, 9, 6, 14, 0) # Sunday
    rule = RecurrenceRule(frequency=RecurrenceFrequency.WEEKLY, interval=1)
    ev = api.create_event_for_session(
        session_id=s1.session_id,
        title="Weekly Sync",
        description="Every Sunday",
        family_context_id=fc.id,
        start_time=start_dt,
        end_time=None,
        recurrence_rule=rule,
    )

    cal = api.get_calendar_for_session(
        session_id=s1.session_id,
        family_context_id=fc.id,
        start_date=datetime.date(2026, 9, 1),
        end_date=datetime.date(2026, 9, 30),
    )
    dates = [entry.date for entry in cal if entry.event_id == ev.id]
    assert dates == [
        datetime.date(2026, 9, 6),
        datetime.date(2026, 9, 13),
        datetime.date(2026, 9, 20),
        datetime.date(2026, 9, 27),
    ]


def test_monthly_recurrence():
    api = FEMCApi()
    a1, s1, a2, s2, a3, s3, fc = _setup_context_and_sessions(api)

    start_dt = datetime.datetime(2026, 1, 15, 9, 0)
    rule = RecurrenceRule(frequency=RecurrenceFrequency.MONTHLY, interval=1)
    ev = api.create_event_for_session(
        session_id=s1.session_id,
        title="Monthly Review",
        description="15th of each month",
        family_context_id=fc.id,
        start_time=start_dt,
        end_time=None,
        recurrence_rule=rule,
    )

    cal = api.get_calendar_for_session(
        session_id=s1.session_id,
        family_context_id=fc.id,
        start_date=datetime.date(2026, 1, 1),
        end_date=datetime.date(2026, 4, 30),
    )
    dates = [entry.date for entry in cal if entry.event_id == ev.id]
    assert dates == [
        datetime.date(2026, 1, 15),
        datetime.date(2026, 2, 15),
        datetime.date(2026, 3, 15),
        datetime.date(2026, 4, 15),
    ]


def test_yearly_recurrence():
    api = FEMCApi()
    a1, s1, a2, s2, a3, s3, fc = _setup_context_and_sessions(api)

    start_dt = datetime.datetime(2020, 10, 25, 0, 0)
    rule = RecurrenceRule(frequency=RecurrenceFrequency.YEARLY, interval=1)
    ev = api.create_event_for_session(
        session_id=s1.session_id,
        title="Anniversary",
        description="Oct 25 every year",
        family_context_id=fc.id,
        start_time=start_dt,
        end_time=None,
        recurrence_rule=rule,
    )

    cal = api.get_calendar_for_session(
        session_id=s1.session_id,
        family_context_id=fc.id,
        start_date=datetime.date(2024, 1, 1),
        end_date=datetime.date(2027, 12, 31),
    )
    dates = [entry.date for entry in cal if entry.event_id == ev.id]
    assert dates == [
        datetime.date(2024, 10, 25),
        datetime.date(2025, 10, 25),
        datetime.date(2026, 10, 25),
        datetime.date(2027, 10, 25),
    ]


def test_until_date_boundary():
    api = FEMCApi()
    a1, s1, a2, s2, a3, s3, fc = _setup_context_and_sessions(api)

    start_dt = datetime.datetime(2026, 9, 1, 10, 0)
    until = datetime.date(2026, 9, 5)
    rule = RecurrenceRule(frequency=RecurrenceFrequency.DAILY, interval=1, until_date=until)
    ev = api.create_event_for_session(
        session_id=s1.session_id,
        title="Short Course",
        description="Daily until Sept 5",
        family_context_id=fc.id,
        start_time=start_dt,
        end_time=None,
        recurrence_rule=rule,
    )

    cal = api.get_calendar_for_session(
        session_id=s1.session_id,
        family_context_id=fc.id,
        start_date=datetime.date(2026, 9, 1),
        end_date=datetime.date(2026, 9, 10),
    )
    dates = [entry.date for entry in cal if entry.event_id == ev.id]
    assert dates == [
        datetime.date(2026, 9, 1),
        datetime.date(2026, 9, 2),
        datetime.date(2026, 9, 3),
        datetime.date(2026, 9, 4),
        datetime.date(2026, 9, 5),
    ]


def test_reminder_configuration_due_trigger_and_duplicate_prevention():
    api = FEMCApi()
    a1, s1, a2, s2, a3, s3, fc = _setup_context_and_sessions(api)

    start_dt = datetime.datetime(2026, 9, 1, 12, 0) # Event at 12:00
    ev = api.create_event_for_session(
        session_id=s1.session_id,
        title="Doctor Appointment",
        description="Routine checkup",
        family_context_id=fc.id,
        start_time=start_dt,
        end_time=None,
    )

    # Configure reminder 30 mins before
    reminder = api.configure_reminder_for_session(
        session_id=s1.session_id,
        event_id=ev.id,
        offset_minutes=30,
        reminder_type=ReminderType.EVENT_START,
    )
    assert reminder.status == ReminderStatus.PENDING
    assert reminder.event_id == ev.id
    assert reminder.provenance is not None

    reminders = api.list_reminders_for_event_for_session(s1.session_id, ev.id)
    assert len(reminders) == 1

    # Time before trigger (11:20 AM - 40 mins before start)
    notifs = api.trigger_due_reminders_for_session(
        session_id=s1.session_id,
        family_context_id=fc.id,
        current_time=datetime.datetime(2026, 9, 1, 11, 20),
    )
    assert len(notifs) == 0

    # Time at trigger (11:30 AM - exactly 30 mins before start)
    notifs = api.trigger_due_reminders_for_session(
        session_id=s1.session_id,
        family_context_id=fc.id,
        current_time=datetime.datetime(2026, 9, 1, 11, 30),
    )
    assert len(notifs) == 1
    assert notifs[0].title == "Reminder: Doctor Appointment"
    assert notifs[0].recipient_id == a1.id

    # Verify reminder status mutated to TRIGGERED
    rem = api.canonical.get_reminder(reminder.id)
    assert rem.status == ReminderStatus.TRIGGERED
    assert rem.last_triggered_at == datetime.datetime(2026, 9, 1, 11, 30)

    # Re-evaluate at 11:35 AM -> duplicate prevention: no new notifications!
    notifs2 = api.trigger_due_reminders_for_session(
        session_id=s1.session_id,
        family_context_id=fc.id,
        current_time=datetime.datetime(2026, 9, 1, 11, 35),
    )
    assert len(notifs2) == 0


def test_unauthorized_reminder_access_and_private_event_protection():
    api = FEMCApi()
    a1, s1, a2, s2, a3, s3, fc = _setup_context_and_sessions(api)

    # Private event owned by Alice
    priv_ev = api.create_event_for_session(
        session_id=s1.session_id,
        title="Alice Secret Event",
        description="Private notes",
        family_context_id=fc.id,
        start_time=datetime.datetime(2026, 9, 1, 10, 0),
        end_time=None,
        visibility=VisibilityLevel.PRIVATE,
    )

    # Stranger cannot configure reminder
    with pytest.raises(PermissionError):
        api.configure_reminder_for_session(
            session_id=s3.session_id,
            event_id=priv_ev.id,
            offset_minutes=15,
        )

    # Family member Bob cannot view or configure reminder for Alice's PRIVATE event
    with pytest.raises(PermissionError):
        api.configure_reminder_for_session(
            session_id=s2.session_id,
            event_id=priv_ev.id,
            offset_minutes=15,
        )

    with pytest.raises(PermissionError):
        api.list_reminders_for_event_for_session(s2.session_id, priv_ev.id)


def test_data_portability_exports_recurrence_and_reminders():
    api = FEMCApi()
    a1, s1, a2, s2, a3, s3, fc = _setup_context_and_sessions(api)

    rule = RecurrenceRule(frequency=RecurrenceFrequency.WEEKLY, interval=1)
    ev = api.create_event_for_session(
        session_id=s1.session_id,
        title="Weekly Dinner",
        description="Family Sunday dinner",
        family_context_id=fc.id,
        start_time=datetime.datetime(2026, 9, 6, 18, 0),
        end_time=None,
        recurrence_rule=rule,
    )

    rem = api.configure_reminder_for_session(
        session_id=s1.session_id,
        event_id=ev.id,
        offset_minutes=60,
    )

    export = api.data_portability.export_family_context_for_account(
        account_id=a1.id,
        family_context_id=fc.id,
    )

    assert export.family_context_id == fc.id
    assert "events" in export.records
    events_export = export.records["events"]

    assert len(events_export) == 1
    assert events_export[0]["recurrence_rule"] == {
        "frequency": "weekly",
        "interval": 1,
        "until_date": None,
    }

    reminders_export = export.records["reminders"]
    assert len(reminders_export) == 1
    assert reminders_export[0]["id"] == rem.id
    assert reminders_export[0]["offset_minutes"] == 60


def test_vel_guardian_audits_invalid_recurrence_and_dangling_reminders():
    api = FEMCApi()
    a1, s1, a2, s2, a3, s3, fc = _setup_context_and_sessions(api)

    # Valid event
    ev = api.create_event_for_session(
        session_id=s1.session_id,
        title="Good Event",
        description="Normal",
        family_context_id=fc.id,
        start_time=datetime.datetime(2026, 9, 1, 10, 0),
        end_time=None,
    )


    # Manually inject invalid recurrence rule (interval=0)
    ev.recurrence_rule = RecurrenceRule(frequency=RecurrenceFrequency.DAILY, interval=0)

    # Manually inject dangling reminder
    from ENGINEERING.source.femc.models import ReminderConfig

    dangling_rem = ReminderConfig(
        event_id="non-existent-event-id",
        family_context_id=fc.id,
        offset_minutes=15,
        created_by_id=a1.id,
    )
    api.canonical.add_reminder(dangling_rem)

    report = api.guardian.run_integrity_audit(a1.id, fc.id)
    assert not report.is_valid

    anomaly_descriptions = [a.description for a in report.anomalies]
    assert any("has invalid recurrence rule" in desc for desc in anomaly_descriptions)
    assert any("references non-existent event_id" in desc for desc in anomaly_descriptions)


def test_month_end_recurrence_clamping_and_restoration():
    api = FEMCApi()
    a1, s1, a2, s2, a3, s3, fc = _setup_context_and_sessions(api)

    # Event on Jan 31st
    start_dt = datetime.datetime(2026, 1, 31, 10, 0)
    rule = RecurrenceRule(frequency=RecurrenceFrequency.MONTHLY, interval=1)
    ev = api.create_event_for_session(
        session_id=s1.session_id,
        title="Jan 31st Event",
        description="Clamps on Feb/Apr, restores on Mar/May",
        family_context_id=fc.id,
        start_time=start_dt,
        end_time=None,
        recurrence_rule=rule,
    )

    cal = api.get_calendar_for_session(
        session_id=s1.session_id,
        family_context_id=fc.id,
        start_date=datetime.date(2026, 1, 1),
        end_date=datetime.date(2026, 5, 31),
    )
    dates = [entry.date for entry in cal if entry.event_id == ev.id]
    assert dates == [
        datetime.date(2026, 1, 31),
        datetime.date(2026, 2, 28), # Clamped for Feb
        datetime.date(2026, 3, 31), # Restored for March!
        datetime.date(2026, 4, 30), # Clamped for April
        datetime.date(2026, 5, 31), # Restored for May!
    ]

