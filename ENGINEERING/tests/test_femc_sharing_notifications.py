import datetime
import pytest
from ENGINEERING.source.femc.api import FEMCApi
from ENGINEERING.source.femc.models import (
    MediaType,
    NotificationStatus,
    NotificationType,
    ShareResourceType,
    VisibilityLevel,
)


def test_notification_creation_retrieval_and_status_update():
    api = FEMCApi()

    sender_person = api.identity.create_person("Sender")
    sender_account = api.identity.create_account("sender", "sender@example.com", sender_person.id)
    sender_session = api.create_session(sender_account.id)

    recipient_person = api.identity.create_person("Recipient")
    recipient_account = api.identity.create_account("recipient", "recipient@example.com", recipient_person.id)
    recipient_session = api.create_session(recipient_account.id)

    context = api.identity.create_family_context(
        "Notify Family", member_ids=[sender_account.id, recipient_account.id], created_by_id=sender_account.id
    )

    notif = api.create_notification_for_session(
        session_id=sender_session.session_id,
        recipient_id=recipient_account.id,
        notification_type=NotificationType.EVENT_INVITE,
        title="Family Reunion Invite",
        message="You are invited to the family reunion picnic!",
        family_context_id=context.id,
    )

    assert notif.id is not None
    assert notif.status == NotificationStatus.UNREAD
    assert notif.provenance is not None

    # Recipient lists notifications
    recip_notifs = api.list_notifications_for_session(recipient_session.session_id)
    assert len(recip_notifs) == 1
    assert recip_notifs[0].id == notif.id

    # Recipient marks notification read
    updated_notif = api.mark_notification_read_for_session(recipient_session.session_id, notif.id)
    assert updated_notif.status == NotificationStatus.READ


def test_notification_authorization_boundary():
    api = FEMCApi()

    sender_person = api.identity.create_person("Alice")
    sender_account = api.identity.create_account("alice", "alice@example.com", sender_person.id)
    sender_session = api.create_session(sender_account.id)

    recipient_person = api.identity.create_person("Bob")
    recipient_account = api.identity.create_account("bob", "bob@example.com", recipient_person.id)

    outsider_person = api.identity.create_person("Eve")
    outsider_account = api.identity.create_account("eve", "eve@example.com", outsider_person.id)
    outsider_session = api.create_session(outsider_account.id)

    notif = api.create_notification_for_session(
        session_id=sender_session.session_id,
        recipient_id=recipient_account.id,
        notification_type=NotificationType.SYSTEM_ALERT,
        title="Private Alert",
        message="Confidential message for Bob",
    )

    # Eve tries to read Bob's notification
    with pytest.raises(PermissionError):
        api.get_notification_for_session(outsider_session.session_id, notif.id)

    # Sender tries to read Bob's notification (must also fail as only recipient can view)
    with pytest.raises(PermissionError):
        api.get_notification_for_session(sender_session.session_id, notif.id)


def test_share_all_resource_types_and_valid_resolution():
    api = FEMCApi()

    person = api.identity.create_person("Sharer")
    account = api.identity.create_account("sharer", "sharer@example.com", person.id)
    context = api.identity.create_family_context("Share Family", member_ids=[account.id], created_by_id=account.id)
    session = api.create_session(account.id)

    # 1. Event
    event = api.create_event_for_session(
        session_id=session.session_id,
        title="Public Picnic",
        description="Open picnic",
        family_context_id=context.id,
        start_time=datetime.datetime(2026, 9, 1, 10, 0),
        end_time=None,
        visibility=VisibilityLevel.FAMILY,
    )
    event_link = api.create_share_link_for_session(session.session_id, ShareResourceType.EVENT, event.id)
    res_event = api.resolve_share_token(event_link.token)
    assert res_event.id == event.id

    # 2. Memory
    memory = api.create_memory_for_session(session.session_id, event.id, "A great day!")
    memory_link = api.create_share_link_for_session(session.session_id, ShareResourceType.MEMORY, memory.id)
    res_memory = api.resolve_share_token(memory_link.token)
    assert res_memory.id == memory.id

    # 3. MediaItem
    photo = api.create_media_item_for_session(
        session.session_id, "https://example.com/photo.jpg", MediaType.PHOTO, "Photo", family_context_id=context.id
    )
    photo_link = api.create_share_link_for_session(session.session_id, ShareResourceType.MEDIA_ITEM, photo.id)
    res_photo = api.resolve_share_token(photo_link.token)
    assert res_photo.id == photo.id

    # 4. MediaAlbum
    album = api.create_media_album_for_session(session.session_id, "Picnic Album", family_context_id=context.id)
    album_link = api.create_share_link_for_session(session.session_id, ShareResourceType.MEDIA_ALBUM, album.id)
    res_album = api.resolve_share_token(album_link.token)
    assert res_album.id == album.id


def test_share_expiry_and_revocation():
    api = FEMCApi()

    person = api.identity.create_person("Owner")
    account = api.identity.create_account("owner_share", "owner_s@example.com", person.id)
    context = api.identity.create_family_context("Revoke Family", member_ids=[account.id], created_by_id=account.id)
    session = api.create_session(account.id)

    event = api.create_event_for_session(
        session_id=session.session_id,
        title="Temporary Share Event",
        description="Will expire or revoke",
        family_context_id=context.id,
        start_time=datetime.datetime(2026, 9, 1, 10, 0),
        end_time=None,
        visibility=VisibilityLevel.FAMILY,
    )

    # 1. Test Revocation
    revokable_link = api.create_share_link_for_session(
        session_id=session.session_id,
        resource_type=ShareResourceType.EVENT,
        resource_id=event.id,
        family_context_id=context.id,
    )

    api.revoke_share_link_for_session(session.session_id, revokable_link.token)

    with pytest.raises(PermissionError):
        api.resolve_share_token(revokable_link.token)

    # 2. Test Expiry
    expired_link = api.create_share_link_for_session(
        session_id=session.session_id,
        resource_type=ShareResourceType.EVENT,
        resource_id=event.id,
        family_context_id=context.id,
        expires_in_minutes=10,
    )
    # Manually simulate expired time
    expired_link.expires_at = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)

    with pytest.raises(PermissionError):
        api.resolve_share_token(expired_link.token)

    # 3. Test Unknown / Malformed Token
    with pytest.raises(ValueError):
        api.resolve_share_token("invalid_malformed_token_123")


def test_private_resource_sharing_protection_all_types():
    api = FEMCApi()

    person = api.identity.create_person("Secret Keeper")
    account = api.identity.create_account("secret_keeper", "keeper@example.com", person.id)
    context = api.identity.create_family_context("Vault Family", member_ids=[account.id], created_by_id=account.id)
    session = api.create_session(account.id)

    # Private Event
    priv_event = api.create_event_for_session(
        session.session_id,
        "Private Event",
        "Secret",
        context.id,
        datetime.datetime(2026, 9, 1, 10, 0),
        None,
        visibility=VisibilityLevel.PRIVATE,
    )
    with pytest.raises(PermissionError):
        api.create_share_link_for_session(session.session_id, ShareResourceType.EVENT, priv_event.id)

    # Private Memory
    priv_memory = api.create_memory_for_session(session.session_id, priv_event.id, "Private note", VisibilityLevel.PRIVATE)
    with pytest.raises(PermissionError):
        api.create_share_link_for_session(session.session_id, ShareResourceType.MEMORY, priv_memory.id)

    # Private MediaItem
    priv_media = api.create_media_item_for_session(
        session.session_id, "https://example.com/priv.jpg", MediaType.PHOTO, "Private", context.id, visibility=VisibilityLevel.PRIVATE
    )
    with pytest.raises(PermissionError):
        api.create_share_link_for_session(session.session_id, ShareResourceType.MEDIA_ITEM, priv_media.id)

    # Private MediaAlbum
    priv_album = api.create_media_album_for_session(
        session.session_id, "Private Album", "Vault", context.id, visibility=VisibilityLevel.PRIVATE
    )
    with pytest.raises(PermissionError):
        api.create_share_link_for_session(session.session_id, ShareResourceType.MEDIA_ALBUM, priv_album.id)
