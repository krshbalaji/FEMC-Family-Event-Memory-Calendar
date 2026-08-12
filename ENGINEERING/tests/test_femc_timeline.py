import datetime
import pytest
from ENGINEERING.source.femc.api import FEMCApi
from ENGINEERING.source.femc.models import MediaType, TimelineItemType, VisibilityLevel


def test_timeline_aggregation_and_ordering():
    api = FEMCApi()

    person = api.identity.create_person("Family Historian")
    account = api.identity.create_account("historian", "historian@example.com", person.id)
    context = api.identity.create_family_context("Timeline Family", member_ids=[account.id], created_by_id=account.id)
    session = api.create_session(account.id)

    # 1. Place created at 09:00
    t_place = datetime.datetime(2026, 8, 1, 9, 0)
    place = api.create_place_for_session(
        session_id=session.session_id,
        name="Lakeside Cabin",
        address="100 Lake Drive",
        family_context_id=context.id,
    )
    place.created_at = t_place

    # 2. Event created at 10:00
    t_event = datetime.datetime(2026, 8, 1, 10, 0)
    event = api.create_event_for_session(
        session_id=session.session_id,
        title="Family Picnic",
        description="Annual picnic at lakeside cabin",
        family_context_id=context.id,
        start_time=t_event,
        end_time=None,
        place_id=place.id,
    )

    # 3. Memory recorded at 12:00
    t_memory = datetime.datetime(2026, 8, 1, 12, 0)
    memory = api.create_memory_for_session(
        session_id=session.session_id,
        event_id=event.id,
        narrative="Caught a huge fish off the dock",
    )
    memory.recorded_at = t_memory

    # 4. Media photo created at 14:00
    t_media = datetime.datetime(2026, 8, 1, 14, 0)
    photo = api.create_media_item_for_session(
        session_id=session.session_id,
        uri="https://storage.example.com/photos/big_fish.jpg",
        media_type=MediaType.PHOTO,
        caption="The big catch!",
        family_context_id=context.id,
        event_id=event.id,
        memory_id=memory.id,
    )
    photo.created_at = t_media

    # Get Timeline for session
    timeline = api.get_timeline_for_session(session.session_id, context.id)

    assert len(timeline) == 4

    # Verify reverse chronological ordering (newest first)
    types = [e.item_type for e in timeline]
    assert types == [
        TimelineItemType.MEDIA,
        TimelineItemType.MEMORY,
        TimelineItemType.EVENT,
        TimelineItemType.PLACE,
    ]

    # Verify ref_ids
    assert timeline[0].ref_id == photo.id
    assert timeline[1].ref_id == memory.id
    assert timeline[2].ref_id == event.id
    assert timeline[3].ref_id == place.id


def test_timeline_limit_parameter():
    api = FEMCApi()

    person = api.identity.create_person("Member")
    account = api.identity.create_account("member", "member@example.com", person.id)
    context = api.identity.create_family_context("Limit Family", member_ids=[account.id], created_by_id=account.id)
    session = api.create_session(account.id)

    for i in range(5):
        api.create_event_for_session(
            session_id=session.session_id,
            title=f"Event {i}",
            description=f"Description {i}",
            family_context_id=context.id,
            start_time=datetime.datetime(2026, 8, 1, 10 + i, 0),
            end_time=None,
        )

    timeline_limited = api.get_timeline_for_session(session.session_id, context.id, limit=2)
    assert len(timeline_limited) == 2
    assert timeline_limited[0].title == "Event 4"
    assert timeline_limited[1].title == "Event 3"


def test_timeline_unauthorized_access_blocked():
    api = FEMCApi()

    owner_person = api.identity.create_person("Owner")
    owner_account = api.identity.create_account("owner", "owner@example.com", owner_person.id)
    context = api.identity.create_family_context("Secret Family", member_ids=[owner_account.id], created_by_id=owner_account.id)
    owner_session = api.create_session(owner_account.id)

    api.create_event_for_session(
        session_id=owner_session.session_id,
        title="Secret Reunion",
        description="Private meeting",
        family_context_id=context.id,
        start_time=datetime.datetime(2026, 8, 1, 12, 0),
        end_time=None,
    )

    outsider_person = api.identity.create_person("Outsider")
    outsider_account = api.identity.create_account("outsider", "outsider@example.com", outsider_person.id)
    outsider_session = api.create_session(outsider_account.id)

    with pytest.raises(PermissionError):
        api.get_timeline_for_session(outsider_session.session_id, context.id)
