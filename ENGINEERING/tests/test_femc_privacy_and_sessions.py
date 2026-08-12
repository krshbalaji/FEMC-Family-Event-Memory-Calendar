import datetime

from ENGINEERING.source.femc.api import FEMCApi
from ENGINEERING.source.femc.models import VisibilityLevel


def test_private_event_calendar_visibility():
    api = FEMCApi()

    person = api.identity.create_person("Owner")
    account = api.identity.create_account("owner", "owner@example.com", person.id)
    context = api.identity.create_family_context("Private Family", member_ids=[account.id], created_by_id=account.id)
    session = api.create_session(account.id)

    event = api.create_event_for_session(
        session.session_id,
        title="Private Meeting",
        description="Owner only event.",
        family_context_id=context.id,
        start_time=datetime.datetime(2026, 3, 1, 10, 0),
        end_time=datetime.datetime(2026, 3, 1, 11, 0),
        visibility=VisibilityLevel.PRIVATE,
    )

    calendar = api.get_calendar_for_session(session.session_id, context.id)
    assert len(calendar) == 1
    assert calendar[0].event_id == event.id

    other_person = api.identity.create_person("Member")
    other_account = api.identity.create_account("member", "member@example.com", other_person.id)
    api.identity.add_member_to_context(context.id, other_account.id)
    other_session = api.create_session(other_account.id)

    calendar_for_other = api.get_calendar_for_session(other_session.session_id, context.id)
    assert all(entry.event_id != event.id for entry in calendar_for_other)

    try:
        api.get_event_for_session(other_session.session_id, event.id)
        assert False, "Expected PermissionError"
    except PermissionError:
        pass


def test_event_with_memory_privacy_for_family_member():
    api = FEMCApi()

    owner_person = api.identity.create_person("Owner")
    owner_account = api.identity.create_account("owner", "owner@example.com", owner_person.id)
    context = api.identity.create_family_context("Private Family", member_ids=[owner_account.id], created_by_id=owner_account.id)
    owner_session = api.create_session(owner_account.id)

    event = api.create_event_for_session(
        owner_session.session_id,
        title="Shared Event",
        description="Family-wide event.",
        family_context_id=context.id,
        start_time=datetime.datetime(2026, 3, 1, 10, 0),
        end_time=datetime.datetime(2026, 3, 1, 11, 0),
        visibility=VisibilityLevel.FAMILY,
    )

    private_memory = api.create_memory_for_session(
        owner_session.session_id,
        event.id,
        narrative="Owner-only memory.",
        visibility=VisibilityLevel.PRIVATE,
    )

    member_person = api.identity.create_person("Member")
    member_account = api.identity.create_account("member", "member@example.com", member_person.id)
    api.identity.add_member_to_context(context.id, member_account.id)
    member_session = api.create_session(member_account.id)

    event_with_memories = api.get_event_with_memories_for_session(member_session.session_id, event.id)
    assert event_with_memories.event.id == event.id
    assert len(event_with_memories.memories) == 0

    discovery = api.discover_context_for_session(member_session.session_id, context.id)
    assert discovery.context.id == context.id
    assert len(discovery.calendar_entries) == 1
    assert discovery.calendar_entries[0].event_id == event.id
    assert len(discovery.memories) == 0


def test_unauthorized_event_memory_access_is_blocked():
    api = FEMCApi()

    owner_person = api.identity.create_person("Owner")
    owner_account = api.identity.create_account("owner", "owner@example.com", owner_person.id)
    context = api.identity.create_family_context("Test Family", member_ids=[owner_account.id], created_by_id=owner_account.id)
    owner_session = api.create_session(owner_account.id)

    event = api.create_event_for_session(
        owner_session.session_id,
        title="Private Event",
        description="Accessible only to family members.",
        family_context_id=context.id,
        start_time=datetime.datetime(2026, 4, 1, 10, 0),
        end_time=datetime.datetime(2026, 4, 1, 11, 0),
        visibility=VisibilityLevel.FAMILY,
    )

    api.create_memory_for_session(
        owner_session.session_id,
        event.id,
        narrative="A family memory.",
        visibility=VisibilityLevel.FAMILY,
    )

    outsider_person = api.identity.create_person("Outsider")
    outsider_account = api.identity.create_account("outsider", "outsider@example.com", outsider_person.id)
    outsider_session = api.create_session(outsider_account.id)

    try:
        api.get_event_with_memories_for_session(outsider_session.session_id, event.id)
        assert False, "Expected PermissionError"
    except PermissionError:
        pass


def test_expired_session_rejected():
    api = FEMCApi()

    person = api.identity.create_person("Expired")
    account = api.identity.create_account("expired", "expired@example.com", person.id)
    session = api.create_session(account.id, duration_minutes=-1)

    try:
        api.resolve_family_context_for_session(session.session_id)
        assert False, "Expected PermissionError"
    except PermissionError:
        pass

    try:
        api.get_calendar_for_session(session.session_id, "none")
        assert False, "Expected PermissionError"
    except PermissionError:
        pass
