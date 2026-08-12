from __future__ import annotations

import datetime
from typing import List, Optional

from .models import (
    Confidence,
    ContextDiscoveryResult,
    Event,
    EventStatus,
    EventWithMemories,
    FamilyTopologyResult,
    MediaAlbum,
    MediaItem,
    MediaType,
    Memory,
    Notification,
    NotificationStatus,
    NotificationType,
    Place,
    Relationship,
    RelationshipType,
    ShareLink,
    ShareResourceType,
    TimelineItemType,
    TimelineProjectionEntry,
    VisibilityLevel,
)


from .repositories import CanonicalRepository, DerivedRepository
from .services import (
    AuthorizationService,
    CalendarService,
    EventService,
    IdentityService,
    MediaService,
    MemoryService,
    NotificationService,
    PlaceService,
    SearchService,
    SharingService,
    TimelineService,
)


class FEMCApi:
    def __init__(self) -> None:
        self.canonical = CanonicalRepository()
        self.derived = DerivedRepository()
        self.authorization = AuthorizationService()
        self.identity = IdentityService(self.canonical)
        self.event = EventService(self.canonical, self.derived, self.authorization)
        self.calendar = CalendarService(self.canonical, self.derived, self.authorization)
        self.memory = MemoryService(self.canonical, self.derived, self.authorization)
        self.place = PlaceService(self.canonical, self.derived, self.authorization)
        self.media = MediaService(self.canonical, self.derived, self.authorization)
        self.timeline = TimelineService(self.canonical, self.derived, self.authorization)
        self.notification = NotificationService(self.canonical, self.authorization)
        self.sharing = SharingService(self.canonical, self.authorization)
        self.search = SearchService(self.derived)





    def create_session(self, account_id: str, duration_minutes: int = 60):
        return self.identity.create_session(account_id, duration_minutes=duration_minutes)

    def _validate_session(self, session_id: str):
        session = self.canonical.get_session(session_id)
        if session is None:
            raise PermissionError("Invalid session")
        if session.expires_at is not None and session.expires_at < datetime.datetime.utcnow():
            raise PermissionError("Session expired")
        return session

    def resolve_family_context_for_session(self, session_id: str):
        session = self._validate_session(session_id)
        return self.identity.resolve_family_context(session.account_id)

    def create_event_for_session(
        self,
        session_id: str,
        title: str,
        description: str,
        family_context_id: Optional[str],
        start_time: datetime.datetime,
        end_time: Optional[datetime.datetime],
        visibility: VisibilityLevel = VisibilityLevel.FAMILY,
        place_id: Optional[str] = None,
    ) -> Event:
        session = self._validate_session(session_id)
        return self.event.create_event(
            owner_id=session.account_id,
            title=title,
            description=description,
            family_context_id=family_context_id,
            start_time=start_time,
            end_time=end_time,
            visibility=visibility,
            place_id=place_id,
        )


    def get_event_for_session(self, session_id: str, event_id: str) -> Event:
        session = self._validate_session(session_id)
        return self.event.get_event_for_account(event_id, session.account_id)

    def get_calendar_for_session(
        self,
        session_id: str,
        family_context_id: str,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
    ):
        session = self._validate_session(session_id)
        return self.calendar.get_calendar_for_context(
            session.account_id,
            family_context_id,
            start_date=start_date,
            end_date=end_date,
        )

    def update_event_status_for_session(
        self,
        session_id: str,
        event_id: str,
        status: EventStatus,
    ) -> Event:
        session = self._validate_session(session_id)
        return self.event.update_event_status(session.account_id, event_id, status)


    def create_memory_for_session(
        self,
        session_id: str,
        event_id: str,
        narrative: str,
        visibility: VisibilityLevel = VisibilityLevel.FAMILY,
    ) -> Memory:
        session = self._validate_session(session_id)
        event = self.canonical.get_event(event_id)
        if event is None:
            raise ValueError("Event does not exist")
        self.event.get_event_for_account(event_id, session.account_id)
        return self.memory.create_memory(
            subject_id=session.account_id,
            narrative=narrative,
            visibility=visibility,
            created_by_id=session.account_id,
            event_id=event_id,
        )

    def get_memory_for_session(self, session_id: str, memory_id: str) -> Memory:
        session = self._validate_session(session_id)
        return self.memory.get_memory_for_account(memory_id, session.account_id)

    def get_event_with_memories_for_session(self, session_id: str, event_id: str) -> EventWithMemories:
        session = self._validate_session(session_id)
        event = self.event.get_event_for_account(event_id, session.account_id)
        if event is None:
            raise ValueError("Event does not exist")
        memories = self.memory.list_memories_for_event_for_account(event_id, session.account_id)
        return EventWithMemories(event=event, memories=memories)

    def discover_context_for_session(self, session_id: str, family_context_id: str) -> ContextDiscoveryResult:
        session = self._validate_session(session_id)
        context = self.identity.resolve_family_context(session.account_id)
        if context is None or context.id != family_context_id:
            raise PermissionError("Account is not authorized for this family context")
        calendar_entries = self.calendar.get_calendar_for_context(session.account_id, family_context_id)
        memories = self.memory.list_memories_for_context_for_account(family_context_id, session.account_id)
        return ContextDiscoveryResult(context=context, calendar_entries=calendar_entries, memories=memories)

    def search_for_session(self, session_id: str, query: str):
        session = self._validate_session(session_id)
        results = self.search.search(query)
        visible_results = []
        for entry in results:
            if entry.type == "event":
                try:
                    self.event.get_event_for_account(entry.id, session.account_id)
                    visible_results.append(entry)
                except PermissionError:
                    continue
            elif entry.type == "memory":
                try:
                    self.memory.get_memory_for_account(entry.id, session.account_id)
                    visible_results.append(entry)
                except PermissionError:
                    continue
        return visible_results

    def create_relationship_for_session(
        self,
        session_id: str,
        source_person_id: str,
        target_person_id: str,
        relationship_type: RelationshipType = RelationshipType.MEMBER,
        confidence: Confidence = Confidence.MEDIUM,
    ) -> Relationship:
        session = self._validate_session(session_id)
        source_person = self.canonical.get_person(source_person_id)
        target_person = self.canonical.get_person(target_person_id)
        if source_person is None or target_person is None:
            raise ValueError("Referenced person does not exist")
        context = self.identity.resolve_family_context(session.account_id)
        if context is None:
            raise PermissionError("Account is not authorized to create relationships")
        return self.identity.create_relationship(
            source_person_id=source_person_id,
            target_person_id=target_person_id,
            relationship_type=relationship_type,
            confidence=confidence,
        )

    def get_family_topology_for_session(self, session_id: str, family_context_id: str) -> FamilyTopologyResult:
        session = self._validate_session(session_id)
        return self.identity.get_family_topology_for_account(family_context_id, session.account_id)

    def create_place_for_session(
        self,
        session_id: str,
        name: str,
        address: str = "",
        family_context_id: Optional[str] = None,
        visibility: VisibilityLevel = VisibilityLevel.FAMILY,
    ) -> Place:
        session = self._validate_session(session_id)
        return self.place.create_place(
            created_by_id=session.account_id,
            name=name,
            address=address,
            family_context_id=family_context_id,
            visibility=visibility,
        )

    def get_place_for_session(self, session_id: str, place_id: str) -> Place:
        session = self._validate_session(session_id)
        place = self.place.get_place_for_account(place_id, session.account_id)
        if place is None:
            raise ValueError("Place does not exist")
        return place

    def list_places_for_session(self, session_id: str, family_context_id: str) -> List[Place]:
        session = self._validate_session(session_id)
        return self.place.list_places_for_context_for_account(family_context_id, session.account_id)

    def create_media_item_for_session(
        self,
        session_id: str,
        uri: str,
        media_type: MediaType = MediaType.PHOTO,
        caption: str = "",
        family_context_id: Optional[str] = None,
        event_id: Optional[str] = None,
        memory_id: Optional[str] = None,
        visibility: VisibilityLevel = VisibilityLevel.FAMILY,
    ) -> MediaItem:
        session = self._validate_session(session_id)
        return self.media.create_media_item(
            owner_id=session.account_id,
            uri=uri,
            media_type=media_type,
            caption=caption,
            family_context_id=family_context_id,
            event_id=event_id,
            memory_id=memory_id,
            visibility=visibility,
        )

    def get_media_item_for_session(self, session_id: str, media_id: str) -> MediaItem:
        session = self._validate_session(session_id)
        item = self.media.get_media_item_for_account(media_id, session.account_id)
        if item is None:
            raise ValueError("Media item does not exist")
        return item

    def list_media_items_for_event_for_session(self, session_id: str, event_id: str) -> List[MediaItem]:
        session = self._validate_session(session_id)
        return self.media.list_media_items_for_event_for_account(event_id, session.account_id)

    def list_media_items_for_memory_for_session(self, session_id: str, memory_id: str) -> List[MediaItem]:
        session = self._validate_session(session_id)
        return self.media.list_media_items_for_memory_for_account(memory_id, session.account_id)

    def create_media_album_for_session(
        self,
        session_id: str,
        title: str,
        description: str = "",
        family_context_id: Optional[str] = None,
        media_ids: Optional[List[str]] = None,
        visibility: VisibilityLevel = VisibilityLevel.FAMILY,
    ) -> MediaAlbum:
        session = self._validate_session(session_id)
        return self.media.create_media_album(
            owner_id=session.account_id,
            title=title,
            description=description,
            family_context_id=family_context_id,
            media_ids=media_ids,
            visibility=visibility,
        )

    def get_media_album_for_session(self, session_id: str, album_id: str) -> MediaAlbum:
        session = self._validate_session(session_id)
        album = self.media.get_media_album_for_account(album_id, session.account_id)
        if album is None:
            raise ValueError("Media album does not exist")
        return album

    def add_media_to_album_for_session(self, session_id: str, album_id: str, media_id: str) -> MediaAlbum:
        session = self._validate_session(session_id)
        return self.media.add_media_to_album(album_id, media_id, session.account_id)

    def get_timeline_for_session(
        self, session_id: str, family_context_id: str, limit: Optional[int] = None
    ) -> List[TimelineProjectionEntry]:
        session = self._validate_session(session_id)
        return self.timeline.get_timeline_for_family_context_for_account(
            family_context_id=family_context_id, account_id=session.account_id, limit=limit
        )

    def create_notification_for_session(
        self,
        session_id: str,
        recipient_id: str,
        notification_type: NotificationType,
        title: str,
        message: str,
        family_context_id: Optional[str] = None,
        target_resource_id: Optional[str] = None,
    ) -> Notification:
        session = self._validate_session(session_id)
        return self.notification.create_notification(
            sender_id=session.account_id,
            recipient_id=recipient_id,
            notification_type=notification_type,
            title=title,
            message=message,
            family_context_id=family_context_id,
            target_resource_id=target_resource_id,
        )

    def get_notification_for_session(self, session_id: str, notification_id: str) -> Notification:
        session = self._validate_session(session_id)
        notif = self.notification.get_notification_for_account(notification_id, session.account_id)
        if notif is None:
            raise ValueError("Notification does not exist")
        return notif

    def list_notifications_for_session(self, session_id: str) -> List[Notification]:
        session = self._validate_session(session_id)
        return self.notification.list_notifications_for_account(session.account_id)

    def mark_notification_read_for_session(self, session_id: str, notification_id: str) -> Notification:
        session = self._validate_session(session_id)
        return self.notification.mark_notification_read(notification_id, session.account_id)

    def create_share_link_for_session(
        self,
        session_id: str,
        resource_type: ShareResourceType,
        resource_id: str,
        family_context_id: Optional[str] = None,
        expires_in_minutes: Optional[int] = None,
    ) -> ShareLink:
        session = self._validate_session(session_id)
        return self.sharing.create_share_link(
            created_by_id=session.account_id,
            resource_type=resource_type,
            resource_id=resource_id,
            family_context_id=family_context_id,
            expires_in_minutes=expires_in_minutes,
        )

    def resolve_share_token(self, token: str):
        return self.sharing.resolve_share_token(token)

    def revoke_share_link_for_session(self, session_id: str, token: str) -> ShareLink:
        session = self._validate_session(session_id)
        return self.sharing.revoke_share_link(token, session.account_id)





