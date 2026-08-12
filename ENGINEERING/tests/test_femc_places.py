import datetime
import pytest
from ENGINEERING.source.femc.api import FEMCApi
from ENGINEERING.source.femc.models import VisibilityLevel


def test_place_creation_and_retrieval_for_session():
    api = FEMCApi()

    person = api.identity.create_person("Homeowner")
    account = api.identity.create_account("homeowner", "home@example.com", person.id)
    context = api.identity.create_family_context("Place Family", member_ids=[account.id], created_by_id=account.id)
    session = api.create_session(account.id)

    place = api.create_place_for_session(
        session_id=session.session_id,
        name="Grandma's House",
        address="123 Family Lane, Oakville",
        family_context_id=context.id,
        visibility=VisibilityLevel.FAMILY,
    )
    assert place.id is not None
    assert place.name == "Grandma's House"
    assert place.address == "123 Family Lane, Oakville"

    retrieved = api.get_place_for_session(session.session_id, place.id)
    assert retrieved.id == place.id
    assert retrieved.name == "Grandma's House"

    places_list = api.list_places_for_session(session.session_id, context.id)
    assert len(places_list) == 1
    assert places_list[0].id == place.id


def test_event_creation_with_attached_place():
    api = FEMCApi()

    person = api.identity.create_person("Organizer")
    account = api.identity.create_account("org_user", "org@example.com", person.id)
    context = api.identity.create_family_context("Reunion Family", member_ids=[account.id], created_by_id=account.id)
    session = api.create_session(account.id)

    place = api.create_place_for_session(
        session_id=session.session_id,
        name="Community Hall",
        address="456 Main St",
        family_context_id=context.id,
    )

    event = api.create_event_for_session(
        session_id=session.session_id,
        title="Annual Gathering",
        description="Reunion at community hall",
        family_context_id=context.id,
        start_time=datetime.datetime(2026, 7, 4, 12, 0),
        end_time=datetime.datetime(2026, 7, 4, 18, 0),
        place_id=place.id,
    )

    assert event.place_id == place.id

    fetched_event = api.get_event_for_session(session.session_id, event.id)
    assert fetched_event.place_id == place.id


def test_unauthorized_place_access_blocked():
    api = FEMCApi()

    owner_person = api.identity.create_person("Owner")
    owner_account = api.identity.create_account("owner", "owner@example.com", owner_person.id)
    context = api.identity.create_family_context("Owner Family", member_ids=[owner_account.id], created_by_id=owner_account.id)
    owner_session = api.create_session(owner_account.id)

    place = api.create_place_for_session(
        session_id=owner_session.session_id,
        name="Private Residence",
        address="Secret Location",
        family_context_id=context.id,
        visibility=VisibilityLevel.FAMILY,
    )

    outsider_person = api.identity.create_person("Outsider")
    outsider_account = api.identity.create_account("outsider", "outsider@example.com", outsider_person.id)
    outsider_session = api.create_session(outsider_account.id)

    with pytest.raises(PermissionError):
        api.get_place_for_session(outsider_session.session_id, place.id)

    with pytest.raises(PermissionError):
        api.list_places_for_session(outsider_session.session_id, context.id)
