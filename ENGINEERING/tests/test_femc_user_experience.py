import datetime

from ENGINEERING.source.femc.api import FEMCApi
from ENGINEERING.source.femc.models import VisibilityLevel


def test_user_experience_end_to_end():
    api = FEMCApi()

    # Setup identity and family context
    person = api.identity.create_person("Alice")
    account = api.identity.create_account("alice", "alice@example.com", person.id)
    context = api.identity.create_family_context("Test Family", member_ids=[account.id], created_by_id=account.id)
    session = api.create_session(account.id)

    assert session.session_id in api.canonical.sessions
    assert session.account_id == account.id

    # Resolve family context from session
    resolved_context = api.resolve_family_context_for_session(session.session_id)
    assert resolved_context is not None
    assert resolved_context.id == context.id

    # Create event through session
    event = api.create_event_for_session(
        session.session_id,
        title="Birthday Dinner",
        description="Family dinner celebration",
        family_context_id=context.id,
        start_time=datetime.datetime(2026, 1, 1, 18, 0),
        end_time=datetime.datetime(2026, 1, 1, 20, 0),
        visibility=VisibilityLevel.FAMILY,
    )

    assert event.id in api.canonical.events
    assert event.provenance is not None

    # Calendar projection is visible to the same session
    calendar_entries = api.get_calendar_for_session(session.session_id, context.id)
    assert len(calendar_entries) == 1
    assert calendar_entries[0].event_id == event.id

    # Get event detail through session
    retrieved_event = api.get_event_for_session(session.session_id, event.id)
    assert retrieved_event.id == event.id

    # Attach memory to the event through session
    memory = api.create_memory_for_session(
        session.session_id,
        event.id,
        narrative="A vivid recollection of the first outing.",
        visibility=VisibilityLevel.FAMILY,
    )

    assert memory.id in api.canonical.memories
    assert memory.event_id == event.id
    assert memory.provenance is not None

    # Retrieve memory through session
    retrieved_memory = api.get_memory_for_session(session.session_id, memory.id)
    assert retrieved_memory.id == memory.id
    assert retrieved_memory.event_id == event.id

    # Search visible memory through session
    memory_results = api.search_for_session(session.session_id, "outing")
    assert any(result.id == memory.id for result in memory_results)

    # Search visible event through session
    event_results = api.search_for_session(session.session_id, "dinner")
    assert any(result.id == event.id for result in event_results)


def test_authorization_feedback_for_unauthorized_user():
    api = FEMCApi()

    person = api.identity.create_person("Alice")
    account = api.identity.create_account("alice", "alice@example.com", person.id)
    context = api.identity.create_family_context("Test Family", member_ids=[account.id], created_by_id=account.id)
    session = api.create_session(account.id)

    event = api.create_event_for_session(
        session.session_id,
        title="Family Meeting",
        description="Should only be visible to family members.",
        family_context_id=context.id,
        start_time=datetime.datetime(2026, 2, 1, 10, 0),
        end_time=datetime.datetime(2026, 2, 1, 12, 0),
        visibility=VisibilityLevel.FAMILY,
    )

    other_person = api.identity.create_person("Mallory")
    other_account = api.identity.create_account("mallory", "mallory@example.com", other_person.id)
    other_session = api.create_session(other_account.id)

    try:
        api.get_event_for_session(other_session.session_id, event.id)
        assert False, "Expected PermissionError"
    except PermissionError:
        pass

    try:
        api.create_memory_for_session(
            other_session.session_id,
            event.id,
            narrative="Unauthorized attempt.",
            visibility=VisibilityLevel.FAMILY,
        )
        assert False, "Expected PermissionError"
    except PermissionError:
        pass
