from __future__ import annotations

import datetime
import hashlib
from typing import List, Optional, Dict, Any

from .models import (
    ActionType,
    ResourceType,
    TransactionRecord,
    Account,
    ActionProposal,
    AnomalySeverity,
    AnomalyType,
    AuditAnomaly,
    AuthenticatedSession,
    CalendarProjectionEntry,
    CelebrationArtifact,
    CelebrationArtifactType,
    Confidence,
    Consent,
    DashboardEntryType,
    DashboardProjectionEntry,
    DashboardSummary,
    DataExportResult,
    Event,
    EventCategory,
    EventStatus,
    ExportValidationResult,
    FamilyContext,
    InsightAnalysis,
    MediaAlbum,
    MediaItem,
    MediaType,
    Memory,
    Notification,
    NotificationStatus,
    NotificationType,
    Person,
    Place,
    ProposalStatus,
    ProposalType,
    ProvenanceMetadata,
    ProvenanceSourceType,
    Relationship,
    RelationshipType,
    RecurrenceFrequency,
    RecurrenceRule,
    ReminderConfig,
    ReminderStatus,
    ReminderType,
    RepairClassification,
    RepairProposal,
    RichEventDetail,
    RichPersonDetail,


    _utc_now,
    SearchResultEntry,
    ShareLink,
    ShareResourceType,
    TimelineItemType,
    TimelineProjectionEntry,
    ValidationReport,
    VisibilityLevel,
    ContextType,
    AgeGroup,
    Language,
    GuideMode,
    SceneDefinition,
    GuideSessionState,
    MayilPracticeWorld,
)



from .repositories import CanonicalRepository, DerivedRepository, TransactionMemoryRepository


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
            account_id=account_id, expires_at=_utc_now() + datetime.timedelta(minutes=duration_minutes)
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



def get_event_occurrences(event: Event, start_date: datetime.date, end_date: datetime.date) -> List[datetime.date]:
    base_date = event.start_time.date()
    if event.recurrence_rule is None:
        if start_date <= base_date <= end_date:
            return [base_date]
        return []

    rule = event.recurrence_rule
    freq = rule.frequency
    interval = max(1, rule.interval)
    until = rule.until_date

    occurrences: List[datetime.date] = []
    target_day = base_date.day
    target_month = base_date.month

    count = 0
    if base_date < start_date:
        if freq == RecurrenceFrequency.DAILY:
            steps = (start_date - base_date).days // interval
            count = max(0, steps)
        elif freq == RecurrenceFrequency.WEEKLY:
            steps = (start_date - base_date).days // (7 * interval)
            count = max(0, steps)
        elif freq == RecurrenceFrequency.MONTHLY:
            m_diff = (start_date.year - base_date.year) * 12 + (start_date.month - base_date.month)
            steps = m_diff // interval
            count = max(0, steps)
        elif freq == RecurrenceFrequency.YEARLY:
            y_diff = start_date.year - base_date.year
            steps = y_diff // interval
            count = max(0, steps)

    import calendar

    while count < 500:
        if freq == RecurrenceFrequency.DAILY:
            curr = base_date + datetime.timedelta(days=count * interval)
        elif freq == RecurrenceFrequency.WEEKLY:
            curr = base_date + datetime.timedelta(days=count * 7 * interval)
        elif freq == RecurrenceFrequency.MONTHLY:
            total_months = (base_date.year * 12 + base_date.month - 1) + count * interval
            new_year = total_months // 12
            new_month = (total_months % 12) + 1
            max_days = calendar.monthrange(new_year, new_month)[1]
            new_day = min(target_day, max_days)
            curr = datetime.date(new_year, new_month, new_day)
        elif freq == RecurrenceFrequency.YEARLY:
            new_year = base_date.year + count * interval
            max_days = calendar.monthrange(new_year, target_month)[1]
            new_day = min(target_day, max_days)
            curr = datetime.date(new_year, target_month, new_day)

        if until and curr > until:
            break
        if curr > end_date:
            break
        if curr >= start_date:
            occurrences.append(curr)

        count += 1

    return occurrences



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
        recurrence_rule: Optional[RecurrenceRule] = None,
        category: EventCategory = EventCategory.GENERAL,
        target_person_ids: Optional[List[str]] = None,
        milestone_year: Optional[int] = None,
        milestone_anchor_date: Optional[datetime.date] = None,
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
            recurrence_rule=recurrence_rule,
            category=category,
            target_person_ids=target_person_ids or [],
            milestone_year=milestone_year,
            milestone_anchor_date=milestone_anchor_date,
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

    def rebuild_calendar_projection(self, family_context_id: str) -> List[CalendarProjectionEntry]:
        context = self.canonical.get_family_context(family_context_id)
        if context is None:
            return []

        self.derived.calendar_entries = [c for c in self.derived.calendar_entries if c.family_context_id != family_context_id]

        rebuilt = []
        for ev in self.canonical.list_events():
            if ev.family_context_id == family_context_id:
                entry = CalendarProjectionEntry(
                    event_id=ev.id,
                    title=ev.title,
                    date=ev.start_time.date(),
                    status=ev.status,
                    visibility=ev.visibility,
                    family_context_id=ev.family_context_id,
                )
                self.derived.add_calendar_entry(entry)
                rebuilt.append(entry)
        return rebuilt



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

        s_date = start_date if start_date is not None else datetime.date(1970, 1, 1)
        e_date = end_date if end_date is not None else datetime.date(2099, 12, 31)

        result_entries: List[CalendarProjectionEntry] = []

        for ev in self.canonical.list_events():
            if ev.family_context_id == family_context_id:
                occs = get_event_occurrences(ev, s_date, e_date)
                for occ in occs:
                    entry = CalendarProjectionEntry(
                        event_id=ev.id,
                        title=ev.title,
                        date=occ,
                        status=ev.status,
                        visibility=ev.visibility,
                        family_context_id=ev.family_context_id,
                    )
                    if self._can_view_projection(account_id, entry, context):
                        result_entries.append(entry)

        result_entries.sort(key=lambda x: x.date)
        return result_entries



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


class ReminderService:
    def __init__(self, canonical: CanonicalRepository, auth: AuthorizationService, notification_service: NotificationService) -> None:
        self.canonical = canonical
        self.auth = auth
        self.notification_service = notification_service

    def create_reminder(
        self,
        created_by_id: str,
        event_id: str,
        offset_minutes: int = 15,
        reminder_type: ReminderType = ReminderType.EVENT_START,
    ) -> ReminderConfig:
        event = self.canonical.get_event(event_id)
        if event is None:
            raise ValueError("Referenced event does not exist")

        context = self.canonical.get_family_context(event.family_context_id) if event.family_context_id else None
        if not self.auth.can_view_event(created_by_id, event, context):
            raise PermissionError("Account is not authorized to create reminders for this event")

        provenance = ProvenanceMetadata(
            source_type=ProvenanceSourceType.USER,
            source_id=created_by_id,
            created_by_id=created_by_id,
            audit_trail=["reminder-created"],
        )

        reminder = ReminderConfig(
            event_id=event_id,
            family_context_id=event.family_context_id,
            offset_minutes=offset_minutes,
            reminder_type=reminder_type,
            status=ReminderStatus.PENDING,
            created_by_id=created_by_id,
            provenance=provenance,
        )
        return self.canonical.add_reminder(reminder)

    def list_reminders_for_event(self, account_id: str, event_id: str) -> List[ReminderConfig]:
        event = self.canonical.get_event(event_id)
        if event is None:
            raise ValueError("Referenced event does not exist")

        context = self.canonical.get_family_context(event.family_context_id) if event.family_context_id else None
        if not self.auth.can_view_event(account_id, event, context):
            raise PermissionError("Account is not authorized to view reminders for this event")

        return [r for r in self.canonical.list_reminders() if r.event_id == event_id]

    def evaluate_due_reminders(
        self,
        account_id: str,
        family_context_id: str,
        current_time: Optional[datetime.datetime] = None,
    ) -> List[Notification]:
        context = self.canonical.get_family_context(family_context_id)
        if context is None:
            raise ValueError("Family context does not exist")
        if account_id not in context.member_ids:
            raise PermissionError("Account is not authorized for this family context")

        if current_time is None:
            current_time = _utc_now()

        triggered_notifications: List[Notification] = []

        for reminder in self.canonical.list_reminders():
            if reminder.family_context_id == family_context_id and reminder.status == ReminderStatus.PENDING:
                event = self.canonical.get_event(reminder.event_id)
                if event is None:
                    continue

                if not self.auth.can_view_event(reminder.created_by_id, event, context):
                    continue

                trigger_time = event.start_time - datetime.timedelta(minutes=reminder.offset_minutes)

                if current_time >= trigger_time:
                    try:
                        notif = self.notification_service.create_notification(
                            sender_id="system-reminder-service",
                            recipient_id=reminder.created_by_id,
                            notification_type=NotificationType.SYSTEM_ALERT,
                            title=f"Reminder: {event.title}",
                            message=f"Event '{event.title}' is starting soon (in {reminder.offset_minutes} minutes).",
                            family_context_id=family_context_id,
                            target_resource_id=event.id,
                        )
                        reminder.status = ReminderStatus.TRIGGERED
                        reminder.last_triggered_at = current_time
                        if reminder.provenance and reminder.provenance.audit_trail is not None:
                            reminder.provenance.audit_trail.append(f"reminder-triggered-at:{current_time.isoformat()}")
                        triggered_notifications.append(notif)
                    except Exception:
                        pass


        return triggered_notifications



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
            expires_at = _utc_now() + datetime.timedelta(minutes=expires_in_minutes)

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
        if share_link.expires_at is not None and share_link.expires_at < _utc_now():
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


class DashboardService:
    def __init__(
        self,
        canonical: CanonicalRepository,
        derived: DerivedRepository,
        auth: AuthorizationService,
        calendar_service: Optional[CalendarService] = None,
        event_service: Optional[EventService] = None,
        memory_service: Optional[MemoryService] = None,
        media_service: Optional[MediaService] = None,
        reminder_service: Optional[ReminderService] = None,
        notification_service: Optional[NotificationService] = None,
    ) -> None:
        self.canonical = canonical
        self.derived = derived
        self.auth = auth
        self.calendar_service = calendar_service
        self.event_service = event_service
        self.memory_service = memory_service
        self.media_service = media_service
        self.reminder_service = reminder_service
        self.notification_service = notification_service

    def build_rich_event_detail(self, account_id: str, event_id: str) -> RichEventDetail:
        event = self.canonical.get_event(event_id)
        if event is None:
            raise ValueError("Event does not exist")
        context = self.canonical.get_family_context(event.family_context_id) if event.family_context_id else None
        if not self.auth.can_view_event(account_id, event, context):
            raise PermissionError("Account is not authorized to view this event")

        place = None
        if event.place_id:
            p = self.canonical.get_place(event.place_id)
            if p and self.auth.can_view_place(account_id, p, context):
                place = p

        memories = [m for m in self.canonical.list_memories() if m.event_id == event.id and self.auth.can_view_memory(account_id, m, context)]
        media_items = [mi for mi in self.canonical.list_media_items() if mi.event_id == event.id and self.auth.can_view_media_item(account_id, mi, context)]
        reminders = [r for r in self.canonical.list_reminders() if r.event_id == event.id]

        target_persons = []
        for pid in event.target_person_ids:
            person = self.canonical.get_person(pid)
            if person:
                target_persons.append(person)

        milestone_year = event.milestone_year
        if milestone_year is None:
            if event.milestone_anchor_date and event.start_time:
                milestone_year = event.start_time.year - event.milestone_anchor_date.year
            elif event.category in (EventCategory.BIRTHDAY, EventCategory.ANNIVERSARY, EventCategory.MILESTONE):
                if target_persons and target_persons[0].birth_date and event.start_time:
                    milestone_year = event.start_time.year - target_persons[0].birth_date.year

        upcoming_occurrences: List[datetime.date] = []
        if event.recurrence_rule:
            start_date = event.start_time.date()
            end_date = start_date + datetime.timedelta(days=365)
            upcoming_occurrences = get_event_occurrences(event, start_date, end_date)

        return RichEventDetail(
            event=event,
            place=place,
            memories=memories,
            media_items=media_items,
            reminders=reminders,
            target_persons=target_persons,
            milestone_year=milestone_year,
            upcoming_occurrences=upcoming_occurrences,
        )

    def build_rich_person_detail(self, account_id: str, person_id: str) -> RichPersonDetail:
        person = self.canonical.get_person(person_id)
        if person is None:
            raise ValueError("Person does not exist")

        account = None
        for acc in self.canonical.list_accounts():
            if acc.person_id == person_id:
                account = acc
                break

        relationships = [
            rel for rel in self.canonical.list_relationships()
            if rel.source_person_id == person_id or rel.target_person_id == person_id
        ]

        context = None
        for fc in self.canonical.list_family_contexts():
            if account_id in fc.member_ids:
                context = fc
                break

        events = [
            ev for ev in self.canonical.list_events()
            if (person_id in ev.target_person_ids or (account and ev.owner_id == account.id))
            and self.auth.can_view_event(account_id, ev, context)
        ]

        event_ids = {ev.id for ev in events}

        memories = [
            m for m in self.canonical.list_memories()
            if (m.subject_id == person_id or (account and m.subject_id == account.id) or (m.event_id and m.event_id in event_ids))
            and self.auth.can_view_memory(account_id, m, context)
        ]
        memory_ids = {m.id for m in memories}

        media_items = [
            mi for mi in self.canonical.list_media_items()
            if ((account and mi.owner_id == account.id) or (mi.event_id and mi.event_id in event_ids) or (mi.memory_id and mi.memory_id in memory_ids))
            and self.auth.can_view_media_item(account_id, mi, context)
        ]

        milestones = [
            ev for ev in events
            if ev.category in (EventCategory.MILESTONE, EventCategory.BIRTHDAY, EventCategory.ANNIVERSARY) or ev.milestone_year is not None
        ]

        return RichPersonDetail(
            person=person,
            account=account,
            relationships=relationships,
            events=events,
            memories=memories,
            media_items=media_items,
            milestones=milestones,
        )

    def generate_dashboard_summary(self, account_id: str, family_context_id: str) -> DashboardSummary:
        context = self.canonical.get_family_context(family_context_id)
        if context is None:
            raise ValueError("Family context does not exist")
        if account_id not in context.member_ids:
            raise PermissionError("Account is not authorized for this family context")

        member_count = len(context.member_ids)

        visible_events = [
            ev for ev in self.canonical.list_events()
            if ev.family_context_id == family_context_id and self.auth.can_view_event(account_id, ev, context)
        ]

        upcoming_events = [self.build_rich_event_detail(account_id, ev.id) for ev in visible_events]

        due_reminders = []
        for r in self.canonical.list_reminders():
            if r.family_context_id == family_context_id or r.created_by_id == account_id:
                if r.event_id:
                    event = self.canonical.get_event(r.event_id)
                    if event is None or not self.auth.can_view_event(account_id, event, context):
                        continue
                due_reminders.append(r)

        recent_memories = [
            m for m in self.canonical.list_memories()
            if self.auth.can_view_memory(account_id, m, context)
        ]

        active_notifications = [
            n for n in self.canonical.list_notifications()
            if n.recipient_id == account_id and n.status == NotificationStatus.UNREAD
        ]

        celebration_highlights = [
            detail for detail in upcoming_events
            if detail.event.category in (EventCategory.BIRTHDAY, EventCategory.ANNIVERSARY, EventCategory.MILESTONE)
        ]

        return DashboardSummary(
            family_context=context,
            member_count=member_count,
            upcoming_events=upcoming_events,
            due_reminders=due_reminders,
            recent_memories=recent_memories,
            active_notifications=active_notifications,
            celebration_highlights=celebration_highlights,
        )

    def project_dashboard_entries(self, account_id: str, family_context_id: str) -> List[DashboardProjectionEntry]:
        summary = self.generate_dashboard_summary(account_id, family_context_id)
        self.derived.clear_dashboard_entries(family_context_id)

        projected: List[DashboardProjectionEntry] = []

        for detail in summary.upcoming_events:
            entry = DashboardProjectionEntry(
                family_context_id=family_context_id,
                item_type=DashboardEntryType.RECURRING_EVENT if detail.event.recurrence_rule else DashboardEntryType.UPCOMING_EVENT,
                title=detail.event.title,
                subtitle=detail.event.description,
                date_or_time=detail.event.start_time,
                ref_id=detail.event.id,
                visibility=detail.event.visibility,
            )
            self.derived.add_dashboard_entry(entry)
            projected.append(entry)

        for rem in summary.due_reminders:
            rem_vis = VisibilityLevel.FAMILY
            if rem.event_id:
                event = self.canonical.get_event(rem.event_id)
                if event:
                    rem_vis = event.visibility
            entry = DashboardProjectionEntry(
                family_context_id=family_context_id,
                item_type=DashboardEntryType.DUE_REMINDER,
                title=f"Reminder: {rem.reminder_type.value if hasattr(rem.reminder_type, 'value') else str(rem.reminder_type)}",
                subtitle=f"Offset {rem.offset_minutes} mins",
                date_or_time=rem.created_at,
                ref_id=rem.id,
                visibility=rem_vis,
            )
            self.derived.add_dashboard_entry(entry)
            projected.append(entry)

        for mem in summary.recent_memories:
            entry = DashboardProjectionEntry(
                family_context_id=family_context_id,
                item_type=DashboardEntryType.RECENT_MEMORY,
                title="Memory",
                subtitle=mem.narrative,
                date_or_time=mem.recorded_at,
                ref_id=mem.id,
                visibility=mem.visibility,
            )
            self.derived.add_dashboard_entry(entry)
            projected.append(entry)

        for notif in summary.active_notifications:
            entry = DashboardProjectionEntry(
                family_context_id=family_context_id,
                item_type=DashboardEntryType.ACTIVE_NOTIFICATION,
                title=notif.title,
                subtitle=notif.message,
                date_or_time=notif.created_at,
                ref_id=notif.id,
                visibility=notif.visibility,
            )
            self.derived.add_dashboard_entry(entry)
            projected.append(entry)

        for ch in summary.celebration_highlights:
            entry = DashboardProjectionEntry(
                family_context_id=family_context_id,
                item_type=DashboardEntryType.CELEBRATION_HIGHLIGHT,
                title=f"Celebration: {ch.event.title}",
                subtitle=f"Category: {ch.event.category.value if hasattr(ch.event.category, 'value') else str(ch.event.category)}",
                date_or_time=ch.event.start_time,
                ref_id=ch.event.id,
                visibility=ch.event.visibility,
            )
            self.derived.add_dashboard_entry(entry)
            projected.append(entry)

        return projected

    def get_dashboard_projection(self, account_id: str, family_context_id: str) -> List[DashboardProjectionEntry]:
        context = self.canonical.get_family_context(family_context_id)
        if context is None:
            raise ValueError("Family context does not exist")
        if account_id not in context.member_ids:
            raise PermissionError("Account is not authorized for this family context")

        entries = self.derived.get_dashboard_entries(family_context_id)
        if not entries:
            entries = self.project_dashboard_entries(account_id, family_context_id)

        authorized_entries = []
        for entry in entries:
            if entry.visibility == VisibilityLevel.PRIVATE:
                if entry.ref_id:
                    if entry.item_type in (DashboardEntryType.UPCOMING_EVENT, DashboardEntryType.RECURRING_EVENT, DashboardEntryType.CELEBRATION_HIGHLIGHT):
                        ev = self.canonical.get_event(entry.ref_id)
                        if ev and self.auth.can_view_event(account_id, ev, context):
                            authorized_entries.append(entry)
                    elif entry.item_type == DashboardEntryType.DUE_REMINDER:
                        rem = self.canonical.get_reminder(entry.ref_id)
                        if rem:
                            if rem.event_id:
                                ev = self.canonical.get_event(rem.event_id)
                                if ev and self.auth.can_view_event(account_id, ev, context):
                                    authorized_entries.append(entry)
                            elif rem.created_by_id == account_id:
                                authorized_entries.append(entry)
                    elif entry.item_type == DashboardEntryType.RECENT_MEMORY:
                        mem = self.canonical.get_memory(entry.ref_id)
                        if mem and self.auth.can_view_memory(account_id, mem, context):
                            authorized_entries.append(entry)
                    elif entry.item_type == DashboardEntryType.ACTIVE_NOTIFICATION:
                        notif = self.canonical.get_notification(entry.ref_id)
                        if notif and notif.recipient_id == account_id:
                            authorized_entries.append(entry)
            else:
                authorized_entries.append(entry)
        return authorized_entries

    def rebuild_dashboard_projections(self, family_context_id: str) -> None:
        context = self.canonical.get_family_context(family_context_id)
        if context is None or not context.member_ids:
            self.derived.clear_dashboard_entries(family_context_id)
            return
        admin_id = context.member_ids[0]
        self.project_dashboard_entries(admin_id, family_context_id)


class CelebrationStudioService:
    def __init__(
        self,
        canonical: CanonicalRepository,
        derived: DerivedRepository,
        auth: AuthorizationService,
        media_service: Optional[MediaService] = None,
    ) -> None:
        self.canonical = canonical
        self.derived = derived
        self.auth = auth
        self.media_service = media_service

    def build_celebration_artifact_for_event(
        self,
        account_id: str,
        event_id: str,
        attach_as_media: bool = False,
    ) -> CelebrationArtifact:
        event = self.canonical.get_event(event_id)
        if event is None:
            raise ValueError("Event does not exist")
        context = self.canonical.get_family_context(event.family_context_id) if event.family_context_id else None
        if not self.auth.can_view_event(account_id, event, context):
            raise PermissionError("Account is not authorized to view this event")

        if event.category == EventCategory.BIRTHDAY:
            artifact_type = CelebrationArtifactType.BIRTHDAY_CARD
            title_prefix = "Birthday Celebration"
        elif event.category == EventCategory.ANNIVERSARY:
            artifact_type = CelebrationArtifactType.ANNIVERSARY_CARD
            title_prefix = "Anniversary Celebration"
        elif event.category == EventCategory.MILESTONE:
            artifact_type = CelebrationArtifactType.MILESTONE_CARD
            title_prefix = "Milestone Celebration"
        else:
            artifact_type = CelebrationArtifactType.EVENT_HIGHLIGHT
            title_prefix = "Event Highlight"

        target_names = []
        for pid in event.target_person_ids:
            p = self.canonical.get_person(pid)
            if p:
                target_names.append(p.name)
        target_str = f" for {', '.join(target_names)}" if target_names else ""
        milestone_str = f" ({event.milestone_year} Years)" if event.milestone_year is not None else ""

        title = f"{title_prefix}: {event.title}{milestone_str}"
        subtitle = f"{event.description}{target_str}".strip()
        rendered_content = f"[Celebration Card] {title} | {subtitle} | Date: {event.start_time.isoformat()}"
        content_hash = hashlib.sha256(rendered_content.encode("utf-8")).hexdigest()

        provenance = ProvenanceMetadata(
            source_type=ProvenanceSourceType.SYSTEM,
            source_id="celebration-studio",
            created_by_id=account_id,
            audit_trail=["celebration-artifact-generated"],
        )

        media_item_id = None
        if attach_as_media and self.media_service is not None:
            media_item = self.media_service.create_media_item(
                owner_id=account_id,
                uri=f"celebration://artifacts/{event.id}",
                media_type=MediaType.PHOTO,
                caption=title,
                family_context_id=event.family_context_id,
                event_id=event.id,
                visibility=event.visibility,
            )
            media_item_id = media_item.id

        artifact = CelebrationArtifact(
            artifact_type=artifact_type,
            title=title,
            subtitle=subtitle,
            rendered_content=rendered_content,
            content_hash=content_hash,
            family_context_id=event.family_context_id or "",
            source_event_id=event.id,
            source_person_id=event.target_person_ids[0] if event.target_person_ids else None,
            media_item_id=media_item_id,
            visibility=event.visibility,
            provenance=provenance,
        )

        return self.derived.add_celebration_artifact(artifact)

    def build_celebration_artifact_for_person(
        self,
        account_id: str,
        person_id: str,
        family_context_id: str,
        attach_as_media: bool = False,
    ) -> CelebrationArtifact:
        context = self.canonical.get_family_context(family_context_id)
        if context is None:
            raise ValueError("Family context does not exist")
        if account_id not in context.member_ids:
            raise PermissionError("Account is not authorized for this family context")

        person = self.canonical.get_person(person_id)
        if person is None:
            raise ValueError("Person does not exist")

        authorized_person_ids = set()
        for m_id in context.member_ids:
            acc = self.canonical.get_account(m_id)
            if acc and acc.person_id:
                authorized_person_ids.add(acc.person_id)

        if person_id not in authorized_person_ids:
            raise PermissionError("Requested person is not an authorized person in this family context")

        title = f"Person Celebration: {person.name}"
        birth_str = f"Born on {person.birth_date.isoformat()}" if person.birth_date else "Special Person"
        subtitle = f"Honoring {person.name} ({birth_str})"
        rendered_content = f"[Person Card] {title} | {subtitle}"
        content_hash = hashlib.sha256(rendered_content.encode("utf-8")).hexdigest()

        provenance = ProvenanceMetadata(
            source_type=ProvenanceSourceType.SYSTEM,
            source_id="celebration-studio",
            created_by_id=account_id,
            audit_trail=["person-celebration-artifact-generated"],
        )

        media_item_id = None
        if attach_as_media and self.media_service is not None:
            media_item = self.media_service.create_media_item(
                owner_id=account_id,
                uri=f"celebration://artifacts/person-{person.id}",
                media_type=MediaType.PHOTO,
                caption=title,
                family_context_id=family_context_id,
                visibility=VisibilityLevel.FAMILY,
            )
            media_item_id = media_item.id

        artifact = CelebrationArtifact(
            artifact_type=CelebrationArtifactType.BIRTHDAY_CARD if person.birth_date else CelebrationArtifactType.EVENT_HIGHLIGHT,
            title=title,
            subtitle=subtitle,
            rendered_content=rendered_content,
            content_hash=content_hash,
            family_context_id=family_context_id,
            source_person_id=person.id,
            media_item_id=media_item_id,
            visibility=VisibilityLevel.FAMILY,
            provenance=provenance,
        )

        return self.derived.add_celebration_artifact(artifact)

    def build_celebration_artifact_for_memory(
        self,
        account_id: str,
        memory_id: str,
        attach_as_media: bool = False,
    ) -> CelebrationArtifact:
        memory = self.canonical.get_memory(memory_id)
        if memory is None:
            raise ValueError("Memory does not exist")

        context = None
        if memory.event_id:
            ev = self.canonical.get_event(memory.event_id)
            if ev and ev.family_context_id:
                context = self.canonical.get_family_context(ev.family_context_id)
        if context is None:
            for fc in self.canonical.list_family_contexts():
                if memory.subject_id in fc.member_ids:
                    context = fc
                    break

        if not self.auth.can_view_memory(account_id, memory, context):
            raise PermissionError("Account is not authorized to view this memory")

        title = "Memory Keepsake"
        subtitle = memory.narrative[:50] + "..." if len(memory.narrative) > 50 else memory.narrative
        rendered_content = f"[Family Memory Card] {title} | Narrative: {memory.narrative}"
        content_hash = hashlib.sha256(rendered_content.encode("utf-8")).hexdigest()

        provenance = ProvenanceMetadata(
            source_type=ProvenanceSourceType.SYSTEM,
            source_id="celebration-studio",
            created_by_id=account_id,
            audit_trail=["memory-celebration-artifact-generated"],
        )

        fc_id = context.id if context else ""
        media_item_id = None
        if attach_as_media and self.media_service is not None:
            media_item = self.media_service.create_media_item(
                owner_id=account_id,
                uri=f"celebration://artifacts/memory-{memory.id}",
                media_type=MediaType.PHOTO,
                caption=title,
                family_context_id=fc_id if fc_id else None,
                memory_id=memory.id,
                visibility=memory.visibility,
            )
            media_item_id = media_item.id

        artifact = CelebrationArtifact(
            artifact_type=CelebrationArtifactType.FAMILY_MEMORY_CARD,
            title=title,
            subtitle=subtitle,
            rendered_content=rendered_content,
            content_hash=content_hash,
            family_context_id=fc_id,
            source_memory_id=memory.id,
            source_event_id=memory.event_id,
            media_item_id=media_item_id,
            visibility=memory.visibility,
            provenance=provenance,
        )

        return self.derived.add_celebration_artifact(artifact)

    def build_celebration_album_artifact(
        self,
        account_id: str,
        album_id: str,
        attach_as_media: bool = False,
    ) -> CelebrationArtifact:
        album = self.canonical.get_media_album(album_id)
        if album is None:
            raise ValueError("Media album does not exist")

        fc_id = album.family_context_id or ""
        context = self.canonical.get_family_context(fc_id) if fc_id else None
        if context and account_id not in context.member_ids:
            raise PermissionError("Account is not authorized for this family context")
        if not self.auth.can_view_media_album(account_id, album, context):
            raise PermissionError("Account is not authorized to view this media album")

        title = f"Celebration Album: {album.title}"
        subtitle = f"Album featuring {len(album.media_ids)} media item(s)"
        rendered_content = f"[Celebration Album] {title} | {subtitle}"
        content_hash = hashlib.sha256(rendered_content.encode("utf-8")).hexdigest()

        provenance = ProvenanceMetadata(
            source_type=ProvenanceSourceType.SYSTEM,
            source_id="celebration-studio",
            created_by_id=account_id,
            audit_trail=["celebration-album-artifact-generated"],
        )

        artifact = CelebrationArtifact(
            artifact_type=CelebrationArtifactType.CELEBRATION_ALBUM,
            title=title,
            subtitle=subtitle,
            rendered_content=rendered_content,
            content_hash=content_hash,
            family_context_id=fc_id,
            visibility=album.visibility,
            provenance=provenance,
        )

        return self.derived.add_celebration_artifact(artifact)

    def get_celebration_artifact_for_account(
        self,
        artifact_id: str,
        account_id: str,
    ) -> Optional[CelebrationArtifact]:
        artifact = self.derived.get_celebration_artifact_by_id(artifact_id)
        if artifact is None:
            return None
        context = self.canonical.get_family_context(artifact.family_context_id) if artifact.family_context_id else None

        if artifact.visibility == VisibilityLevel.PRIVATE:
            if artifact.provenance and artifact.provenance.created_by_id != account_id:
                raise PermissionError("Account is not authorized to view private celebration artifact")
        elif context and account_id not in context.member_ids:
            raise PermissionError("Account is not authorized to view celebration artifacts for this context")

        return artifact

    def list_celebration_artifacts_for_context_for_account(
        self,
        family_context_id: str,
        account_id: str,
    ) -> List[CelebrationArtifact]:
        context = self.canonical.get_family_context(family_context_id)
        if context is None:
            raise ValueError("Family context does not exist")
        if account_id not in context.member_ids:
            raise PermissionError("Account is not authorized for this family context")

        artifacts = self.derived.get_celebration_artifacts(family_context_id)
        authorized: List[CelebrationArtifact] = []
        for art in artifacts:
            if art.visibility == VisibilityLevel.PRIVATE:
                if art.provenance and art.provenance.created_by_id == account_id:
                    authorized.append(art)
            else:
                authorized.append(art)
        return authorized

    def rebuild_celebration_artifacts(self, family_context_id: str) -> List[CelebrationArtifact]:
        context = self.canonical.get_family_context(family_context_id)
        if context is None:
            return []

        self.derived.clear_celebration_artifacts(family_context_id)

        rebuilt: List[CelebrationArtifact] = []

        # 1. Event celebration artifacts
        context_event_ids = set()
        for ev in self.canonical.list_events():
            if ev.family_context_id == family_context_id:
                context_event_ids.add(ev.id)
                if ev.category in (EventCategory.BIRTHDAY, EventCategory.ANNIVERSARY, EventCategory.MILESTONE):
                    created_by = ev.provenance.created_by_id if ev.provenance else ev.owner_id
                    art = self.build_celebration_artifact_for_event(created_by, ev.id, attach_as_media=False)
                    rebuilt.append(art)

        # 2. Person celebration artifacts
        for m_id in context.member_ids:
            acc = self.canonical.get_account(m_id)
            if acc and acc.person_id:
                person = self.canonical.get_person(acc.person_id)
                if person:
                    art = self.build_celebration_artifact_for_person(m_id, person.id, family_context_id, attach_as_media=False)
                    rebuilt.append(art)

        # 3. Memory celebration artifacts
        for mem in self.canonical.list_memories():
            if (mem.event_id and mem.event_id in context_event_ids) or (mem.subject_id in context.member_ids):
                created_by = mem.provenance.created_by_id if mem.provenance else context.member_ids[0]
                art = self.build_celebration_artifact_for_memory(created_by, mem.id, attach_as_media=False)
                rebuilt.append(art)

        # 4. Media Album celebration artifacts
        for album in self.canonical.list_media_albums():
            if album.family_context_id == family_context_id:
                art = self.build_celebration_album_artifact(album.owner_id, album.id, attach_as_media=False)
                rebuilt.append(art)

        return rebuilt


class DataPortabilityService:
    def __init__(self, canonical: CanonicalRepository, derived: DerivedRepository, auth: AuthorizationService) -> None:
        self.canonical = canonical
        self.derived = derived
        self.auth = auth

    def export_family_context_for_account(self, account_id: str, family_context_id: str) -> DataExportResult:
        context = self.canonical.get_family_context(family_context_id)
        if context is None:
            raise ValueError("Family context does not exist")
        if account_id not in context.member_ids:
            raise PermissionError("Account is not authorized to export this family context")

        provenance = ProvenanceMetadata(
            source_type=ProvenanceSourceType.SYSTEM,
            source_id="femc-data-portability",
            created_by_id=account_id,
            audit_trail=["data-export-generated"],
        )

        records: Dict[str, List[Dict[str, Any]]] = {
            "family_contexts": [],
            "accounts": [],
            "persons": [],
            "relationships": [],
            "events": [],
            "memories": [],
            "places": [],
            "media_items": [],
            "media_albums": [],
            "notifications": [],
            "reminders": [],
            "share_links": [],
            "action_proposals": [],
            "repair_proposals": [],
            "insight_analyses": [],
            "transactions": [],
        }


        created_by = context.provenance.created_by_id if context.provenance else ""
        records["family_contexts"].append({
            "id": context.id,
            "name": context.name,
            "member_ids": list(context.member_ids),
            "created_by_id": created_by,
            "created_at": context.created_at.isoformat(),
        })

        for member_id in context.member_ids:
            acc = self.canonical.get_account(member_id)
            if acc:
                records["accounts"].append({
                    "id": acc.id,
                    "username": acc.username,
                    "email": acc.email,
                    "person_id": acc.person_id,
                    "created_at": acc.created_at.isoformat(),
                })
                person = self.canonical.get_person(acc.person_id)
                if person and not any(p["id"] == person.id for p in records["persons"]):
                    records["persons"].append({
                        "id": person.id,
                        "name": person.name,
                        "birth_date": person.birth_date.isoformat() if person.birth_date else None,
                    })

        context_person_ids = {p["id"] for p in records["persons"]}
        for rel in self.canonical.list_relationships():
            if rel.source_person_id in context_person_ids and rel.target_person_id in context_person_ids:
                rel_type = rel.relationship_type.value if hasattr(rel.relationship_type, "value") else str(rel.relationship_type)
                records["relationships"].append({
                    "id": rel.id,
                    "source_person_id": rel.source_person_id,
                    "target_person_id": rel.target_person_id,
                    "relationship_type": rel_type,
                })

        for ev in self.canonical.list_events():
            if ev.family_context_id == family_context_id and self.auth.can_view_event(account_id, ev, context):
                ev_status = ev.status.value if hasattr(ev.status, "value") else str(ev.status)
                ev_vis = ev.visibility.value if hasattr(ev.visibility, "value") else str(ev.visibility)
                rec_dict = None
                if ev.recurrence_rule:
                    r_freq = ev.recurrence_rule.frequency.value if hasattr(ev.recurrence_rule.frequency, "value") else str(ev.recurrence_rule.frequency)
                    rec_dict = {
                        "frequency": r_freq,
                        "interval": ev.recurrence_rule.interval,
                        "until_date": ev.recurrence_rule.until_date.isoformat() if ev.recurrence_rule.until_date else None,
                    }
                records["events"].append({
                    "id": ev.id,
                    "title": ev.title,
                    "description": ev.description,
                    "owner_id": ev.owner_id,
                    "family_context_id": ev.family_context_id,
                    "place_id": ev.place_id,
                    "start_time": ev.start_time.isoformat() if ev.start_time else None,
                    "end_time": ev.end_time.isoformat() if ev.end_time else None,
                    "status": ev_status,
                    "visibility": ev_vis,
                    "recurrence_rule": rec_dict,
                })

        for mem in self.canonical.list_memories():
            if self.auth.can_view_memory(account_id, mem, context):
                in_context = False
                if mem.event_id and any(e["id"] == mem.event_id for e in records["events"]):
                    in_context = True
                elif mem.subject_id in context.member_ids:
                    in_context = True

                if in_context:
                    mem_vis = mem.visibility.value if hasattr(mem.visibility, "value") else str(mem.visibility)
                    records["memories"].append({
                        "id": mem.id,
                        "event_id": mem.event_id,
                        "subject_id": mem.subject_id,
                        "narrative": mem.narrative,
                        "recorded_at": mem.recorded_at.isoformat() if mem.recorded_at else None,
                        "visibility": mem_vis,
                    })

        for plc in self.canonical.list_places():
            if plc.family_context_id == family_context_id and self.auth.can_view_place(account_id, plc, context):
                plc_vis = plc.visibility.value if hasattr(plc.visibility, "value") else str(plc.visibility)
                records["places"].append({
                    "id": plc.id,
                    "name": plc.name,
                    "address": plc.address,
                    "family_context_id": plc.family_context_id,
                    "visibility": plc_vis,
                })

        for item in self.canonical.list_media_items():
            if item.family_context_id == family_context_id and self.auth.can_view_media_item(account_id, item, context):
                m_type = item.media_type.value if hasattr(item.media_type, "value") else str(item.media_type)
                m_vis = item.visibility.value if hasattr(item.visibility, "value") else str(item.visibility)
                records["media_items"].append({
                    "id": item.id,
                    "uri": item.uri,
                    "media_type": m_type,
                    "caption": item.caption,
                    "owner_id": item.owner_id,
                    "family_context_id": item.family_context_id,
                    "event_id": item.event_id,
                    "memory_id": item.memory_id,
                    "visibility": m_vis,
                })

        for album in self.canonical.list_media_albums():
            if album.family_context_id == family_context_id and self.auth.can_view_media_album(account_id, album, context):
                al_vis = album.visibility.value if hasattr(album.visibility, "value") else str(album.visibility)
                records["media_albums"].append({
                    "id": album.id,
                    "title": album.title,
                    "description": album.description,
                    "owner_id": album.owner_id,
                    "family_context_id": album.family_context_id,
                    "media_ids": list(album.media_ids),
                    "visibility": al_vis,
                })

        for notif in self.canonical.list_notifications():
            if notif.recipient_id == account_id and notif.family_context_id == family_context_id:
                n_type = notif.notification_type.value if hasattr(notif.notification_type, "value") else str(notif.notification_type)
                n_status = notif.status.value if hasattr(notif.status, "value") else str(notif.status)
                records["notifications"].append({
                    "id": notif.id,
                    "recipient_id": notif.recipient_id,
                    "sender_id": notif.sender_id,
                    "notification_type": n_type,
                    "title": notif.title,
                    "message": notif.message,
                    "status": n_status,
                })

        for reminder in self.canonical.list_reminders():
            if reminder.family_context_id == family_context_id and reminder.created_by_id == account_id:
                r_type = reminder.reminder_type.value if hasattr(reminder.reminder_type, "value") else str(reminder.reminder_type)
                r_status = reminder.status.value if hasattr(reminder.status, "value") else str(reminder.status)
                records["reminders"].append({
                    "id": reminder.id,
                    "event_id": reminder.event_id,
                    "family_context_id": reminder.family_context_id,
                    "offset_minutes": reminder.offset_minutes,
                    "reminder_type": r_type,
                    "status": r_status,
                    "last_triggered_at": reminder.last_triggered_at.isoformat() if reminder.last_triggered_at else None,
                })


        for link in self.canonical.list_share_links():
            if link.family_context_id == family_context_id and link.created_by_id == account_id:
                res_type = link.resource_type.value if hasattr(link.resource_type, "value") else str(link.resource_type)
                records["share_links"].append({
                    "id": link.id,
                    "token": link.token,
                    "resource_type": res_type,
                    "resource_id": link.resource_id,
                    "is_revoked": link.is_revoked,
                })

        for prop in self.canonical.list_action_proposals():
            if prop.family_context_id == family_context_id and prop.target_account_id == account_id:
                p_status = prop.status.value if hasattr(prop.status, "value") else str(prop.status)
                p_type = prop.proposal_type.value if hasattr(prop.proposal_type, "value") else str(prop.proposal_type)
                records["action_proposals"].append({
                    "id": prop.id,
                    "proposal_type": p_type,
                    "title": prop.title,
                    "reasoning": prop.reasoning,
                    "target_account_id": prop.target_account_id,
                    "status": p_status,
                })

        for insight in self.canonical.list_insight_analyses():
            if insight.family_context_id == family_context_id and (insight.provenance is None or insight.provenance.created_by_id == account_id):
                records["insight_analyses"].append({
                    "id": insight.id,
                    "title": insight.title,
                    "analysis_summary": insight.analysis_summary,
                })

        records["repair_proposals"] = []
        for r_prop in self.canonical.list_repair_proposals():
            if r_prop.family_context_id == family_context_id:
                c_val = r_prop.classification.value if hasattr(r_prop.classification, "value") else str(r_prop.classification)
                records["repair_proposals"].append({
                    "id": r_prop.id,
                    "anomaly_id": r_prop.anomaly_id,
                    "proposed_repair_action": r_prop.proposed_repair_action,
                    "target_entity_type": r_prop.target_entity_type,
                    "target_entity_id": r_prop.target_entity_id,
                    "classification": c_val,
                    "requires_human_approval": r_prop.requires_human_approval,
                    "is_executed": r_prop.is_executed,
                })

        if hasattr(self, "transaction_service") and self.transaction_service:
            tx_history = self.transaction_service.get_transaction_history_for_session(account_id, family_context_id, limit=200)
            for tx in tx_history:
                records["transactions"].append({
                    "transaction_id": tx.transaction_id,
                    "timestamp": tx.timestamp.isoformat(),
                    "actor_account_id": tx.actor_account_id,
                    "action_type": tx.action_type.value if hasattr(tx.action_type, "value") else str(tx.action_type),
                    "resource_type": tx.resource_type.value if hasattr(tx.resource_type, "value") else str(tx.resource_type),
                    "resource_id": tx.resource_id,
                    "resource_label_snapshot": tx.resource_label_snapshot,
                    "operation": tx.operation,
                    "visibility": tx.visibility.value if hasattr(tx.visibility, "value") else str(tx.visibility),
                })

        return DataExportResult(
            family_context_id=family_context_id,
            provenance=provenance,
            records=records,
        )




    def validate_data_export(self, payload: Dict[str, Any]) -> ExportValidationResult:
        errors: List[str] = []
        warnings: List[str] = []
        counts: Dict[str, int] = {}

        if not isinstance(payload, dict):
            return ExportValidationResult(is_valid=False, errors=["Payload must be a JSON object"])

        if payload.get("schema_version") != "1.0":
            errors.append(f"Unsupported or missing schema_version: {payload.get('schema_version')}")

        if not payload.get("export_id"):
            errors.append("Missing required export_id")

        if not payload.get("family_context_id"):
            errors.append("Missing required family_context_id")

        provenance_data = payload.get("provenance")
        if not provenance_data or not isinstance(provenance_data, dict):
            errors.append("Missing or invalid provenance metadata")

        records = payload.get("records")
        if not isinstance(records, dict):
            errors.append("Missing or invalid records dictionary")
        else:
            for category, items in records.items():
                if not isinstance(items, list):
                    errors.append(f"Record category '{category}' must be a list")
                else:
                    counts[category] = len(items)
                    for item in items:
                        if not isinstance(item, dict) or "id" not in item:
                            errors.append(f"Malformed record in category '{category}': missing 'id'")

        is_valid = len(errors) == 0
        return ExportValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            record_counts=counts,
        )


class MayilService:
    def __init__(
        self,
        canonical: CanonicalRepository,
        derived: DerivedRepository,
        auth: AuthorizationService,
        event_service: EventService,
    ) -> None:
        self.canonical = canonical
        self.derived = derived
        self.auth = auth
        self.event_service = event_service

    def generate_insights(self, account_id: str, family_context_id: str) -> InsightAnalysis:
        context = self.canonical.get_family_context(family_context_id)
        if context is None:
            raise ValueError("Family context does not exist")
        if account_id not in context.member_ids:
            raise PermissionError("Account is not authorized for this family context")

        # Mayil READS data authorized for the account
        visible_events = [ev for ev in self.canonical.list_events() if ev.family_context_id == family_context_id and self.auth.can_view_event(account_id, ev, context)]
        visible_memories = [m for m in self.canonical.list_memories() if self.auth.can_view_memory(account_id, m, context)]
        visible_places = [p for p in self.canonical.list_places() if p.family_context_id == family_context_id and self.auth.can_view_place(account_id, p, context)]

        summary = f"Analyzed {len(visible_events)} events, {len(visible_memories)} memories, and {len(visible_places)} places for context '{context.name}'."

        provenance = ProvenanceMetadata(
            source_type=ProvenanceSourceType.SYSTEM,
            source_id="mayil-ai-engine",
            created_by_id=account_id,
            audit_trail=["mayil-analysis-generated"],
        )

        analysis = InsightAnalysis(
            title=f"Mayil Intelligence Summary: {context.name}",
            analysis_summary=summary,
            family_context_id=family_context_id,
            confidence=Confidence.HIGH,
            provenance=provenance,
        )

        return self.canonical.add_insight_analysis(analysis)

    def propose_event_recommendation(
        self,
        account_id: str,
        family_context_id: str,
        title: str,
        description: str,
        start_time: Optional[datetime.datetime] = None,
    ) -> ActionProposal:
        context = self.canonical.get_family_context(family_context_id)
        if context is None:
            raise ValueError("Family context does not exist")
        if account_id not in context.member_ids:
            raise PermissionError("Account is not authorized for this family context")

        provenance = ProvenanceMetadata(
            source_type=ProvenanceSourceType.SYSTEM,
            source_id="mayil-ai-engine",
            created_by_id=account_id,
            audit_trail=["proposal-created"],
        )

        st_str = start_time.isoformat() if start_time else (_utc_now() + datetime.timedelta(days=1)).isoformat()

        proposed_changes = {
            "title": title,
            "description": description,
            "family_context_id": family_context_id,
            "start_time": st_str,
        }

        proposal = ActionProposal(
            proposal_type=ProposalType.EVENT_RECOMMENDATION,
            title=f"Recommended Event: {title}",
            reasoning=f"Mayil AI recommends scheduling '{title}' based on family activity analysis.",
            proposed_changes=proposed_changes,
            confidence=Confidence.HIGH,
            family_context_id=family_context_id,
            target_account_id=account_id,
            status=ProposalStatus.PROPOSED,
            provenance=provenance,
        )

        return self.canonical.add_action_proposal(proposal)

    def list_proposals_for_account(self, account_id: str, family_context_id: str) -> List[ActionProposal]:
        context = self.canonical.get_family_context(family_context_id)
        if context is None:
            raise ValueError("Family context does not exist")
        if account_id not in context.member_ids:
            raise PermissionError("Account is not authorized for this family context")

        return [
            prop for prop in self.canonical.list_action_proposals()
            if prop.family_context_id == family_context_id and prop.target_account_id == account_id
        ]

    def approve_action_proposal(self, account_id: str, proposal_id: str) -> ActionProposal:
        proposal = self.canonical.get_action_proposal(proposal_id)
        if proposal is None:
            raise ValueError("Action proposal not found")

        if proposal.target_account_id != account_id:
            raise PermissionError("Only target account can approve this proposal")

        if proposal.status != ProposalStatus.PROPOSED:
            raise ValueError(f"Proposal cannot be approved in state '{proposal.status}'")

        context = self.canonical.get_family_context(proposal.family_context_id)
        if context is None or account_id not in context.member_ids:
            raise PermissionError("Account is not authorized for this family context")

        # Mark APPROVED
        proposal.status = ProposalStatus.APPROVED

        try:
            # Execute proposed action ONLY through existing domain services
            if proposal.proposal_type == ProposalType.EVENT_RECOMMENDATION:
                changes = proposal.proposed_changes
                title = changes.get("title", "Proposed Event")
                desc = changes.get("description", "")
                fc_id = changes.get("family_context_id")
                st_raw = changes.get("start_time")
                st = datetime.datetime.fromisoformat(st_raw) if st_raw else _utc_now()

                self.event_service.create_event(
                    owner_id=account_id,
                    title=title,
                    description=desc,
                    family_context_id=fc_id,
                    start_time=st,
                    end_time=None,
                )
            else:
                raise ValueError(f"Unsupported proposal type for execution: {proposal.proposal_type}")
        except Exception:
            proposal.status = ProposalStatus.PROPOSED
            raise

        # Mark EXECUTED
        proposal.status = ProposalStatus.EXECUTED


        if proposal.provenance and proposal.provenance.audit_trail is not None:
            proposal.provenance.audit_trail.append(f"approved-from-mayil-proposal:{proposal.id}")

        return proposal

    def reject_action_proposal(self, account_id: str, proposal_id: str) -> ActionProposal:
        proposal = self.canonical.get_action_proposal(proposal_id)
        if proposal is None:
            raise ValueError("Action proposal not found")

        if proposal.target_account_id != account_id:
            raise PermissionError("Only target account can reject this proposal")

        if proposal.status != ProposalStatus.PROPOSED:
            raise ValueError(f"Proposal cannot be rejected in state '{proposal.status}'")

        # Mark REJECTED without mutating any canonical domain data
        proposal.status = ProposalStatus.REJECTED

        if proposal.provenance and proposal.provenance.audit_trail is not None:
            proposal.provenance.audit_trail.append(f"rejected-from-mayil-proposal:{proposal.id}")

        return proposal

    def propose_celebration_artifact_recommendation(
        self,
        account_id: str,
        family_context_id: str,
        event_id: str,
        reasoning: str = "Upcoming landmark celebration event detected",
    ) -> ActionProposal:
        context = self.canonical.get_family_context(family_context_id)
        if context is None:
            raise ValueError("Family context does not exist")
        if account_id not in context.member_ids:
            raise PermissionError("Account is not authorized for this family context")

        event = self.canonical.get_event(event_id)
        if event is None or event.family_context_id != family_context_id:
            raise ValueError("Referenced event does not exist in context")

        provenance = ProvenanceMetadata(
            source_type=ProvenanceSourceType.SYSTEM,
            source_id="mayil-ai-engine",
            created_by_id=account_id,
            audit_trail=["mayil-celebration-proposal-generated"],
        )

        proposal = ActionProposal(
            proposal_type=ProposalType.EVENT_RECOMMENDATION,
            title=f"Celebration Artifact Proposal for {event.title}",
            reasoning=reasoning,
            proposed_changes={"action": "build_celebration_artifact", "event_id": event_id},
            confidence=Confidence.HIGH,
            family_context_id=family_context_id,
            target_account_id=account_id,
            status=ProposalStatus.PROPOSED,
            provenance=provenance,
        )

        return self.canonical.add_action_proposal(proposal)


class VelGuardianService:
    def __init__(
        self,
        canonical: CanonicalRepository,
        derived: DerivedRepository,
        auth: AuthorizationService,
        calendar_service: CalendarService,
        timeline_service: TimelineService,
        dashboard_service: Optional[DashboardService] = None,
        celebration_studio_service: Optional[CelebrationStudioService] = None,
    ) -> None:
        self.canonical = canonical
        self.derived = derived
        self.auth = auth
        self.calendar_service = calendar_service
        self.timeline_service = timeline_service
        self.dashboard_service = dashboard_service
        self.celebration_studio_service = celebration_studio_service

    def run_integrity_audit(self, account_id: str, family_context_id: str) -> ValidationReport:
        context = self.canonical.get_family_context(family_context_id)
        if context is None:
            raise ValueError("Family context does not exist")
        if account_id not in context.member_ids:
            raise PermissionError("Account is not authorized for this family context")

        anomalies: List[AuditAnomaly] = []
        inspected_count = 0

        # Gather context canonical entities
        context_events = [e for e in self.canonical.list_events() if e.family_context_id == family_context_id]
        context_places = [p for p in self.canonical.list_places() if p.family_context_id == family_context_id]
        context_memories = [m for m in self.canonical.list_memories() if self._memory_in_context(m, family_context_id, context.member_ids)]
        context_media_items = [m for m in self.canonical.list_media_items() if m.family_context_id == family_context_id]
        context_media_albums = [a for a in self.canonical.list_media_albums() if a.family_context_id == family_context_id]
        context_notifications = [n for n in self.canonical.list_notifications() if n.family_context_id == family_context_id]
        context_share_links = [s for s in self.canonical.list_share_links() if s.family_context_id == family_context_id]
        context_proposals = [p for p in self.canonical.list_action_proposals() if p.family_context_id == family_context_id]
        relationships = self.canonical.list_relationships()

        all_place_ids = {p.id for p in self.canonical.list_places()}
        all_event_ids = {e.id for e in self.canonical.list_events()}
        all_memory_ids = {m.id for m in self.canonical.list_memories()}
        all_media_item_ids = {m.id for m in self.canonical.list_media_items()}
        all_account_ids = {a.id for a in self.canonical.list_accounts()}
        all_person_ids = {p.id for p in self.canonical.list_persons()}

        inspected_count += (
            len(context_events)
            + len(context_places)
            + len(context_memories)
            + len(context_media_items)
            + len(context_media_albums)
            + len(context_notifications)
            + len(context_share_links)
            + len(context_proposals)
            + len(relationships)
        )

        # 1. Reference Relationship Integrity Checks
        for member_id in context.member_ids:
            if member_id not in all_account_ids:
                prop = self._create_repair_proposal("dangling_member_account", "FamilyContext", context.id, family_context_id, classification=RepairClassification.CANONICAL_REPAIR)
                anomalies.append(AuditAnomaly(
                    anomaly_type=AnomalyType.DANGLING_REFERENCE,
                    severity=AnomalySeverity.CRITICAL,
                    description=f"FamilyContext '{context.id}' references non-existent member account '{member_id}'",
                    affected_entity_id=context.id,
                    family_context_id=family_context_id,
                    repair_proposal=prop,
                ))

        for ev in context_events:
            if ev.place_id and ev.place_id not in all_place_ids:
                prop = self._create_repair_proposal("dangling_place_id", "Event", ev.id, family_context_id, classification=RepairClassification.CANONICAL_REPAIR)
                anomalies.append(AuditAnomaly(
                    anomaly_type=AnomalyType.DANGLING_REFERENCE,
                    severity=AnomalySeverity.WARNING,
                    description=f"Event '{ev.title}' references non-existent place_id '{ev.place_id}'",
                    affected_entity_id=ev.id,
                    family_context_id=family_context_id,
                    repair_proposal=prop,
                ))

        for mem in context_memories:
            if mem.event_id and mem.event_id not in all_event_ids:
                prop = self._create_repair_proposal("dangling_event_id", "Memory", mem.id, family_context_id, classification=RepairClassification.CANONICAL_REPAIR)
                anomalies.append(AuditAnomaly(
                    anomaly_type=AnomalyType.DANGLING_REFERENCE,
                    severity=AnomalySeverity.WARNING,
                    description=f"Memory '{mem.id}' references non-existent event_id '{mem.event_id}'",
                    affected_entity_id=mem.id,
                    family_context_id=family_context_id,
                    repair_proposal=prop,
                ))

        for item in context_media_items:
            if item.event_id and item.event_id not in all_event_ids:
                prop = self._create_repair_proposal("dangling_event_id", "MediaItem", item.id, family_context_id, classification=RepairClassification.CANONICAL_REPAIR)
                anomalies.append(AuditAnomaly(
                    anomaly_type=AnomalyType.DANGLING_REFERENCE,
                    severity=AnomalySeverity.WARNING,
                    description=f"MediaItem '{item.id}' references non-existent event_id '{item.event_id}'",
                    affected_entity_id=item.id,
                    family_context_id=family_context_id,
                    repair_proposal=prop,
                ))
            if item.memory_id and item.memory_id not in all_memory_ids:
                prop = self._create_repair_proposal("dangling_memory_id", "MediaItem", item.id, family_context_id, classification=RepairClassification.CANONICAL_REPAIR)
                anomalies.append(AuditAnomaly(
                    anomaly_type=AnomalyType.DANGLING_REFERENCE,
                    severity=AnomalySeverity.WARNING,
                    description=f"MediaItem '{item.id}' references non-existent memory_id '{item.memory_id}'",
                    affected_entity_id=item.id,
                    family_context_id=family_context_id,
                    repair_proposal=prop,
                ))

        for album in context_media_albums:
            for mid in album.media_ids:
                if mid not in all_media_item_ids:
                    prop = self._create_repair_proposal("dangling_media_id_in_album", "MediaAlbum", album.id, family_context_id, classification=RepairClassification.CANONICAL_REPAIR)
                    anomalies.append(AuditAnomaly(
                        anomaly_type=AnomalyType.DANGLING_REFERENCE,
                        severity=AnomalySeverity.WARNING,
                        description=f"MediaAlbum '{album.title}' references non-existent media_id '{mid}'",
                        affected_entity_id=album.id,
                        family_context_id=family_context_id,
                        repair_proposal=prop,
                    ))

        for notif in context_notifications:
            if notif.target_resource_id:
                if not self._target_resource_exists(notif.target_resource_id):
                    prop = self._create_repair_proposal("dangling_notification_resource", "Notification", notif.id, family_context_id, classification=RepairClassification.CANONICAL_REPAIR)
                    anomalies.append(AuditAnomaly(
                        anomaly_type=AnomalyType.DANGLING_REFERENCE,
                        severity=AnomalySeverity.WARNING,
                        description=f"Notification '{notif.id}' references non-existent target resource '{notif.target_resource_id}'",
                        affected_entity_id=notif.id,
                        family_context_id=family_context_id,
                        repair_proposal=prop,
                    ))

        for link in context_share_links:
            if not self._target_resource_exists(link.resource_id):
                prop = self._create_repair_proposal("dangling_share_link_resource", "ShareLink", link.id, family_context_id, classification=RepairClassification.CANONICAL_REPAIR)
                anomalies.append(AuditAnomaly(
                    anomaly_type=AnomalyType.DANGLING_REFERENCE,
                    severity=AnomalySeverity.CRITICAL,
                    description=f"ShareLink '{link.token}' references non-existent target resource '{link.resource_id}'",
                    affected_entity_id=link.id,
                    family_context_id=family_context_id,
                    repair_proposal=prop,
                ))

        # 2. Topology Consistency Checks
        context_person_ids = {acc.person_id for acc in [self.canonical.get_account(m) for m in context.member_ids] if acc}
        for rel in relationships:
            if rel.source_person_id in context_person_ids or rel.target_person_id in context_person_ids:
                if rel.source_person_id == rel.target_person_id:
                    prop = self._create_repair_proposal("fix_self_relationship", "Relationship", rel.id, family_context_id, classification=RepairClassification.CANONICAL_REPAIR)
                    anomalies.append(AuditAnomaly(
                        anomaly_type=AnomalyType.TOPOLOGY_INCONSISTENCY,
                        severity=AnomalySeverity.WARNING,
                        description=f"Relationship '{rel.id}' has identical source and target person ID '{rel.source_person_id}'",
                        affected_entity_id=rel.id,
                        family_context_id=family_context_id,
                        repair_proposal=prop,
                    ))
                elif rel.source_person_id not in all_person_ids or rel.target_person_id not in all_person_ids:
                    prop = self._create_repair_proposal("fix_unresolved_relationship", "Relationship", rel.id, family_context_id, classification=RepairClassification.CANONICAL_REPAIR)
                    anomalies.append(AuditAnomaly(
                        anomaly_type=AnomalyType.TOPOLOGY_INCONSISTENCY,
                        severity=AnomalySeverity.WARNING,
                        description=f"Relationship '{rel.id}' references non-existent person ID",
                        affected_entity_id=rel.id,
                        family_context_id=family_context_id,
                        repair_proposal=prop,
                    ))

        # 3. Projection Consistency Checks
        cal_entries = {c.event_id: c for c in self.derived.get_calendar_entries(family_context_id)}
        for ev in context_events:
            if ev.id not in cal_entries:
                prop = self._create_repair_proposal("rebuild_derived_projections", "CalendarProjection", ev.id, family_context_id, classification=RepairClassification.DERIVED_ONLY)
                anomalies.append(AuditAnomaly(
                    anomaly_type=AnomalyType.PROJECTION_DESYNC,
                    severity=AnomalySeverity.WARNING,
                    description=f"Event '{ev.title}' missing from calendar projection",
                    affected_entity_id=ev.id,
                    family_context_id=family_context_id,
                    repair_proposal=prop,
                ))
            else:
                c_entry = cal_entries[ev.id]
                if c_entry.title != ev.title or c_entry.visibility != ev.visibility or c_entry.status != ev.status:
                    prop = self._create_repair_proposal("rebuild_derived_projections", "CalendarProjection", ev.id, family_context_id, classification=RepairClassification.DERIVED_ONLY)
                    anomalies.append(AuditAnomaly(
                        anomaly_type=AnomalyType.PROJECTION_DESYNC,
                        severity=AnomalySeverity.WARNING,
                        description=f"Calendar projection entry for event '{ev.id}' desynced from canonical record",
                        affected_entity_id=ev.id,
                        family_context_id=family_context_id,
                        repair_proposal=prop,
                    ))

        timeline_entries = {t.ref_id: t for t in self.derived.get_timeline_entries(family_context_id)}
        for ev in context_events:
            if ev.id not in timeline_entries:
                prop = self._create_repair_proposal("rebuild_derived_projections", "TimelineProjection", ev.id, family_context_id, classification=RepairClassification.DERIVED_ONLY)
                anomalies.append(AuditAnomaly(
                    anomaly_type=AnomalyType.PROJECTION_DESYNC,
                    severity=AnomalySeverity.WARNING,
                    description=f"Event '{ev.title}' missing from timeline projection",
                    affected_entity_id=ev.id,
                    family_context_id=family_context_id,
                    repair_proposal=prop,
                ))

        # 4. Privacy Invariant Checks
        for ev in context_events:
            if ev.visibility == VisibilityLevel.PRIVATE:
                for link in context_share_links:
                    if link.resource_id == ev.id and not link.is_revoked:
                        prop = self._create_repair_proposal("revoke_privacy_violating_share_link", "ShareLink", link.id, family_context_id, classification=RepairClassification.CANONICAL_REPAIR)
                        anomalies.append(AuditAnomaly(
                            anomaly_type=AnomalyType.PRIVACY_INVARIANT_VIOLATION,
                            severity=AnomalySeverity.CRITICAL,
                            description=f"Private event '{ev.id}' is exposed via active share link token '{link.token}'",
                            affected_entity_id=ev.id,
                            family_context_id=family_context_id,
                            repair_proposal=prop,
                        ))
                if ev.id in cal_entries and cal_entries[ev.id].visibility == VisibilityLevel.PUBLIC:
                    prop = self._create_repair_proposal("rebuild_derived_projections", "CalendarProjection", ev.id, family_context_id, classification=RepairClassification.DERIVED_ONLY)
                    anomalies.append(AuditAnomaly(
                        anomaly_type=AnomalyType.PRIVACY_INVARIANT_VIOLATION,
                        severity=AnomalySeverity.CRITICAL,
                        description=f"Private event '{ev.id}' exposed as PUBLIC in calendar projection",
                        affected_entity_id=ev.id,
                        family_context_id=family_context_id,
                        repair_proposal=prop,
                    ))

        context_reminders = [r for r in self.canonical.list_reminders() if r.family_context_id == family_context_id]

        for reminder in context_reminders:
            if reminder.event_id not in all_event_ids:
                prop = self._create_repair_proposal("dangling_event_id_in_reminder", "ReminderConfig", reminder.id, family_context_id, classification=RepairClassification.CANONICAL_REPAIR)
                anomalies.append(AuditAnomaly(
                    anomaly_type=AnomalyType.DANGLING_REFERENCE,
                    severity=AnomalySeverity.WARNING,
                    description=f"ReminderConfig '{reminder.id}' references non-existent event_id '{reminder.event_id}'",
                    affected_entity_id=reminder.id,
                    family_context_id=family_context_id,
                    repair_proposal=prop,
                ))
            if reminder.status == ReminderStatus.TRIGGERED and reminder.last_triggered_at is None:
                prop = self._create_repair_proposal("inconsistent_reminder_trigger_state", "ReminderConfig", reminder.id, family_context_id, classification=RepairClassification.CANONICAL_REPAIR)
                anomalies.append(AuditAnomaly(
                    anomaly_type=AnomalyType.TOPOLOGY_INCONSISTENCY,
                    severity=AnomalySeverity.WARNING,
                    description=f"ReminderConfig '{reminder.id}' marked TRIGGERED but last_triggered_at is None",
                    affected_entity_id=reminder.id,
                    family_context_id=family_context_id,
                    repair_proposal=prop,
                ))

        for ev in context_events:
            if ev.recurrence_rule:
                rule = ev.recurrence_rule
                if rule.interval <= 0 or (rule.until_date and rule.until_date < ev.start_time.date()):
                    prop = self._create_repair_proposal("invalid_recurrence_rule", "Event", ev.id, family_context_id, classification=RepairClassification.CANONICAL_REPAIR)
                    anomalies.append(AuditAnomaly(
                        anomaly_type=AnomalyType.TOPOLOGY_INCONSISTENCY,
                        severity=AnomalySeverity.CRITICAL,
                        description=f"Event '{ev.id}' has invalid recurrence rule (interval={rule.interval}, until_date={rule.until_date})",
                        affected_entity_id=ev.id,
                        family_context_id=family_context_id,
                        repair_proposal=prop,
                    ))

        # 5. Missing Provenance Checks
        for entity, entity_type in [
            *[(e, "Event") for e in context_events],
            *[(m, "Memory") for m in context_memories],
            *[(p, "Place") for p in context_places],
            *[(mi, "MediaItem") for mi in context_media_items],
            *[(ma, "MediaAlbum") for ma in context_media_albums],
            *[(n, "Notification") for n in context_notifications],
            *[(sl, "ShareLink") for sl in context_share_links],
            *[(rem, "ReminderConfig") for rem in context_reminders],
        ]:
            if entity.provenance is None:
                prop = self._create_repair_proposal("add_provenance", entity_type, entity.id, family_context_id, classification=RepairClassification.CANONICAL_REPAIR)
                anomalies.append(AuditAnomaly(
                    anomaly_type=AnomalyType.PROVENANCE_MISSING,
                    severity=AnomalySeverity.CRITICAL,
                    description=f"{entity_type} '{entity.id}' missing required provenance metadata",
                    affected_entity_id=entity.id,
                    family_context_id=family_context_id,
                    repair_proposal=prop,
                ))


        for art in self.derived.get_celebration_artifacts(family_context_id):
            if art.source_event_id and art.source_event_id not in all_event_ids:
                prop = self._create_repair_proposal("rebuild_derived_projections", "CelebrationArtifact", art.id, family_context_id, classification=RepairClassification.DERIVED_ONLY)
                anomalies.append(AuditAnomaly(
                    anomaly_type=AnomalyType.DANGLING_REFERENCE,
                    severity=AnomalySeverity.WARNING,
                    description=f"CelebrationArtifact '{art.id}' references non-existent source_event_id '{art.source_event_id}'",
                    affected_entity_id=art.id,
                    family_context_id=family_context_id,
                    repair_proposal=prop,
                ))

        is_valid = len(anomalies) == 0
        return ValidationReport(
            is_valid=is_valid,
            checked_at=_utc_now(),
            total_entities_inspected=inspected_count,
            anomalies=anomalies,
        )

    def _memory_in_context(self, memory: Memory, family_context_id: str, member_ids: List[str]) -> bool:
        if memory.event_id:
            ev = self.canonical.get_event(memory.event_id)
            if ev and ev.family_context_id == family_context_id:
                return True
        return memory.subject_id in member_ids

    def _target_resource_exists(self, resource_id: str) -> bool:
        return (
            self.canonical.get_event(resource_id) is not None
            or self.canonical.get_memory(resource_id) is not None
            or self.canonical.get_media_item(resource_id) is not None
            or self.canonical.get_media_album(resource_id) is not None
            or self.canonical.get_place(resource_id) is not None
        )

    def _create_repair_proposal(
        self,
        action: str,
        entity_type: str,
        entity_id: str,
        family_context_id: str,
        classification: RepairClassification = RepairClassification.DERIVED_ONLY,
    ) -> RepairProposal:
        provenance = ProvenanceMetadata(
            source_type=ProvenanceSourceType.SYSTEM,
            source_id="vel-guardian-engine",
            created_by_id="vel-guardian",
            audit_trail=["vel-integrity-audit", "repair-proposed"],
        )
        requires_human_approval = (classification == RepairClassification.CANONICAL_REPAIR)
        prop = RepairProposal(
            proposed_repair_action=action,
            target_entity_type=entity_type,
            target_entity_id=entity_id,
            family_context_id=family_context_id,
            classification=classification,
            requires_human_approval=requires_human_approval,
            is_executed=False,
            provenance=provenance,
        )
        return self.canonical.add_repair_proposal(prop)

    def get_repair_proposals(self, account_id: str, family_context_id: str) -> List[RepairProposal]:
        context = self.canonical.get_family_context(family_context_id)
        if context is None:
            raise ValueError("Family context does not exist")
        if account_id not in context.member_ids:
            raise PermissionError("Account is not authorized for this family context")

        return [
            p for p in self.canonical.list_repair_proposals()
            if p.family_context_id == family_context_id
        ]

    def execute_repair_proposal(self, account_id: str, proposal_id: str) -> RepairProposal:
        proposal = self.canonical.get_repair_proposal(proposal_id)
        if proposal is None:
            raise ValueError("Repair proposal not found")

        context = self.canonical.get_family_context(proposal.family_context_id)
        if context is None or account_id not in context.member_ids:
            raise PermissionError("Account is not authorized for this family context")

        if proposal.is_executed:
            raise ValueError("Repair proposal has already been executed")

        # Canonical repairs MUST NOT execute automatically in current seed baseline
        if proposal.classification == RepairClassification.CANONICAL_REPAIR:
            raise NotImplementedError("Canonical entity repairs are deferred in the current seed baseline")

        # Derived projection repairs (explicit, typed operations only)
        if proposal.classification == RepairClassification.DERIVED_ONLY:
            if proposal.proposed_repair_action == "rebuild_derived_projections":
                try:
                    self.calendar_service.rebuild_calendar_projection(proposal.family_context_id)
                    self.timeline_service.rebuild_timeline_projection()
                    if hasattr(self, 'dashboard_service') and self.dashboard_service is not None:
                        self.dashboard_service.rebuild_dashboard_projections(proposal.family_context_id)
                    if hasattr(self, 'celebration_studio_service') and self.celebration_studio_service is not None:
                        self.celebration_studio_service.rebuild_celebration_artifacts(proposal.family_context_id)
                except Exception as e:
                    # Atomicity: if rebuild fails, proposal state stays unchanged and is_executed remains False
                    raise RuntimeError(f"Derived projection rebuild failed: {str(e)}") from e
            else:
                raise ValueError(f"Unknown derived repair action: '{proposal.proposed_repair_action}'")

        proposal.is_executed = True

        if proposal.provenance and proposal.provenance.audit_trail is not None:
            proposal.provenance.audit_trail.append(f"repair-executed-by:{account_id}")

        return proposal










class TransactionMemoryService:
    def __init__(
        self,
        repository: TransactionMemoryRepository,
        canonical: CanonicalRepository,
        authorization: AuthorizationService,
    ) -> None:
        self.repository = repository
        self.canonical = canonical
        self.authorization = authorization

    def record_transaction(
        self,
        actor_account_id: str,
        family_context_id: str,
        action_type: ActionType,
        resource_type: ResourceType,
        resource_id: str,
        resource_label_snapshot: str,
        operation: str,
        actor_person_id: Optional[str] = None,
        visibility: VisibilityLevel = VisibilityLevel.FAMILY,
        result_status: str = "SUCCESS",
        source: str = "user_action",
        correlation_id: Optional[str] = None,
        parent_transaction_id: Optional[str] = None,
        changed_fields: Optional[dict] = None,
        before_snapshot: Optional[dict] = None,
        after_snapshot: Optional[dict] = None,
        reason: Optional[str] = None,
        related_resource_ids: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
    ) -> TransactionRecord:
        record = TransactionRecord(
            actor_account_id=actor_account_id,
            actor_person_id=actor_person_id,
            family_context_id=family_context_id,
            action_type=action_type,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_label_snapshot=resource_label_snapshot,
            operation=operation,
            result_status=result_status,
            visibility=visibility,
            source=source,
            correlation_id=correlation_id,
            parent_transaction_id=parent_transaction_id,
            changed_fields=changed_fields,
            before_snapshot=before_snapshot,
            after_snapshot=after_snapshot,
            reason=reason,
            related_resource_ids=related_resource_ids or [],
            metadata=metadata or {},
        )
        return self.repository.record_transaction(record)

    def can_view_transaction(self, account_id: str, record: TransactionRecord, context: Optional[FamilyContext]) -> bool:
        if record.visibility == VisibilityLevel.PUBLIC:
            return True
        if record.visibility == VisibilityLevel.PRIVATE:
            return account_id == record.actor_account_id
        if record.visibility == VisibilityLevel.FAMILY:
            if context is None:
                return False
            return account_id in context.member_ids or account_id == record.actor_account_id
        return False

    def get_transaction_history_for_session(
        self,
        account_id: str,
        family_context_id: str,
        resource_type: Optional[ResourceType] = None,
        resource_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[TransactionRecord]:
        context = self.canonical.get_family_context(family_context_id)
        all_records = self.repository.list_transactions(
            family_context_id=family_context_id,
            resource_type=resource_type,
            resource_id=resource_id,
            limit=None,
        )

        authorized_records = [
            r for r in all_records
            if self.can_view_transaction(account_id, r, context)
        ]

        return authorized_records[:limit]

    def get_resource_history_for_session(
        self,
        account_id: str,
        family_context_id: str,
        resource_type: ResourceType,
        resource_id: str,
    ) -> List[TransactionRecord]:
        return self.get_transaction_history_for_session(
            account_id=account_id,
            family_context_id=family_context_id,
            resource_type=resource_type,
            resource_id=resource_id,
            limit=100,
        )

    def get_correlation_chain(
        self,
        account_id: str,
        family_context_id: str,
        correlation_id: str,
    ) -> List[TransactionRecord]:
        context = self.canonical.get_family_context(family_context_id)
        all_records = self.repository.list_transactions(
            family_context_id=family_context_id,
            correlation_id=correlation_id,
            limit=None,
        )
        return [r for r in all_records if self.can_view_transaction(account_id, r, context)]

    def explain_resource_history(
        self,
        account_id: str,
        family_context_id: str,
        resource_type: ResourceType,
        resource_id: str,
    ) -> dict:
        history = self.get_resource_history_for_session(account_id, family_context_id, resource_type, resource_id)

        current_state_desc = "Resource exists in canonical state."
        if resource_type == ResourceType.EVENT:
            ev = self.canonical.get_event(resource_id)
            if not ev: current_state_desc = "Event has been deleted."
            else: current_state_desc = f"Event '{ev.title}' scheduled on {ev.start_time} ({ev.visibility.value})."
        elif resource_type == ResourceType.MEMORY:
            mem = self.canonical.get_memory(resource_id)
            if not mem: current_state_desc = "Memory story has been deleted."
            else: current_state_desc = f"Memory '{mem.title}' ({mem.visibility.value})."

        facts = []
        for r in reversed(history):
            actor_name = r.actor_account_id
            acct = self.canonical.get_account(r.actor_account_id)
            if acct and acct.person_id:
                p = self.canonical.get_person(acct.person_id)
                if p: actor_name = p.name

            t_str = r.timestamp.strftime("%b %d, %H:%M UTC")
            facts.append(f"RECORDED FACT [{t_str}]: {actor_name} executed {r.action_type.value.upper()} ({r.operation}) on {r.resource_label_snapshot}")

        interpretation = f"Traced {len(history)} authorized historical activities leading to current state."

        return {
            "resource_id": resource_id,
            "resource_type": resource_type.value,
            "recorded_facts": facts,
            "current_state": current_state_desc,
            "mayil_interpretation": interpretation,
            "history_count": len(history),
        }


# ============================================================
# V2.3-D MAYIL LEARN-BY-DOING + LIVING DEMO SERVICE
# ============================================================

class MayilGuidedExperienceService:
    def __init__(
        self,
        canonical: CanonicalRepository,
        derived: DerivedRepository,
        auth: AuthorizationService,
        transaction_service: Optional[TransactionMemoryService] = None,
    ) -> None:
        self.canonical = canonical
        self.derived = derived
        self.auth = auth
        self.transaction_service = transaction_service
        self.guided_sessions: Dict[str, GuideSessionState] = {}
        self.practice_worlds: Dict[str, MayilPracticeWorld] = {}

    def initialize_session(
        self,
        account_id: str,
        family_context_id: str,
        mode: GuideMode = GuideMode.LEARN_BY_DOING,
        context_type: ContextType = ContextType.FAMILY,
        age_group: AgeGroup = AgeGroup.MIXED,
        include_family: bool = True,
        language: Language = Language.ENGLISH,
    ) -> GuideSessionState:
        session = GuideSessionState(
            account_id=account_id,
            family_context_id=family_context_id,
            current_mode=mode,
            context_type=context_type,
            age_group=age_group,
            include_family=include_family,
            language=language,
        )
        self.guided_sessions[account_id] = session
        return session

    def get_session(self, account_id: str) -> Optional[GuideSessionState]:
        return self.guided_sessions.get(account_id)

    def get_shared_journey_scenes(self, context_type: ContextType = ContextType.FAMILY, language: Language = Language.ENGLISH) -> List[SceneDefinition]:
        # Multilingual definitions for English, Tamil, Hindi
        scenes = [
            SceneDefinition(
                scene_id="SCENE_WELCOME",
                scene_index=0,
                title={"en": "Welcome to FEMC", "ta": "FEMC-க்கு நல்வரவு", "hi": "FEMC में आपका स्वागत है"},
                instruction={"en": "Let's explore your home dashboard together.", "ta": "உங்கள் முகப்புப் பலகையை ஒன்றாக ஆராய்வோம்.", "hi": "आइए साथ मिलकर अपना मुख्य डैशबोर्ड देखें।"},
                narration={"en": "Welcome! I am Mayil, your family memory companion.", "ta": "வணக்கம்! நான் மயில், உங்கள் குடும்ப நினைவுத் தோழன்.", "hi": "नमस्ते! मैं मयिल हूँ, आपका पारिवारिक स्मरण साथी।"},
                subtitle={"en": "Overview of active family events and memories", "ta": "செயலில் உள்ள குடும்ப நிகழ்வுகள் மற்றும் நினைவுகள்", "hi": "सक्रिय पारिवारिक आयोजनों और यादों का अवलोकन"},
                success_message={"en": "Great start!", "ta": "சிறப்பான தொடக்கம்!", "hi": "शानदार शुरुआत!"},
                help_message={"en": "Click on HOME to view dashboard.", "ta": "முகப்பைத் பார்க்க HOME என்பதைக் கிளிக் செய்யவும்.", "hi": "डैशबोर्ड देखने के लिए HOME पर क्लिक करें।"},
                target_view="home",
                target_control="nav-home",
                expected_action=ActionType.PERSPECTIVE_SWITCH,
                expected_resource_type=ResourceType.GROUP_CONTEXT,
                next_scene_id="SCENE_FAMILY",
            ),
            SceneDefinition(
                scene_id="SCENE_FAMILY",
                scene_index=1,
                title={"en": "Family & Relationships", "ta": "குடும்பம் மற்றும் உறவுகள்", "hi": "परिवार और रिश्ते"},
                instruction={"en": "Please click FAMILY to view your group topology.", "ta": "உங்கள் குழு அமைப்பைப் பார்க்க FAMILY என்பதைக் கிளிக் செய்யவும்.", "hi": "अपने समूह टोपोलॉजी को देखने के लिए FAMILY पर क्लिक करें।"},
                narration={"en": "Here are the people you love and care about.", "ta": "இங்கே நீங்கள் நேசிக்கும் குடும்ப உறுப்பினர்கள் உள்ளனர்.", "hi": "यहाँ वे लोग हैं जिन्हें आप प्यार करते हैं।"},
                subtitle={"en": "Family members and relationship connections", "ta": "குடும்ப உறுப்பினர்கள் மற்றும் உறவு இணைப்புகள்", "hi": "परिवार के सदस्य और रिश्तों के संबंध"},
                success_message={"en": "Wonderful! You are viewing family topology.", "ta": "அருமை! நீங்கள் குடும்ப அமைப்பைப் பார்க்கிறீர்கள்.", "hi": "अद्भुत! आप पारिवारिक टोपोलॉजी देख रहे हैं।"},
                help_message={"en": "Click the FAMILY item on the top navigation bar.", "ta": "மேல் வழிசெலுத்தல் பட்டியில் உள்ள FAMILY என்பதைக் கிளிக் செய்யவும்.", "hi": "नेविगेशन बार पर FAMILY पर क्लिक करें।"},
                target_view="family",
                target_control="nav-family",
                expected_action=ActionType.PERSPECTIVE_SWITCH,
                expected_resource_type=ResourceType.PERSON,
                next_scene_id="SCENE_CALENDAR",
            ),
            SceneDefinition(
                scene_id="SCENE_CALENDAR",
                scene_index=2,
                title={"en": "Shared Calendar", "ta": "பகிரப்பட்ட நாட்காட்டி", "hi": "साझा कैलेंडर"},
                instruction={"en": "Click CALENDAR to view scheduled events.", "ta": "திட்டமிடப்பட்ட நிகழ்வுகளைப் பார்க்க CALENDAR என்பதைக் கிளிக் செய்யவும்.", "hi": "नियोजित कार्यक्रमों को देखने के लिए CALENDAR पर क्लिक करें।"},
                narration={"en": "Never miss a family milestone or celebration.", "ta": "குடும்ப மைல்கல் அல்லது கொண்டாட்டத்தை என்றும் தவறவிடாதீர்கள்.", "hi": "किसी भी पारिवारिक अवसर को कभी न भूलें।"},
                subtitle={"en": "Timeline of family celebrations and milestones", "ta": "குடும்பக் கொண்டாட்டங்கள் மற்றும் மைல்கற்களின் காலவரிசை", "hi": "पारिवारिक समारोहों और मील के पत्थरों की समयरेखा"},
                success_message={"en": "Excellent! You are now in the Calendar view.", "ta": "மிக நன்று! இப்போது நாட்காட்டி பார்வையில் உள்ளீர்கள்.", "hi": "उत्कृष्ट! अब आप कैलेंडर दृश्य में हैं।"},
                help_message={"en": "Click CALENDAR on the top navigation ribbon.", "ta": "மேல் வழிசெலுத்தல் ரிப்பனில் CALENDAR என்பதைக் கிளிக் செய்யவும்.", "hi": "शीर्ष नेविगेशन रिबन पर CALENDAR पर क्लिक करें।"},
                target_view="calendar",
                target_control="nav-events",
                expected_action=ActionType.PERSPECTIVE_SWITCH,
                expected_resource_type=ResourceType.EVENT,
                next_scene_id="SCENE_CREATE_EVENT",
            ),
            SceneDefinition(
                scene_id="SCENE_CREATE_EVENT",
                scene_index=3,
                title={"en": "Schedule a Real Event", "ta": "ஒரு உண்மையான நிகழ்வைத் திட்டமிடுங்கள்", "hi": "एक वास्तविक कार्यक्रम निर्धारित करें"},
                instruction={"en": "Now let's create a real event! Click + Schedule New Event.", "ta": "இப்போது ஒரு புதிய நிகழ்வை உருவாக்குவோம்! + Schedule New Event என்பதைக் கிளிக் செய்யவும்.", "hi": "अब एक नया कार्यक्रम बनाएं! + Schedule New Event पर क्लिक करें।"},
                narration={"en": "Creating events keeps memories organized in context.", "ta": "நிகழ்வுகளை உருவாக்குவது நினைவுகளை ஒழுங்கமைக்கிறது.", "hi": "आयोजन बनाने से यादें व्यवस्थित रहती हैं।"},
                subtitle={"en": "Add birthday, milestone or family gathering", "ta": "பிறந்த நாள் அல்லது குடும்பக் கூட்டத்தைச் சேர்க்கவும்", "hi": "जन्मदिन या पारिवारिक समारोह जोड़ें"},
                success_message={"en": "Bravo! You created a real FEMC event.", "ta": "அற்புதம்! நீங்கள் ஒரு புதிய நிகழ்வை உருவாக்கியுள்ளீர்கள்.", "hi": "शाबाश! आपने एक नया आयोजन बनाया।"},
                help_message={"en": "Click the '+ Schedule New Event' button on the Calendar card.", "ta": "கார்டில் உள்ள '+ Schedule New Event' பொத்தானைக் கிளிக் செய்யவும்.", "hi": "कैलेंडर कार्ड पर '+ Schedule New Event' बटन पर क्लिक करें।"},
                target_view="calendar",
                target_control="btn-create-event",
                expected_action=ActionType.CREATE,
                expected_resource_type=ResourceType.EVENT,
                transaction_expectation="EVENT_CREATE",
                next_scene_id="SCENE_MEMORIES",
            ),
            SceneDefinition(
                scene_id="SCENE_MEMORIES",
                scene_index=4,
                title={"en": "Memories & Media", "ta": "நினைவுகள் மற்றும் ஊடகங்கள்", "hi": "यादें और मीडिया"},
                instruction={"en": "Click MEMORIES & MEDIA to view stories.", "ta": "கதைகளைப் பார்க்க MEMORIES & MEDIA என்பதைக் கிளிக் செய்யவும்.", "hi": "कहानियां देखने के लिए MEMORIES & MEDIA पर क्लिक करें।"},
                narration={"en": "Memories connect stories with rich photos and audio.", "ta": "நினைவுகள் கதைகளை புகைப்படங்களுடன் இணைக்கின்றன.", "hi": "यादें कहानियों को तस्वीरों से जोड़ती हैं।"},
                subtitle={"en": "Story wall with audio notes and media cards", "ta": "ஒலி குறிப்புகள் மற்றும் புகைப்படச் சுவர்கள்", "hi": "ऑडियो नोट्स और फोटो कार्ड के साथ स्टोरी वॉल"},
                success_message={"en": "Awesome! Welcome to the Memory Story Wall.", "ta": "அருமை! நினைவுச் சுவருக்கு நல்வரவு.", "hi": "शानदार! मेमोरी स्टोरी वॉल में आपका स्वागत है।"},
                help_message={"en": "Click MEMORIES & MEDIA on the navigation bar.", "ta": "வழிசெலுத்தல் பட்டியில் MEMORIES & MEDIA என்பதைக் கிளிக் செய்யவும்.", "hi": "नेविगेशन बार पर MEMORIES & MEDIA पर क्लिक करें।"},
                target_view="memories",
                target_control="nav-timeline",
                expected_action=ActionType.PERSPECTIVE_SWITCH,
                expected_resource_type=ResourceType.MEMORY,
                next_scene_id="SCENE_CAPTURE_MEDIA",
            ),
            SceneDefinition(
                scene_id="SCENE_CAPTURE_MEDIA",
                scene_index=5,
                title={"en": "Add & Capture Media", "ta": "ஊடகங்களைச் சேர்க்கவும்", "hi": "मीडिया जोड़ें"},
                instruction={"en": "Click + Add Photo / Media to attach a photo.", "ta": "புகைப்படத்தை இணைக்க + Add Photo / Media என்பதைக் கிளிக் செய்யவும்.", "hi": "फोटो संलग्न करने के लिए + Add Photo / Media पर क्लिक करें।"},
                narration={"en": "Photos and audio bring family events to life.", "ta": "புகைப்படங்கள் நிகழ்வுகளுக்கு உயிர் கொடுக்கின்றன.", "hi": "तस्वीरें पारिवारिक कार्यक्रमों में जान डालती हैं।"},
                subtitle={"en": "Attach photo gallery item or record audio note", "ta": "புகைப்படம் அல்லது குரல் குறிப்பை இணைக்கவும்", "hi": "फोटो या वॉयस नोट संलग्न करें"},
                success_message={"en": "Great! Photo attached to memory.", "ta": "மிக நன்று! புகைப்படம் இணைக்கப்பட்டது.", "hi": "बहुत बढ़िया! फोटो संलग्न हो गई।"},
                help_message={"en": "Click '+ Add Photo / Media' in the Media section.", "ta": "ஊடகப் பிரிவில் உள்ள '+ Add Photo / Media' பொத்தானைக் கிளிக் செய்யவும்.", "hi": "मीडिया अनुभाग में '+ Add Photo / Media' पर क्लिक करें।"},
                target_view="media",
                target_control="btn-add-media",
                expected_action=ActionType.ATTACH,
                expected_resource_type=ResourceType.MEDIA,
                transaction_expectation="MEDIA_ATTACH",
                next_scene_id="SCENE_CREATE_MEMORY",
            ),
            SceneDefinition(
                scene_id="SCENE_CREATE_MEMORY",
                scene_index=6,
                title={"en": "Write a Memory Story", "ta": "ஒரு நினைவுக் கதையை எழுதுங்கள்", "hi": "एक स्मृति कहानी लिखें"},
                instruction={"en": "Click + Write Memory Story to record a story.", "ta": "கதையைப் பதிவுசெய்ய + Write Memory Story என்பதைக் கிளிக் செய்யவும்.", "hi": "कहानी रिकॉर्ड करने के लिए + Write Memory Story पर क्लिक करें।"},
                narration={"en": "Preserve your narrative in your own words.", "ta": "உங்கள் கதையை உங்கள் சொந்த சொற்களில் பாதுகாக்கவும்.", "hi": "अपनी कहानी को अपने शब्दों में सहेजें।"},
                subtitle={"en": "Create narrative memory story linked to event", "ta": "நிகழ்வுடன் இணைக்கப்பட்ட நினைவுக் கதையை உருவாக்கவும்", "hi": "आयोजन से जुड़ी स्मृति कहानी बनाएं"},
                success_message={"en": "Wonderful! Memory story recorded.", "ta": "அருமை! நினைவுக் கதை பதிவு செய்யப்பட்டது.", "hi": "अद्भुत! स्मृति कहानी दर्ज की गई।"},
                help_message={"en": "Click '+ Write Memory Story' on the Memory Wall.", "ta": "நினைவுச் சுவரில் உள்ள '+ Write Memory Story' பொத்தானைக் கிளிக் செய்யவும்.", "hi": "मेमोरी वॉल पर '+ Write Memory Story' पर क्लिक करें।"},
                target_view="memories",
                target_control="btn-create-memory",
                expected_action=ActionType.CREATE,
                expected_resource_type=ResourceType.MEMORY,
                transaction_expectation="MEMORY_CREATE",
                next_scene_id="SCENE_CREATE_CELEBRATION",
            ),
            SceneDefinition(
                scene_id="SCENE_CREATE_CELEBRATION",
                scene_index=7,
                title={"en": "Celebration Studio", "ta": "கொண்டாட்டக்கூடம்", "hi": "सेलिब्रेशन स्टूडियो"},
                instruction={"en": "Click CELEBRATIONS to view artifacts.", "ta": "கொண்டாட்டப் பொருட்களைப் பார்க்க CELEBRATIONS என்பதைக் கிளிக் செய்யவும்.", "hi": "उत्सव कलाकृतियों को देखने के लिए CELEBRATIONS पर क्लिक करें।"},
                narration={"en": "Mayil transforms memories into celebration cards and albums.", "ta": "மயில் நினைவுகளைக் கொண்டாட்ட ஆல்பங்களாக மாற்றுகிறது.", "hi": "मयिल यादों को उत्सव एल्बम में बदल देता है।"},
                subtitle={"en": "Derived celebration cards and family albums", "ta": "வாழ்த்து அட்டைகள் மற்றும் குடும்ப ஆல்பங்கள்", "hi": "ग्रीटिंग कार्ड और पारिवारिक एल्बम"},
                success_message={"en": "Magical! Celebration artifact generated.", "ta": "அற்புதமான மாயாஜாலம்! கொண்டாட்ட ஆல்பம் உருவாக்கப்பட்டது.", "hi": "जादुई! उत्सव एल्बम तैयार किया गया।"},
                help_message={"en": "Click CELEBRATIONS on the top navigation bar.", "ta": "மேல் வழிசெலுத்தல் பட்டியில் CELEBRATIONS என்பதைக் கிளிக் செய்யவும்.", "hi": "शीर्ष नेविगेशन बार पर CELEBRATIONS पर क्लिक करें।"},
                target_view="celebrations",
                target_control="nav-celebrations",
                expected_action=ActionType.GENERATE,
                expected_resource_type=ResourceType.CELEBRATION_ARTIFACT,
                transaction_expectation="CELEBRATION_GENERATE",
                next_scene_id="SCENE_SHARE_LINK",
            ),
            SceneDefinition(
                scene_id="SCENE_SHARE_LINK",
                scene_index=8,
                title={"en": "Sharing & Privacy", "ta": "பகிர்வு மற்றும் தனியுரிமை", "hi": "शेयरिंग और गोपनीयता"},
                instruction={"en": "Click SHARING to create tokenized links.", "ta": "இணைப்புகளை உருவாக்க SHARING என்பதைக் கிளிக் செய்யவும்.", "hi": "लिंक बनाने के लिए SHARING पर क्लिक करें।"},
                narration={"en": "Share securely with external family and friends.", "ta": "உறவினர்களுடன் பாதுகாப்பாகப் பகிருங்கள்.", "hi": "सुरक्षित रूप से बाहरी लोगों के साथ साझा करें।"},
                subtitle={"en": "Tokenized share links and revocation controls", "ta": "பாதுகாப்பான பகிர்தல் இணைப்புகள் மற்றும் ரத்துசெய்தல்", "hi": "सुरक्षित शेयर लिंक और निरस्तीकरण नियंत्रण"},
                success_message={"en": "Perfect! Share link generated.", "ta": "சிறப்பு! பகிர்வு இணைப்பு உருவாக்கப்பட்டது.", "hi": "उत्कृष्ट! शेयर लिंक तैयार किया गया।"},
                help_message={"en": "Click SHARING on the top navigation bar.", "ta": "மேல் வழிசெலுத்தல் பட்டியில் SHARING என்பதைக் கிளிக் செய்யவும்.", "hi": "शीर्ष नेविगेशन बार पर SHARING पर क्लिक करें।"},
                target_view="sharing",
                target_control="nav-sharing",
                expected_action=ActionType.SHARE,
                expected_resource_type=ResourceType.SHARE_LINK,
                transaction_expectation="SHARE_CREATE",
                next_scene_id="SCENE_VIEW_HISTORY",
            ),
            SceneDefinition(
                scene_id="SCENE_VIEW_HISTORY",
                scene_index=9,
                title={"en": "Activity & Audit Memory", "ta": "செயல்பாட்டு மற்றும் தணிக்கை நினைவு", "hi": "गतिविधि और ऑडिट मेमोरी"},
                instruction={"en": "Click ACTIVITY to view your journey log.", "ta": "உங்கள் வரலாற்றுப் பதிவைப் பார்க்க ACTIVITY என்பதைக் கிளிக் செய்யவும்.", "hi": "अपनी यात्रा देखने के लिए ACTIVITY पर क्लिक करें।"},
                narration={"en": "Every action is logged in an immutable audit memory.", "ta": "ஒவ்வொரு செயலும் மாற்ற முடியாத தணிக்கை நினைவில் பதிவு செய்யப்படுகிறது.", "hi": "हर कार्य अपरिवर्तनीय ऑडिट मेमोरी में दर्ज होता है।"},
                subtitle={"en": "Chronological audit memory feed and correlation chain", "ta": "காலவரிசைப்படி தணிக்கை வரலாற்றுப் பதிவு", "hi": "कालानुक्रमिक ऑडिट मेमोरी फ़ीड"},
                success_message={"en": "Amazing! You are inspecting audit memory.", "ta": "அற்புதம்! நீங்கள் தணிக்கை நினைவை ஆய்வு செய்கிறீர்கள்.", "hi": "अद्भुत! आप ऑडिट मेमोरी का निरीक्षण कर रहे हैं।"},
                help_message={"en": "Click ACTIVITY on the top navigation bar.", "ta": "மேல் வழிசெலுத்தல் பட்டியில் ACTIVITY என்பதைக் கிளிக் செய்யவும்.", "hi": "शीर्ष नेविगेशन बार पर ACTIVITY पर क्लिक करें।"},
                target_view="history",
                target_control="nav-history",
                expected_action=ActionType.PERSPECTIVE_SWITCH,
                expected_resource_type=ResourceType.GROUP_CONTEXT,
                next_scene_id="SCENE_ASK_MAYIL",
            ),
            SceneDefinition(
                scene_id="SCENE_ASK_MAYIL",
                scene_index=10,
                title={"en": "Mayil Explainability Audit", "ta": "மயிலின் விளக்க தணிக்கை", "hi": "मयिल स्पष्टीकरण ऑडिट"},
                instruction={"en": "Click Ask Mayil to hear Mayil explain what you did.", "ta": "நீங்கள் செய்ததை மயில் விளக்குவதைக் கேட்க Ask Mayil என்பதைக் கிளிக் செய்யவும்.", "hi": "आपने जो किया उसे मयिल द्वारा समझाने के लिए Ask Mayil पर क्लिक करें।"},
                narration={"en": "Mayil analyzes your journey history and answers questions.", "ta": "மயில் உங்கள் வரலாற்றை ஆய்வு செய்து கேள்விகளுக்குப் பதிலளிக்கிறது.", "hi": "मयिल आपकी यात्रा का विश्लेषण करता है और प्रश्नों का उत्तर देता है।"},
                subtitle={"en": "Conversational explainability distinguishing facts vs state", "ta": "உண்மைகளையும் தற்போதைய நிலையையும் பிரித்து விவரிக்கும் உரையாடல்", "hi": "तथ्यों और स्थिति के बीच अंतर बताने वाला संवाद"},
                success_message={"en": "Congratulations! You have completed the Mayil Learn-By-Doing Journey!", "ta": "வாழ்த்துக்கள்! நீங்கள் கற்றல் பயணத்தை வெற்றிகரமாக முடித்துவிட்டீர்கள்!", "hi": "बधाई हो! आपने मयिल लर्निंग जर्नी पूरी कर ली है!"},
                help_message={"en": "Click the 'Ask Mayil' button on the page.", "ta": "'Ask Mayil' பொத்தானைக் கிளிக் செய்யவும்.", "hi": "'Ask Mayil' बटन पर क्लिक करें।"},
                target_view="history",
                target_control="btn-ask-mayil",
                expected_action=ActionType.MAYIL_PROPOSAL,
                expected_resource_type=ResourceType.MAYIL_INTERACTION,
                next_scene_id=None,
            ),
        ]
        return scenes

    def validate_user_action(
        self,
        account_id: str,
        action_type: ActionType,
        control_id: str,
        resource_id: str,
        resource_label: str = "",
        operation: str = "",
    ) -> dict:
        session = self.guided_sessions.get(account_id)
        if not session:
            return {"status": "error", "message": "No active guided session"}

        scenes = self.get_shared_journey_scenes(session.context_type, session.language)
        if session.current_scene_index >= len(scenes):
            return {"status": "completed", "message": "Guided journey complete!"}

        current_scene = scenes[session.current_scene_index]
        is_correct = (control_id == current_scene.target_control or action_type == current_scene.expected_action)

        lang_key = session.language.value if hasattr(session.language, "value") else str(session.language)

        if is_correct:
            # 1. Record authentic transaction if transaction service is available
            tx_record = None
            if self.transaction_service:
                tx_record = self.transaction_service.record_transaction(
                    actor_account_id=account_id,
                    family_context_id=session.family_context_id,
                    action_type=action_type,
                    resource_type=current_scene.expected_resource_type,
                    resource_id=resource_id or current_scene.scene_id,
                    resource_label_snapshot=resource_label or current_scene.title.get(lang_key, "Exercise Action"),
                    operation=operation or current_scene.instruction.get(lang_key, "Completed exercise"),
                    source="learn_by_doing_exercise",
                )
                session.last_transaction_id = tx_record.transaction_id

            if current_scene.scene_id not in session.completed_scene_ids:
                session.completed_scene_ids.append(current_scene.scene_id)

            session.attempts = 0
            session.current_scene_index += 1
            is_journey_complete = session.current_scene_index >= len(scenes)

            next_sc = scenes[session.current_scene_index] if not is_journey_complete else None

            return {
                "status": "success",
                "message": current_scene.success_message.get(lang_key, "Great job!"),
                "is_journey_complete": is_journey_complete,
                "current_scene": current_scene.__dict__,
                "next_scene": next_sc.__dict__ if next_sc else None,
                "session_state": session.__dict__,
                "transaction_recorded": tx_record.transaction_id if tx_record else None,
            }
        else:
            session.attempts += 1
            return {
                "status": "wrong_action",
                "message": f"That's okay 😊. For this exercise, please click '{current_scene.target_control}'",
                "help_message": current_scene.help_message.get(lang_key, "Please follow Mayil's guide."),
                "target_control": current_scene.target_control,
                "current_scene": current_scene.__dict__,
                "session_state": session.__dict__,
            }

    def switch_mode(self, account_id: str, new_mode: GuideMode) -> GuideSessionState:
        session = self.guided_sessions.get(account_id)
        if session:
            session.current_mode = new_mode
            session.updated_at = datetime.datetime.utcnow()
        return session

    def reset_guided_session(self, account_id: str) -> GuideSessionState:
        session = self.guided_sessions.get(account_id)
        if session:
            session.current_scene_index = 0
            session.attempts = 0
            session.completed_scene_ids.clear()
            session.created_resource_ids.clear()
            session.last_transaction_id = None
            session.updated_at = datetime.datetime.utcnow()
        return session

    def get_or_create_practice_world(
        self,
        account_id: str,
        family_context_id: str,
        context_type: ContextType = ContextType.FAMILY,
        age_group: AgeGroup = AgeGroup.MIXED,
        include_family: bool = True,
        language: Language = Language.ENGLISH,
    ) -> MayilPracticeWorld:
        if not hasattr(self, "practice_worlds"):
            self.practice_worlds: Dict[str, MayilPracticeWorld] = {}

        pw = self.practice_worlds.get(account_id)
        if not pw or not pw.is_active:
            pw = MayilPracticeWorld(
                account_id=account_id,
                family_context_id=family_context_id,
                is_active=True,
                context_type=context_type,
                age_group=age_group,
                include_family=include_family,
                language=language,
            )
            self._seed_practice_world_data(pw)
            self.practice_worlds[account_id] = pw
        return pw

    def _seed_practice_world_data(self, pw: MayilPracticeWorld) -> None:
        pw.simulated_persons.clear()
        pw.simulated_events.clear()
        pw.simulated_memories.clear()
        pw.simulated_media_items.clear()
        pw.simulated_celebrations.clear()
        pw.simulated_reminders.clear()
        pw.simulated_share_links.clear()
        pw.simulated_transactions.clear()

        # Seed Persons based on context
        if pw.context_type == ContextType.FAMILY:
            pw.simulated_persons = [
                {"id": "sim_p1", "name": "Alice", "role": "Mom", "avatar": "👩"},
                {"id": "sim_p2", "name": "Bob", "role": "Dad", "avatar": "👨"},
                {"id": "sim_p3", "name": "Charlie", "role": "Son", "avatar": "👦"},
                {"id": "sim_p4", "name": "Diana", "role": "Daughter", "avatar": "👧"},
                {"id": "sim_p5", "name": "Grandma Mary", "role": "Grandmother", "avatar": "👵"},
            ]
        elif pw.context_type == ContextType.FRIENDS:
            pw.simulated_persons = [
                {"id": "sim_p1", "name": "Sam", "role": "Friend", "avatar": "👱"},
                {"id": "sim_p2", "name": "Alex", "role": "Friend", "avatar": "🧔"},
                {"id": "sim_p3", "name": "Maya", "role": "Friend", "avatar": "👩‍🦱"},
            ]
            if pw.include_family:
                pw.simulated_persons.append({"id": "sim_p4", "name": "Alice (Mom)", "role": "Family", "avatar": "👩"})
        else:
            pw.simulated_persons = [
                {"id": "sim_p1", "name": "Elena (Lead)", "role": "Organizer", "avatar": "👩‍💼"},
                {"id": "sim_p2", "name": "Raj (Coordinator)", "role": "Volunteer", "avatar": "👨‍💼"},
            ]
            if pw.include_family:
                pw.simulated_persons.append({"id": "sim_p3", "name": "Bob (Dad)", "role": "Family Volunteer", "avatar": "👨"})

        # Seed initial simulated events
        pw.simulated_events = [
            {
                "id": "sim_ev1",
                "title": "Alice's Birthday Dinner" if pw.context_type == ContextType.FAMILY else "Group Reunion",
                "date": "2026-08-20",
                "status": "UPCOMING",
                "description": "Celebration dinner with special cake and song.",
            },
            {
                "id": "sim_ev2",
                "title": "Weekend Getaway",
                "date": "2026-08-25",
                "status": "UPCOMING",
                "description": "Fun weekend trip together.",
            },
        ]

        # Seed initial simulated memories
        pw.simulated_memories = [
            {
                "id": "sim_mem1",
                "title": "Birthday Cake Surprise",
                "summary": "Joyful moment when blowing out candles.",
                "ref_event_id": "sim_ev1",
            }
        ]

        # Seed initial simulated media
        pw.simulated_media_items = [
            {"id": "sim_med1", "caption": "Cake Photo", "type": "PHOTO", "url": "/static/demo_cake.jpg"}
        ]

        # Seed initial simulated celebration
        pw.simulated_celebrations = [
            {"id": "sim_cel1", "title": "Birthday Celebration Card", "theme": "GOLDEN_JOY"}
        ]

        # Seed initial simulated reminder
        pw.simulated_reminders = [
            {"id": "sim_rem1", "title": "Buy Birthday Gift", "due_date": "2026-08-19"}
        ]

        # Seed initial simulated share link
        pw.simulated_share_links = [
            {"id": "sim_sh1", "token": "sim_share_token_123", "target_type": "EVENT", "target_id": "sim_ev1"}
        ]

        # Seed initial practice transaction record
        pw.simulated_transactions.append({
            "transaction_id": "sim_tx_001",
            "action_type": "PRACTICE_WORLD_INITIALIZED",
            "resource_type": "PRACTICE_WORLD",
            "resource_id": pw.session_id,
            "resource_label": f"Practice World ({pw.context_type.value})",
            "details": "Initialized isolated Mayil Practice World training sandbox.",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "is_practice": True,
            "audit_type": "PRACTICE WORLD ACTIVITY",
        })

    def execute_simulated_action(
        self,
        account_id: str,
        action_type: ActionType,
        control_id: str,
        resource_type: ResourceType = ResourceType.EVENT,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        pw = self.practice_worlds.get(account_id)
        if not pw or not pw.is_active:
            pw = self.get_or_create_practice_world(account_id, "sim_fc_001")

        session = self.guided_sessions.get(account_id)
        if not session:
            session = self.initialize_session(account_id, "sim_fc_001")

        scenes = self.get_shared_journey_scenes(session.context_type)
        current_scene = scenes[session.current_scene_index]
        lang_key = session.language.value.lower()

        payload = payload or {}
        new_resource_id = f"sim_res_{len(pw.simulated_transactions)+1:03d}"

        # Perform simulated sandbox mutation (Zero Real Canonical Mutation)
        if action_type in (ActionType.CREATE, ActionType.PERSPECTIVE_SWITCH) and resource_type == ResourceType.EVENT:
            pw.simulated_events.append({
                "id": new_resource_id,
                "title": payload.get("title", "Simulated Family Event"),
                "date": payload.get("date", "2026-08-22"),
                "status": "UPCOMING",
                "description": payload.get("description", "Simulated practice event"),
            })
        elif action_type in (ActionType.CREATE, ActionType.ATTACH) and resource_type == ResourceType.MEMORY:
            pw.simulated_memories.append({
                "id": new_resource_id,
                "title": payload.get("title", "Simulated Memory"),
                "summary": payload.get("summary", "A beautiful simulated moment."),
                "ref_event_id": payload.get("ref_event_id", "sim_ev1"),
            })
        elif action_type in (ActionType.ATTACH, ActionType.CREATE) and resource_type in (ResourceType.MEDIA, ResourceType.MEDIA_ALBUM):
            pw.simulated_media_items.append({
                "id": new_resource_id,
                "caption": payload.get("caption", "Simulated Media Photo"),
                "type": payload.get("type", "PHOTO"),
                "url": payload.get("url", "/static/demo_sim_media.jpg"),
            })
        elif action_type in (ActionType.CREATE, ActionType.GENERATE) and resource_type == ResourceType.CELEBRATION_ARTIFACT:
            pw.simulated_celebrations.append({
                "id": new_resource_id,
                "title": payload.get("title", "Simulated Celebration Card"),
                "theme": payload.get("theme", "FESTIVE"),
            })
        elif action_type in (ActionType.CREATE, ActionType.REMINDER_CREATE) and resource_type == ResourceType.REMINDER:
            pw.simulated_reminders.append({
                "id": new_resource_id,
                "title": payload.get("title", "Simulated Reminder"),
                "due_date": payload.get("due_date", "2026-08-21"),
            })
        elif action_type in (ActionType.CREATE, ActionType.SHARE) and resource_type == ResourceType.SHARE_LINK:
            pw.simulated_share_links.append({
                "id": new_resource_id,
                "token": f"sim_share_{new_resource_id}",
                "target_type": resource_type.value,
                "target_id": payload.get("target_id", "sim_ev1"),
            })
        elif action_type == ActionType.CREATE and resource_type == ResourceType.PERSON:
            pw.simulated_persons.append({
                "id": new_resource_id,
                "name": payload.get("title", payload.get("name", "Simulated Member")),
                "email": payload.get("email", "sim_member@example.com"),
                "relationship": payload.get("relationship", "MEMBER"),
            })
        elif action_type == ActionType.REVOKE_SHARE and resource_type == ResourceType.SHARE_LINK:
            token = payload.get("token")
            pw.simulated_share_links = [l for l in pw.simulated_share_links if l.get("token") != token]

        # Append simulated transaction record
        tx_id = f"sim_tx_{len(pw.simulated_transactions)+1:03d}"
        sim_tx = {
            "transaction_id": tx_id,
            "action_type": action_type.value,
            "resource_type": resource_type.value,
            "resource_id": new_resource_id,
            "resource_label": payload.get("title") or payload.get("name") or payload.get("caption") or control_id,
            "details": f"Simulated practice action: {action_type.value} on control '{control_id}'",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "is_practice": True,
            "audit_type": "PRACTICE WORLD ACTIVITY",
        }
        pw.simulated_transactions.append(sim_tx)

        # Update guide session state
        session.completed_scene_ids.append(current_scene.scene_id)
        session.created_resource_ids.append(new_resource_id)
        session.last_transaction_id = tx_id
        session.attempts = 0
        session.current_scene_index += 1

        is_journey_complete = session.current_scene_index >= len(scenes)
        next_sc = scenes[session.current_scene_index] if not is_journey_complete else None

        explanation = f"You just executed '{action_type.value}' in Mayil's Practice World. FEMC recorded this as a safe simulated transaction."

        res_dict = {
            "status": "success",
            "message": current_scene.success_message.get(lang_key, "Great job!"),
            "explanation": explanation,
            "is_journey_complete": is_journey_complete,
            "current_scene": current_scene.__dict__,
            "next_scene": next_sc.__dict__ if next_sc else None,
            "session_state": session.__dict__,
            "practice_world": pw.__dict__,
            "simulated_transaction": sim_tx,
        }

        if action_type == ActionType.CREATE and resource_type == ResourceType.PERSON:
            res_dict["account_id"] = f"sim_acc_{new_resource_id}"
            res_dict["person_id"] = new_resource_id
            res_dict["session_id"] = f"sim_sess_{new_resource_id}"
        elif action_type in (ActionType.CREATE, ActionType.PERSPECTIVE_SWITCH) and resource_type == ResourceType.EVENT:
            from .models import Event, EventStatus, EventCategory, VisibilityLevel
            cat_str = payload.get("category", "GENERAL").upper()
            vis_str = payload.get("visibility", "FAMILY").upper()
            try: cat = EventCategory(cat_str.lower())
            except ValueError: cat = EventCategory.GENERAL
            try: vis = VisibilityLevel(vis_str.lower())
            except ValueError: vis = VisibilityLevel.FAMILY

            now = _utc_now()
            sim_event = Event(
                id=new_resource_id,
                title=payload.get("title", "New Event"),
                description=payload.get("description", ""),
                family_context_id=pw.family_context_id,
                start_time=now + datetime.timedelta(days=1),
                end_time=now + datetime.timedelta(days=1, hours=2),
                visibility=vis,
                category=cat,
                status=EventStatus.PLANNED,
            )
            res_dict["event"] = sim_event
        elif action_type in (ActionType.CREATE, ActionType.ATTACH) and resource_type == ResourceType.MEMORY:
            from .models import Memory, VisibilityLevel
            vis_str = payload.get("visibility", "FAMILY").upper()
            try: vis = VisibilityLevel(vis_str.lower())
            except ValueError: vis = VisibilityLevel.FAMILY

            sim_memory = Memory(
                id=new_resource_id,
                event_id=payload.get("ref_event_id"),
                narrative=payload.get("summary", ""),
                visibility=vis,
            )
            res_dict["memory"] = sim_memory
        elif action_type in (ActionType.ATTACH, ActionType.CREATE) and resource_type in (ResourceType.MEDIA, ResourceType.MEDIA_ALBUM):
            from .models import MediaItem, MediaType, VisibilityLevel
            media_type_str = payload.get("type", "PHOTO").lower()
            vis_str = payload.get("visibility", "FAMILY").upper()
            try: m_type = MediaType(media_type_str)
            except ValueError: m_type = MediaType.PHOTO
            try: vis = VisibilityLevel(vis_str.lower())
            except ValueError: vis = VisibilityLevel.FAMILY

            sim_med = MediaItem(
                id=new_resource_id,
                uri=payload.get("url", ""),
                media_type=m_type,
                caption=payload.get("caption", ""),
                family_context_id=pw.family_context_id,
                event_id=payload.get("event_id"),
                memory_id=payload.get("memory_id"),
                visibility=vis,
            )
            res_dict["media_item"] = sim_med
        elif action_type in (ActionType.CREATE, ActionType.GENERATE) and resource_type == ResourceType.CELEBRATION_ARTIFACT:
            from .models import CelebrationArtifact
            sim_artifact = CelebrationArtifact(
                id=new_resource_id,
                title=payload.get("title", ""),
                family_context_id=pw.family_context_id,
            )
            res_dict["artifact"] = sim_artifact
        elif resource_type == ResourceType.SHARE_LINK:
            from .models import ShareLink, ShareResourceType
            if action_type == ActionType.REVOKE_SHARE:
                token = payload.get("token")
                sim_link = ShareLink(
                    id="sim_revoked",
                    token=token,
                    resource_type=ShareResourceType.EVENT,
                    resource_id="sim_ev1",
                    family_context_id=pw.family_context_id,
                    is_revoked=True,
                )
            else:
                res_type_str = payload.get("resource_type", "EVENT").upper()
                try: res_type = ShareResourceType(res_type_str.lower())
                except ValueError: res_type = ShareResourceType.EVENT
                sim_link = ShareLink(
                    id=new_resource_id,
                    token=f"sim_share_{new_resource_id}",
                    resource_type=res_type,
                    resource_id=payload.get("target_id"),
                    family_context_id=pw.family_context_id,
                )
            res_dict["share_link"] = sim_link

        return res_dict

    def explain_practice_history(self, account_id: str) -> Dict[str, Any]:
        pw = self.practice_worlds.get(account_id)
        if not pw:
            return {"status": "error", "message": "No active practice world found."}

        history_summary = []
        for tx in pw.simulated_transactions:
            history_summary.append(
                f"[{tx.get('timestamp')[:19]}] {tx.get('action_type')}: {tx.get('resource_label')} ({tx.get('audit_type')})"
            )

        return {
            "status": "success",
            "audit_type": "PRACTICE WORLD ACTIVITY",
            "transaction_count": len(pw.simulated_transactions),
            "simulated_transactions": pw.simulated_transactions,
            "mayil_explanation": (
                f"In Mayil's Practice World, you have performed {len(pw.simulated_transactions)} safe training actions. "
                "All actions remain strictly isolated in the practice sandbox and have zero effect on your real family data."
            ),
            "history_summary": history_summary,
        }

    def reset_practice_world(self, account_id: str) -> MayilPracticeWorld:
        pw = self.practice_worlds.get(account_id)
        if pw:
            self._seed_practice_world_data(pw)
            pw.updated_at = datetime.datetime.utcnow()
        session = self.guided_sessions.get(account_id)
        if session:
            self.reset_guided_session(account_id)
        return pw or self.get_or_create_practice_world(account_id, "sim_fc_001")

    def exit_practice_world(self, account_id: str) -> Dict[str, Any]:
        pw = self.practice_worlds.get(account_id)
        if pw:
            pw.is_active = False
            pw.updated_at = datetime.datetime.utcnow()
        return {
            "status": "exited",
            "message": "Practice complete. Your real FEMC data was not changed.",
            "is_practice_active": False,
        }

    def get_practice_members_projection(
        self,
        account_sessions: Dict[str, str],
        active_account_id: str,
        practice_world: MayilPracticeWorld,
    ) -> List[Dict[str, Any]]:
        members_list = []
        for acc_id, sess_id in account_sessions.items():
            acc = self.canonical.get_account(acc_id)
            per = self.canonical.get_person(acc.person_id) if acc and acc.person_id else None
            if acc and per:
                members_list.append({
                    "account_id": acc.id,
                    "person_id": per.id,
                    "name": per.name,
                    "email": acc.email,
                    "username": acc.username,
                    "session_id": sess_id,
                    "is_active": acc.id == active_account_id,
                })
        for sp in practice_world.simulated_persons:
            members_list.append({
                "account_id": sp["id"],
                "person_id": sp["id"],
                "name": sp["name"],
                "email": sp.get("email", sp["name"].lower().split()[0] + "@example.com"),
                "username": sp["name"].lower(),
                "session_id": f"sim_sess_{sp['id']}",
                "is_active": False,
            })
        return members_list

    def get_practice_calendar_projection(self, practice_world: MayilPracticeWorld) -> List[Dict[str, Any]]:
        calendar_entries = []
        for e in practice_world.simulated_events:
            try:
                dt = datetime.datetime.strptime(e.get("date", "2026-08-22"), "%Y-%m-%d").date()
            except Exception:
                dt = datetime.date(2026, 8, 22)
            calendar_entries.append({
                "event_id": e.get("id"),
                "title": e.get("title"),
                "date": dt.isoformat(),
                "status": e.get("status", "UPCOMING"),
                "visibility": "FAMILY",
                "family_context_id": practice_world.family_context_id,
            })
        return calendar_entries

    def get_practice_event_detail_projection(self, practice_world: MayilPracticeWorld) -> Dict[str, Any]:
        if not practice_world.simulated_events:
            return {}
        e_first = practice_world.simulated_events[-1]
        return {
            "event_id": e_first.get("id"),
            "title": e_first.get("title"),
            "description": e_first.get("description", ""),
            "category": "general",
            "visibility": "family",
            "status": e_first.get("status", "UPCOMING"),
        }

    def get_practice_timeline_projection(self, practice_world: MayilPracticeWorld) -> List[Dict[str, Any]]:
        timeline_entries = []
        for m in practice_world.simulated_memories:
            ref_evt = next((e for e in practice_world.simulated_events if e["id"] == m.get("ref_event_id")), None)
            evt_date = ref_evt["date"] if ref_evt else "2026-08-22"
            timeline_entries.append({
                "event_id": m.get("ref_event_id", "sim_ev1"),
                "title": m.get("title"),
                "date": evt_date,
                "memory_ids": [m.get("id")],
                "narrative_excerpt": m.get("summary", ""),
            })
        return timeline_entries

    def get_practice_media_projection(self, practice_world: MayilPracticeWorld) -> List[Dict[str, Any]]:
        items = []
        for m in practice_world.simulated_media_items:
            items.append({
                "id": m.get("id"),
                "caption": m.get("caption"),
                "media_type": m.get("type", "PHOTO").lower(),
                "uri": m.get("url", "/static/demo_sim_media.jpg"),
            })
        return items

    def get_practice_celebrations_projection(self, practice_world: MayilPracticeWorld) -> List[Dict[str, Any]]:
        return practice_world.simulated_celebrations

    def get_practice_sharing_projection(self, practice_world: MayilPracticeWorld) -> List[Dict[str, Any]]:
        return practice_world.simulated_share_links

    def get_practice_history_projection(self, practice_world: MayilPracticeWorld) -> List[Dict[str, Any]]:
        return practice_world.simulated_transactions

    def get_practice_export_projection(self, practice_world: MayilPracticeWorld) -> Dict[str, Any]:
        return {
            "export_id": "sim_export_001",
            "family_context_id": practice_world.family_context_id,
            "exported_at": datetime.datetime.utcnow().isoformat(),
            "schema_version": "1.0",
            "records": {
                "events": practice_world.simulated_events,
                "memories": practice_world.simulated_memories,
                "media_items": practice_world.simulated_media_items,
                "celebrations": practice_world.simulated_celebrations,
                "share_links": practice_world.simulated_share_links,
                "transactions": practice_world.simulated_transactions,
            }
        }

