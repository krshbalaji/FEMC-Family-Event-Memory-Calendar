from __future__ import annotations

import datetime
from typing import List, Optional

from .models import (
    Account,
    AuthenticatedSession,
    CalendarProjectionEntry,
    Confidence,
    Consent,
    Event,
    EventStatus,
    FamilyContext,
    MediaAlbum,
    MediaItem,
    MediaType,
    Memory,
    Notification,
    NotificationStatus,
    NotificationType,
    Person,
    Place,
    ProvenanceMetadata,
    ProvenanceSourceType,
    Relationship,
    RelationshipType,
    SearchResultEntry,
    ShareLink,
    ShareResourceType,
    TimelineItemType,
    TimelineProjectionEntry,
    VisibilityLevel,
)



from .repositories import CanonicalRepository, DerivedRepository


class AuthorizationService:
    def can_view_event(self, account_id: str, event: Event, context: Optional[FamilyContext]) -> bool:
        if event.visibility == VisibilityLevel.PUBLIC:
            return True
        if event.visibility == VisibilityLevel.PRIVATE:
            return account_id == event.owner_id
        if event.visibility == VisibilityLevel.FAMILY:
            if context is None:
                return False
            return account_id in context.member_ids or account_id == event.owner_id
        return False

    def can_create_event(self, account_id: str, context: Optional[FamilyContext]) -> bool:
        if context is None:
            return False
        return account_id in context.member_ids

    def can_view_memory(self, account_id: str, memory: Memory, context: Optional[FamilyContext]) -> bool:
        if memory.visibility == VisibilityLevel.PUBLIC:
            return True
        if memory.visibility == VisibilityLevel.PRIVATE:
            return account_id == memory.subject_id
        if memory.visibility == VisibilityLevel.FAMILY:
            return context is not None and account_id in context.member_ids
        return False

    def can_create_memory(self, account_id: str, memory: Memory, context: Optional[FamilyContext]) -> bool:
        if memory.visibility == VisibilityLevel.PUBLIC:
            return True
        if memory.visibility == VisibilityLevel.PRIVATE:
            return account_id == memory.subject_id
        if memory.visibility == VisibilityLevel.FAMILY:
            return context is not None and account_id in context.member_ids
        return False

    def can_view_place(self, account_id: str, place: Place, context: Optional[FamilyContext]) -> bool:
        if place.visibility == VisibilityLevel.PUBLIC:
            return True
        if place.visibility == VisibilityLevel.PRIVATE:
            return place.provenance is not None and account_id == place.provenance.created_by_id
        if place.visibility == VisibilityLevel.FAMILY:
            return context is not None and account_id in context.member_ids
        return False

    def can_create_place(self, account_id: str, context: Optional[FamilyContext]) -> bool:
        if context is None:
            return False
        return account_id in context.member_ids

    def can_view_media_item(self, account_id: str, item: MediaItem, context: Optional[FamilyContext]) -> bool:
        if item.visibility == VisibilityLevel.PUBLIC:
            return True
        if item.visibility == VisibilityLevel.PRIVATE:
            return account_id == item.owner_id
        if item.visibility == VisibilityLevel.FAMILY:
            return context is not None and account_id in context.member_ids
        return False

    def can_create_media_item(self, account_id: str, context: Optional[FamilyContext]) -> bool:
        if context is None:
            return False
        return account_id in context.member_ids

    def can_view_media_album(self, account_id: str, album: MediaAlbum, context: Optional[FamilyContext]) -> bool:
        if album.visibility == VisibilityLevel.PUBLIC:
            return True
        if album.visibility == VisibilityLevel.PRIVATE:
            return account_id == album.owner_id
        if album.visibility == VisibilityLevel.FAMILY:
            return context is not None and account_id in context.member_ids
        return False

    def can_create_media_album(self, account_id: str, context: Optional[FamilyContext]) -> bool:
        if context is None:
            return False
        return account_id in context.member_ids

    def can_view_notification(self, account_id: str, notification: Notification) -> bool:
        return account_id == notification.recipient_id

    def can_create_share_link(
        self, account_id: str, resource_visibility: VisibilityLevel, context: Optional[FamilyContext]
    ) -> bool:
        if resource_visibility == VisibilityLevel.PRIVATE:
            return False
        if resource_visibility == VisibilityLevel.PUBLIC:
            return True
        if resource_visibility == VisibilityLevel.FAMILY:
            return context is not None and account_id in context.member_ids
        return False





class IdentityService:
    def __init__(self, canonical: CanonicalRepository) -> None:
        self.canonical = canonical

    def create_person(self, name: str, birth_date: Optional[datetime.date] = None) -> Person:
        from .models import Person

        person = Person(name=name, birth_date=birth_date)
        return self.canonical.add_person(person)

    def create_account(self, username: str, email: str, person_id: str) -> Account:
        account = Account(username=username, email=email, person_id=person_id)
        return self.canonical.add_account(account)

    def resolve_family_context(self, account_id: str) -> Optional[FamilyContext]:
        for context in self.canonical.list_family_contexts():
            if account_id in context.member_ids:
                return context
        return None

    def create_family_context(self, name: str, member_ids: Optional[List[str]] = None, created_by_id: str = "") -> FamilyContext:
        if member_ids is None:
            member_ids = []
        provenance = ProvenanceMetadata(
            source_type=ProvenanceSourceType.USER,
            source_id=created_by_id,
            created_by_id=created_by_id,
            audit_trail=["family-context-created"],
        )
        context = FamilyContext(name=name, member_ids=member_ids, provenance=provenance)
        return self.canonical.add_family_context(context)

    def create_session(self, account_id: str, duration_minutes: int = 60) -> AuthenticatedSession:
        session = AuthenticatedSession(
            account_id=account_id, expires_at=datetime.datetime.utcnow() + datetime.timedelta(minutes=duration_minutes)
        )
        return self.canonical.add_session(session)

    def add_member_to_context(self, context_id: str, account_id: str) -> Optional[FamilyContext]:
        context = self.canonical.get_family_context(context_id)
        if context is None:
            return None
        if account_id not in context.member_ids:
            context.member_ids.append(account_id)
        return context

    def create_relationship(
        self,
        source_person_id: str,
        target_person_id: str,
        relationship_type: RelationshipType = RelationshipType.MEMBER,
        confidence: Confidence = Confidence.MEDIUM,
    ) -> Relationship:
        source_person = self.canonical.get_person(source_person_id)
        target_person = self.canonical.get_person(target_person_id)
        if source_person is None or target_person is None:
            raise ValueError("Referenced person does not exist")
        relationship = Relationship(
            source_person_id=source_person_id,
            target_person_id=target_person_id,
            relationship_type=relationship_type,
            confidence=confidence,
        )
        saved = self.canonical.add_relationship(relationship)
        if saved.id not in source_person.relationships:
            source_person.relationships.append(saved.id)
        if saved.id not in target_person.relationships:
            target_person.relationships.append(saved.id)
        return saved

    def get_family_topology_for_account(self, family_context_id: str, account_id: str) -> FamilyTopologyResult:
        from .models import FamilyTopologyMember, FamilyTopologyResult

        context = self.canonical.get_family_context(family_context_id)
        if context is None:
            raise ValueError("Family context does not exist")
        if account_id not in context.member_ids:
            raise PermissionError("Account is not authorized for this family context")

        topology_members: List[FamilyTopologyMember] = []
        member_person_ids = set()

        for m_id in context.member_ids:
            acc = self.canonical.get_account(m_id)
            if acc:
                person = self.canonical.get_person(acc.person_id) if acc.person_id else None
                if person:
                    member_person_ids.add(person.id)
                topology_members.append(FamilyTopologyMember(account=acc, person=person))

        topology_relationships: List[Relationship] = []
        for rel in self.canonical.list_relationships():
            if rel.source_person_id in member_person_ids and rel.target_person_id in member_person_ids:
                topology_relationships.append(rel)

        return FamilyTopologyResult(context=context, members=topology_members, relationships=topology_relationships)



class EventService:
    def __init__(self, canonical: CanonicalRepository, derived: DerivedRepository, auth: AuthorizationService) -> None:
        self.canonical = canonical
        self.derived = derived
        self.auth = auth

    def create_event(
        self,
        owner_id: str,
        title: str,
        description: str,
        family_context_id: Optional[str],
        start_time: datetime.datetime,
        end_time: Optional[datetime.datetime],
        visibility: VisibilityLevel = VisibilityLevel.FAMILY,
        place_id: Optional[str] = None,
    ) -> Event:
        context = self.canonical.get_family_context(family_context_id) if family_context_id else None
        if not self.auth.can_create_event(owner_id, context):
            raise PermissionError("Account is not authorized to create events in the target family context")
        if place_id is not None:
            place = self.canonical.get_place(place_id)
            if place is None:
                raise ValueError("Referenced place does not exist")
            if not self.auth.can_view_place(owner_id, place, context):
                raise PermissionError("Account is not authorized to use this place")
        provenance = ProvenanceMetadata(
            source_type=ProvenanceSourceType.USER,
            source_id=owner_id,
            created_by_id=owner_id,
            audit_trail=["event-created"],
        )
        event = Event(
            title=title,
            description=description,
            owner_id=owner_id,
            family_context_id=family_context_id,
            place_id=place_id,
            start_time=start_time,
            end_time=end_time,
            visibility=visibility,
            provenance=provenance,
        )
        saved = self.canonical.add_event(event)
        self._project_event(saved, context)
        return saved


    def _project_event(self, event: Event, context: Optional[FamilyContext]) -> None:
        entry = CalendarProjectionEntry(
            event_id=event.id,
            title=event.title,
            date=event.start_time.date(),
            status=event.status,
            visibility=event.visibility,
            family_context_id=event.family_context_id,
        )
        self.derived.add_calendar_entry(entry)
        self.derived.add_search_entry(
            SearchResultEntry(
                id=event.id,
                type="event",
                title=event.title,
                excerpt=event.description,
                visibility=event.visibility,
            )
        )

    def get_event(self, event_id: str) -> Optional[Event]:
        return self.canonical.get_event(event_id)

    def get_event_for_account(self, event_id: str, account_id: str) -> Optional[Event]:
        event = self.get_event(event_id)
        if event is None:
            return None
        context = self.canonical.get_family_context(event.family_context_id) if event.family_context_id else None
        if not self.auth.can_view_event(account_id, event, context):
            raise PermissionError("Account is not authorized to view this event")
        return event

    def list_events(self) -> List[Event]:
        return self.canonical.list_events()

    def update_event_status(self, account_id: str, event_id: str, status: EventStatus) -> Event:
        event = self.get_event(event_id)
        if event is None:
            raise ValueError("Event does not exist")
        context = self.canonical.get_family_context(event.family_context_id) if event.family_context_id else None
        if not self.auth.can_view_event(account_id, event, context):
            raise PermissionError("Account is not authorized to modify this event")
        if event.owner_id != account_id and (context is None or account_id not in context.member_ids):
            raise PermissionError("Account is not authorized to update status of this event")

        event.status = status
        if event.provenance and event.provenance.audit_trail is not None:
            event.provenance.audit_trail.append(f"status-updated-to-{status.value}")

        self.derived.update_calendar_entry_status(event_id, status)
        return event


class CalendarService:
    def __init__(self, canonical: CanonicalRepository, derived: DerivedRepository, auth: AuthorizationService) -> None:
        self.canonical = canonical
        self.derived = derived
        self.auth = auth

    def get_calendar_for_context(
        self,
        account_id: str,
        family_context_id: str,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
    ) -> List[CalendarProjectionEntry]:
        context = self.canonical.get_family_context(family_context_id)
        if context is None:
            return []
        entries = self.derived.get_calendar_entries(
            family_context_id=family_context_id,
            start_date=start_date,
            end_date=end_date,
        )
        return [entry for entry in entries if self._can_view_projection(account_id, entry, context)]


    def _can_view_projection(self, account_id: str, entry: CalendarProjectionEntry, context: FamilyContext) -> bool:
        if entry.visibility == VisibilityLevel.PUBLIC:
            return True
        if entry.visibility == VisibilityLevel.PRIVATE:
            event = self.canonical.get_event(entry.event_id)
            return event is not None and account_id == event.owner_id
        return account_id in context.member_ids


class MemoryService:
    def __init__(self, canonical: CanonicalRepository, derived: DerivedRepository, auth: AuthorizationService) -> None:
        self.canonical = canonical
        self.derived = derived
        self.auth = auth

    def create_memory(self, subject_id: str, narrative: str, visibility: VisibilityLevel, created_by_id: str, event_id: Optional[str] = None) -> Memory:
        context = None
        for family_context in self.canonical.list_family_contexts():
            if subject_id in family_context.member_ids:
                context = family_context
                break
        if event_id is not None:
            event = self.canonical.get_event(event_id)
            if event is None:
                raise ValueError("Referenced event does not exist")
            if event.family_context_id is not None and context is not None and event.family_context_id != context.id:
                raise PermissionError("Event does not belong to the user's family context")
        memory = Memory(
            event_id=event_id,
            subject_id=subject_id,
            narrative=narrative,
            visibility=visibility,
            provenance=ProvenanceMetadata(
                source_type=ProvenanceSourceType.USER,
                source_id=created_by_id,
                created_by_id=created_by_id,
                audit_trail=["memory-created"],
            ),
        )
        if not self.auth.can_create_memory(created_by_id, memory, context):
            raise PermissionError("Account is not authorized to create this memory")
        saved = self.canonical.add_memory(memory)
        self.derived.add_search_entry(
            SearchResultEntry(
                id=saved.id,
                type="memory",
                title=f"Memory for {saved.subject_id}",
                excerpt=saved.narrative,
                visibility=saved.visibility,
            )
        )
        return saved

    def get_memory(self, memory_id: str) -> Optional[Memory]:
        return self.canonical.get_memory(memory_id)

    def get_memory_for_account(self, memory_id: str, account_id: str) -> Optional[Memory]:
        memory = self.get_memory(memory_id)
        if memory is None:
            return None
        context = None
        for family_context in self.canonical.list_family_contexts():
            if memory.subject_id in family_context.member_ids:
                context = family_context
                break
        if not self.auth.can_view_memory(account_id, memory, context):
            raise PermissionError("Account is not authorized to view this memory")
        return memory

    def list_memories_for_event_for_account(self, event_id: str, account_id: str) -> List[Memory]:
        event = self.canonical.get_event(event_id)
        if event is None:
            raise ValueError("Event does not exist")
        context = self.canonical.get_family_context(event.family_context_id) if event.family_context_id else None
        if not self.auth.can_view_event(account_id, event, context):
            raise PermissionError("Account is not authorized to view this event")
        memories: List[Memory] = []
        for memory in self.canonical.list_memories():
            if memory.event_id != event_id:
                continue
            if self.auth.can_view_memory(account_id, memory, context):
                memories.append(memory)
        return memories

    def list_memories_for_context_for_account(self, family_context_id: str, account_id: str) -> List[Memory]:
        context = self.canonical.get_family_context(family_context_id)
        if context is None:
            raise ValueError("Family context does not exist")
        if account_id not in context.member_ids:
            raise PermissionError("Account is not authorized for this family context")
        memories: List[Memory] = []
        for memory in self.canonical.list_memories():
            if memory.event_id is None:
                continue
            event = self.canonical.get_event(memory.event_id)
            if event is None or event.family_context_id != family_context_id:
                continue
            if not self.auth.can_view_event(account_id, event, context):
                continue
            if self.auth.can_view_memory(account_id, memory, context):
                memories.append(memory)
        return memories


class SearchService:
    def __init__(self, derived: DerivedRepository) -> None:
        self.derived = derived

    def search(self, query: str) -> List[SearchResultEntry]:
        return self.derived.search(query)


class PlaceService:
    def __init__(self, canonical: CanonicalRepository, derived: DerivedRepository, auth: AuthorizationService) -> None:
        self.canonical = canonical
        self.derived = derived
        self.auth = auth

    def create_place(
        self,
        created_by_id: str,
        name: str,
        address: str = "",
        family_context_id: Optional[str] = None,
        visibility: VisibilityLevel = VisibilityLevel.FAMILY,
    ) -> Place:
        context = self.canonical.get_family_context(family_context_id) if family_context_id else None
        if not self.auth.can_create_place(created_by_id, context):
            raise PermissionError("Account is not authorized to create places in this family context")
        provenance = ProvenanceMetadata(
            source_type=ProvenanceSourceType.USER,
            source_id=created_by_id,
            created_by_id=created_by_id,
            audit_trail=["place-created"],
        )
        place = Place(
            name=name,
            address=address,
            family_context_id=family_context_id,
            visibility=visibility,
            provenance=provenance,
        )
        return self.canonical.add_place(place)

    def get_place_for_account(self, place_id: str, account_id: str) -> Optional[Place]:
        place = self.canonical.get_place(place_id)
        if place is None:
            return None
        context = self.canonical.get_family_context(place.family_context_id) if place.family_context_id else None
        if not self.auth.can_view_place(account_id, place, context):
            raise PermissionError("Account is not authorized to view this place")
        return place

    def list_places_for_context_for_account(self, family_context_id: str, account_id: str) -> List[Place]:
        context = self.canonical.get_family_context(family_context_id)
        if context is None:
            raise ValueError("Family context does not exist")
        if account_id not in context.member_ids:
            raise PermissionError("Account is not authorized for this family context")
        places: List[Place] = []
        for place in self.canonical.list_places():
            if place.family_context_id == family_context_id and self.auth.can_view_place(account_id, place, context):
                places.append(place)
        return places


class MediaService:
    def __init__(self, canonical: CanonicalRepository, derived: DerivedRepository, auth: AuthorizationService) -> None:
        self.canonical = canonical
        self.derived = derived
        self.auth = auth

    def create_media_item(
        self,
        owner_id: str,
        uri: str,
        media_type: MediaType = MediaType.PHOTO,
        caption: str = "",
        family_context_id: Optional[str] = None,
        event_id: Optional[str] = None,
        memory_id: Optional[str] = None,
        visibility: VisibilityLevel = VisibilityLevel.FAMILY,
    ) -> MediaItem:
        context = self.canonical.get_family_context(family_context_id) if family_context_id else None
        if event_id:
            event = self.canonical.get_event(event_id)
            if event is None:
                raise ValueError("Referenced event does not exist")
        if memory_id:
            memory = self.canonical.get_memory(memory_id)
            if memory is None:
                raise ValueError("Referenced memory does not exist")
        provenance = ProvenanceMetadata(
            source_type=ProvenanceSourceType.USER,
            source_id=owner_id,
            created_by_id=owner_id,
            audit_trail=["media-item-created"],
        )
        item = MediaItem(
            uri=uri,
            media_type=media_type,
            caption=caption,
            owner_id=owner_id,
            family_context_id=family_context_id,
            event_id=event_id,
            memory_id=memory_id,
            visibility=visibility,
            provenance=provenance,
        )
        if not self.auth.can_create_media_item(owner_id, context):
            raise PermissionError("Account is not authorized to create media items in this context")
        return self.canonical.add_media_item(item)

    def get_media_item_for_account(self, media_id: str, account_id: str) -> Optional[MediaItem]:
        item = self.canonical.get_media_item(media_id)
        if item is None:
            return None
        context = self.canonical.get_family_context(item.family_context_id) if item.family_context_id else None
        if not self.auth.can_view_media_item(account_id, item, context):
            raise PermissionError("Account is not authorized to view this media item")
        return item

    def list_media_items_for_event_for_account(self, event_id: str, account_id: str) -> List[MediaItem]:
        event = self.canonical.get_event(event_id)
        if event is None:
            raise ValueError("Event does not exist")
        context = self.canonical.get_family_context(event.family_context_id) if event.family_context_id else None
        items: List[MediaItem] = []
        for item in self.canonical.list_media_items():
            if item.event_id == event_id and self.auth.can_view_media_item(account_id, item, context):
                items.append(item)
        return items

    def list_media_items_for_memory_for_account(self, memory_id: str, account_id: str) -> List[MediaItem]:
        memory = self.canonical.get_memory(memory_id)
        if memory is None:
            raise ValueError("Memory does not exist")
        context = None
        for family_context in self.canonical.list_family_contexts():
            if memory.subject_id in family_context.member_ids:
                context = family_context
                break
        items: List[MediaItem] = []
        for item in self.canonical.list_media_items():
            if item.memory_id == memory_id and self.auth.can_view_media_item(account_id, item, context):
                items.append(item)
        return items

    def create_media_album(
        self,
        owner_id: str,
        title: str,
        description: str = "",
        family_context_id: Optional[str] = None,
        media_ids: Optional[List[str]] = None,
        visibility: VisibilityLevel = VisibilityLevel.FAMILY,
    ) -> MediaAlbum:
        if media_ids is None:
            media_ids = []
        context = self.canonical.get_family_context(family_context_id) if family_context_id else None
        provenance = ProvenanceMetadata(
            source_type=ProvenanceSourceType.USER,
            source_id=owner_id,
            created_by_id=owner_id,
            audit_trail=["media-album-created"],
        )
        album = MediaAlbum(
            title=title,
            description=description,
            owner_id=owner_id,
            family_context_id=family_context_id,
            media_ids=media_ids,
            visibility=visibility,
            provenance=provenance,
        )
        if not self.auth.can_create_media_album(owner_id, context):
            raise PermissionError("Account is not authorized to create media albums in this context")
        return self.canonical.add_media_album(album)

    def get_media_album_for_account(self, album_id: str, account_id: str) -> Optional[MediaAlbum]:
        album = self.canonical.get_media_album(album_id)
        if album is None:
            return None
        context = self.canonical.get_family_context(album.family_context_id) if album.family_context_id else None
        if not self.auth.can_view_media_album(account_id, album, context):
            raise PermissionError("Account is not authorized to view this media album")
        return album

    def add_media_to_album(self, album_id: str, media_id: str, account_id: str) -> MediaAlbum:
        album = self.get_media_album_for_account(album_id, account_id)
        if album is None:
            raise ValueError("Media album does not exist")
        media = self.get_media_item_for_account(media_id, account_id)
        if media is None:
            raise ValueError("Media item does not exist")
        if media_id not in album.media_ids:
            album.media_ids.append(media_id)
        return album


class TimelineService:
    def __init__(self, canonical: CanonicalRepository, derived: DerivedRepository, auth: AuthorizationService) -> None:
        self.canonical = canonical
        self.derived = derived
        self.auth = auth

    def rebuild_timeline_projection(self) -> None:
        self.derived.clear_timeline_entries()

        for event in self.canonical.list_events():
            self.derived.add_timeline_entry(
                TimelineProjectionEntry(
                    id=f"timeline-event-{event.id}",
                    item_type=TimelineItemType.EVENT,
                    timestamp=event.start_time,
                    title=event.title,
                    summary=event.description,
                    owner_id=event.owner_id,
                    family_context_id=event.family_context_id,
                    visibility=event.visibility,
                    ref_id=event.id,
                )
            )

        for memory in self.canonical.list_memories():
            owner_id = memory.subject_id
            family_context_id = None
            if memory.event_id:
                ev = self.canonical.get_event(memory.event_id)
                if ev:
                    family_context_id = ev.family_context_id
            if family_context_id is None:
                for fc in self.canonical.list_family_contexts():
                    if memory.subject_id in fc.member_ids:
                        family_context_id = fc.id
                        break

            self.derived.add_timeline_entry(
                TimelineProjectionEntry(
                    id=f"timeline-memory-{memory.id}",
                    item_type=TimelineItemType.MEMORY,
                    timestamp=memory.recorded_at,
                    title="Memory Recorded",
                    summary=memory.narrative,
                    owner_id=owner_id,
                    family_context_id=family_context_id,
                    visibility=memory.visibility,
                    ref_id=memory.id,
                )
            )

        for item in self.canonical.list_media_items():
            self.derived.add_timeline_entry(
                TimelineProjectionEntry(
                    id=f"timeline-media-{item.id}",
                    item_type=TimelineItemType.MEDIA,
                    timestamp=item.created_at,
                    title=f"Media ({item.media_type.value})",
                    summary=item.caption or item.uri,
                    owner_id=item.owner_id,
                    family_context_id=item.family_context_id,
                    visibility=item.visibility,
                    ref_id=item.id,
                )
            )

        for place in self.canonical.list_places():
            created_by = place.provenance.created_by_id if place.provenance else ""
            self.derived.add_timeline_entry(
                TimelineProjectionEntry(
                    id=f"timeline-place-{place.id}",
                    item_type=TimelineItemType.PLACE,
                    timestamp=place.created_at,
                    title=place.name,
                    summary=place.address,
                    owner_id=created_by,
                    family_context_id=place.family_context_id,
                    visibility=place.visibility,
                    ref_id=place.id,
                )
            )

    def get_timeline_for_family_context_for_account(
        self, family_context_id: str, account_id: str, limit: Optional[int] = None
    ) -> List[TimelineProjectionEntry]:
        context = self.canonical.get_family_context(family_context_id)
        if context is None:
            raise ValueError("Family context does not exist")
        if account_id not in context.member_ids:
            raise PermissionError("Account is not authorized for this family context")

        self.rebuild_timeline_projection()

        all_entries = self.derived.get_timeline_entries(family_context_id=family_context_id)

        authorized_entries: List[TimelineProjectionEntry] = []
        for entry in all_entries:
            if entry.item_type == TimelineItemType.EVENT:
                ev = self.canonical.get_event(entry.ref_id)
                if ev and self.auth.can_view_event(account_id, ev, context):
                    authorized_entries.append(entry)
            elif entry.item_type == TimelineItemType.MEMORY:
                mem = self.canonical.get_memory(entry.ref_id)
                if mem and self.auth.can_view_memory(account_id, mem, context):
                    authorized_entries.append(entry)
            elif entry.item_type == TimelineItemType.MEDIA:
                med = self.canonical.get_media_item(entry.ref_id)
                if med and self.auth.can_view_media_item(account_id, med, context):
                    authorized_entries.append(entry)
            elif entry.item_type == TimelineItemType.PLACE:
                plc = self.canonical.get_place(entry.ref_id)
                if plc and self.auth.can_view_place(account_id, plc, context):
                    authorized_entries.append(entry)

        authorized_entries.sort(key=lambda x: x.timestamp, reverse=True)

        if limit is not None and limit > 0:
            return authorized_entries[:limit]
        return authorized_entries


class NotificationService:
    def __init__(self, canonical: CanonicalRepository, auth: AuthorizationService) -> None:
        self.canonical = canonical
        self.auth = auth

    def create_notification(
        self,
        sender_id: str,
        recipient_id: str,
        notification_type: NotificationType,
        title: str,
        message: str,
        family_context_id: Optional[str] = None,
        target_resource_id: Optional[str] = None,
    ) -> Notification:
        recipient = self.canonical.get_account(recipient_id)
        if recipient is None:
            raise ValueError("Recipient account does not exist")
        provenance = ProvenanceMetadata(
            source_type=ProvenanceSourceType.USER,
            source_id=sender_id,
            created_by_id=sender_id,
            audit_trail=["notification-created"],
        )
        notification = Notification(
            recipient_id=recipient_id,
            sender_id=sender_id,
            notification_type=notification_type,
            title=title,
            message=message,
            family_context_id=family_context_id,
            target_resource_id=target_resource_id,
            status=NotificationStatus.UNREAD,
            visibility=VisibilityLevel.PRIVATE,
            provenance=provenance,
        )
        return self.canonical.add_notification(notification)

    def get_notification_for_account(self, notification_id: str, account_id: str) -> Optional[Notification]:
        notification = self.canonical.get_notification(notification_id)
        if notification is None:
            return None
        if not self.auth.can_view_notification(account_id, notification):
            raise PermissionError("Account is not authorized to view this notification")
        return notification

    def list_notifications_for_account(self, account_id: str) -> List[Notification]:
        return [n for n in self.canonical.list_notifications() if n.recipient_id == account_id]

    def mark_notification_read(self, notification_id: str, account_id: str) -> Notification:
        notification = self.get_notification_for_account(notification_id, account_id)
        if notification is None:
            raise ValueError("Notification does not exist")
        notification.status = NotificationStatus.READ
        return notification


class SharingService:
    def __init__(self, canonical: CanonicalRepository, auth: AuthorizationService) -> None:
        self.canonical = canonical
        self.auth = auth

    def create_share_link(
        self,
        created_by_id: str,
        resource_type: ShareResourceType,
        resource_id: str,
        family_context_id: Optional[str] = None,
        expires_in_minutes: Optional[int] = None,
    ) -> ShareLink:
        resource_visibility = VisibilityLevel.PRIVATE
        context = self.canonical.get_family_context(family_context_id) if family_context_id else None

        if resource_type == ShareResourceType.EVENT:
            event = self.canonical.get_event(resource_id)
            if event is None:
                raise ValueError("Referenced event does not exist")
            resource_visibility = event.visibility
            if context is None and event.family_context_id:
                context = self.canonical.get_family_context(event.family_context_id)
            if not self.auth.can_view_event(created_by_id, event, context):
                raise PermissionError("Account is not authorized for target resource")
        elif resource_type == ShareResourceType.MEMORY:
            memory = self.canonical.get_memory(resource_id)
            if memory is None:
                raise ValueError("Referenced memory does not exist")
            resource_visibility = memory.visibility
            if context is None:
                if memory.event_id:
                    ev = self.canonical.get_event(memory.event_id)
                    if ev and ev.family_context_id:
                        context = self.canonical.get_family_context(ev.family_context_id)
                if context is None:
                    for fc in self.canonical.list_family_contexts():
                        if memory.subject_id in fc.member_ids:
                            context = fc
                            break
            if not self.auth.can_view_memory(created_by_id, memory, context):
                raise PermissionError("Account is not authorized for target resource")
        elif resource_type == ShareResourceType.MEDIA_ITEM:
            media = self.canonical.get_media_item(resource_id)
            if media is None:
                raise ValueError("Referenced media item does not exist")
            resource_visibility = media.visibility
            if context is None and media.family_context_id:
                context = self.canonical.get_family_context(media.family_context_id)
            if not self.auth.can_view_media_item(created_by_id, media, context):
                raise PermissionError("Account is not authorized for target resource")
        elif resource_type == ShareResourceType.MEDIA_ALBUM:
            album = self.canonical.get_media_album(resource_id)
            if album is None:
                raise ValueError("Referenced media album does not exist")
            resource_visibility = album.visibility
            if context is None and album.family_context_id:
                context = self.canonical.get_family_context(album.family_context_id)
            if not self.auth.can_view_media_album(created_by_id, album, context):
                raise PermissionError("Account is not authorized for target resource")


        if resource_visibility == VisibilityLevel.PRIVATE:
            raise PermissionError("Cannot create share link for private resources")

        if not self.auth.can_create_share_link(created_by_id, resource_visibility, context):
            raise PermissionError("Account is not authorized to share this resource")

        expires_at = None
        if expires_in_minutes is not None and expires_in_minutes > 0:
            expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_in_minutes)

        provenance = ProvenanceMetadata(
            source_type=ProvenanceSourceType.USER,
            source_id=created_by_id,
            created_by_id=created_by_id,
            audit_trail=["share-link-created"],
        )

        share_link = ShareLink(
            resource_type=resource_type,
            resource_id=resource_id,
            created_by_id=created_by_id,
            family_context_id=family_context_id,
            is_revoked=False,
            expires_at=expires_at,
            provenance=provenance,
        )
        return self.canonical.add_share_link(share_link)

    def resolve_share_token(self, token: str):
        share_link = self.canonical.get_share_link_by_token(token)
        if share_link is None:
            raise ValueError("Share link not found")
        if share_link.is_revoked:
            raise PermissionError("Share link has been revoked")
        if share_link.expires_at is not None and share_link.expires_at < datetime.datetime.utcnow():
            raise PermissionError("Share link has expired")

        if share_link.resource_type == ShareResourceType.EVENT:
            event = self.canonical.get_event(share_link.resource_id)
            if event is None or event.visibility == VisibilityLevel.PRIVATE:
                raise PermissionError("Resource unavailable or private")
            return event
        elif share_link.resource_type == ShareResourceType.MEMORY:
            memory = self.canonical.get_memory(share_link.resource_id)
            if memory is None or memory.visibility == VisibilityLevel.PRIVATE:
                raise PermissionError("Resource unavailable or private")
            return memory
        elif share_link.resource_type == ShareResourceType.MEDIA_ITEM:
            media = self.canonical.get_media_item(share_link.resource_id)
            if media is None or media.visibility == VisibilityLevel.PRIVATE:
                raise PermissionError("Resource unavailable or private")
            return media
        elif share_link.resource_type == ShareResourceType.MEDIA_ALBUM:
            album = self.canonical.get_media_album(share_link.resource_id)
            if album is None or album.visibility == VisibilityLevel.PRIVATE:
                raise PermissionError("Resource unavailable or private")
            return album

        raise ValueError("Invalid resource type")

    def revoke_share_link(self, token: str, account_id: str) -> ShareLink:
        share_link = self.canonical.get_share_link_by_token(token)
        if share_link is None:
            raise ValueError("Share link not found")
        if share_link.created_by_id != account_id:
            raise PermissionError("Only creator can revoke share link")
        share_link.is_revoked = True
        return share_link




