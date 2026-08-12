import datetime

from ENGINEERING.source.femc.api import FEMCApi
from ENGINEERING.source.femc.models import VisibilityLevel


def test_create_family_context_and_event():
    api = FEMCApi()

    person = api.identity.create_person("Alice")
    account = api.identity.create_account("alice", "alice@example.com", person.id)
    context = api.identity.create_family_context("Test Family", member_ids=[account.id], created_by_id=account.id)
    event = api.event.create_event(
        owner_id=account.id,
        title="Birthday Dinner",
        description="Family dinner celebration",
        family_context_id=context.id,
        start_time=datetime.datetime(2026, 1, 1, 18, 0),
        end_time=datetime.datetime(2026, 1, 1, 20, 0),
        visibility=VisibilityLevel.FAMILY,
    )

    assert event.id in api.canonical.events
    assert event.provenance is not None
    calendar = api.calendar.get_calendar_for_context(account.id, context.id)
    assert len(calendar) == 1
    assert calendar[0].event_id == event.id


def test_memory_creation_and_search():
    api = FEMCApi()

    person = api.identity.create_person("Bob")
    account = api.identity.create_account("bob", "bob@example.com", person.id)
    context = api.identity.create_family_context("Public Family", member_ids=[account.id], created_by_id=account.id)
    memory = api.memory.create_memory(
        subject_id=account.id,
        narrative="A vivid recollection of the first outing.",
        visibility=VisibilityLevel.PUBLIC,
        created_by_id=account.id,
    )

    assert memory.id in api.canonical.memories
    results = api.search.search("outing")
    assert any(result.id == memory.id for result in results)


def test_authorization_denies_unauthorized_event_creation():
    api = FEMCApi()

    person = api.identity.create_person("Eve")
    account = api.identity.create_account("eve", "eve@example.com", person.id)
    other_person = api.identity.create_person("Mallory")
    other_account = api.identity.create_account("mallory", "mallory@example.com", other_person.id)
    context = api.identity.create_family_context("Private Family", member_ids=[other_account.id], created_by_id=other_account.id)

    try:
        api.event.create_event(
            owner_id=account.id,
            title="Unauthorized Gathering",
            description="This should fail.",
            family_context_id=context.id,
            start_time=datetime.datetime(2026, 2, 1, 10, 0),
            end_time=datetime.datetime(2026, 2, 1, 12, 0),
            visibility=VisibilityLevel.FAMILY,
        )
        assert False, "Expected PermissionError"
    except PermissionError:
        pass
