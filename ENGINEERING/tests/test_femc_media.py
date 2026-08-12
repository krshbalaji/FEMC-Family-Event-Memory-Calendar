import datetime
import pytest
from ENGINEERING.source.femc.api import FEMCApi
from ENGINEERING.source.femc.models import MediaType, VisibilityLevel


def test_media_item_creation_and_event_memory_attachment():
    api = FEMCApi()

    person = api.identity.create_person("Photographer")
    account = api.identity.create_account("photo_user", "photo@example.com", person.id)
    context = api.identity.create_family_context("Media Family", member_ids=[account.id], created_by_id=account.id)
    session = api.create_session(account.id)

    event = api.create_event_for_session(
        session.session_id,
        title="Graduation Ceremony",
        description="Graduation day",
        family_context_id=context.id,
        start_time=datetime.datetime(2026, 6, 15, 10, 0),
        end_time=None,
    )

    memory = api.create_memory_for_session(
        session.session_id,
        event.id,
        narrative="Receiving the diploma",
    )

    # Attach photo to Event
    event_photo = api.create_media_item_for_session(
        session_id=session.session_id,
        uri="https://storage.example.com/photos/grad_stage.jpg",
        media_type=MediaType.PHOTO,
        caption="On stage with diploma",
        family_context_id=context.id,
        event_id=event.id,
    )
    assert event_photo.id is not None
    assert event_photo.event_id == event.id

    # Attach photo to Memory
    memory_photo = api.create_media_item_for_session(
        session_id=session.session_id,
        uri="https://storage.example.com/photos/grad_portrait.jpg",
        media_type=MediaType.PHOTO,
        caption="Portrait with family",
        family_context_id=context.id,
        memory_id=memory.id,
    )
    assert memory_photo.id is not None
    assert memory_photo.memory_id == memory.id

    # List media items by Event
    event_media = api.list_media_items_for_event_for_session(session.session_id, event.id)
    assert len(event_media) == 1
    assert event_media[0].id == event_photo.id

    # List media items by Memory
    memory_media = api.list_media_items_for_memory_for_session(session.session_id, memory.id)
    assert len(memory_media) == 1
    assert memory_media[0].id == memory_photo.id


def test_media_album_creation_and_grouping():
    api = FEMCApi()

    person = api.identity.create_person("Curator")
    account = api.identity.create_account("curator", "curator@example.com", person.id)
    context = api.identity.create_family_context("Album Family", member_ids=[account.id], created_by_id=account.id)
    session = api.create_session(account.id)

    photo1 = api.create_media_item_for_session(
        session.session_id,
        uri="https://storage.example.com/photos/vacation1.jpg",
        media_type=MediaType.PHOTO,
        caption="Beach sunrise",
        family_context_id=context.id,
    )
    photo2 = api.create_media_item_for_session(
        session.session_id,
        uri="https://storage.example.com/photos/vacation2.jpg",
        media_type=MediaType.PHOTO,
        caption="Mountain sunset",
        family_context_id=context.id,
    )

    album = api.create_media_album_for_session(
        session_id=session.session_id,
        title="Summer Vacation 2026",
        description="Highlights of our summer trip",
        family_context_id=context.id,
        media_ids=[photo1.id],
    )
    assert album.id is not None
    assert len(album.media_ids) == 1
    assert album.media_ids[0] == photo1.id

    # Add second photo to album
    updated_album = api.add_media_to_album_for_session(session.session_id, album.id, photo2.id)
    assert len(updated_album.media_ids) == 2
    assert photo2.id in updated_album.media_ids

    fetched_album = api.get_media_album_for_session(session.session_id, album.id)
    assert fetched_album.title == "Summer Vacation 2026"
    assert len(fetched_album.media_ids) == 2


def test_unauthorized_media_access_blocked():
    api = FEMCApi()

    owner_person = api.identity.create_person("Owner")
    owner_account = api.identity.create_account("owner", "owner@example.com", owner_person.id)
    context = api.identity.create_family_context("Private Media Family", member_ids=[owner_account.id], created_by_id=owner_account.id)
    owner_session = api.create_session(owner_account.id)

    photo = api.create_media_item_for_session(
        session_id=owner_session.session_id,
        uri="https://storage.example.com/photos/private.jpg",
        caption="Private photo",
        family_context_id=context.id,
        visibility=VisibilityLevel.FAMILY,
    )

    album = api.create_media_album_for_session(
        session_id=owner_session.session_id,
        title="Private Album",
        family_context_id=context.id,
        visibility=VisibilityLevel.FAMILY,
    )

    outsider_person = api.identity.create_person("Outsider")
    outsider_account = api.identity.create_account("outsider", "outsider@example.com", outsider_person.id)
    outsider_session = api.create_session(outsider_account.id)

    with pytest.raises(PermissionError):
        api.get_media_item_for_session(outsider_session.session_id, photo.id)

    with pytest.raises(PermissionError):
        api.get_media_album_for_session(outsider_session.session_id, album.id)

    with pytest.raises(PermissionError):
        api.add_media_to_album_for_session(outsider_session.session_id, album.id, photo.id)
