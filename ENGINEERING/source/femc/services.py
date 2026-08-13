from __future__ import annotations

import datetime
from typing import List, Optional

from .models import (
    Account,
    ActionProposal,
    AnomalySeverity,
    AnomalyType,
    AuditAnomaly,
    AuthenticatedSession,
    CalendarProjectionEntry,
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


    SearchResultEntry,
    ShareLink,
    ShareResourceType,
    TimelineItemType,
    TimelineProjectionEntry,
    ValidationReport,
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
            current_time = datetime.datetime.utcnow()

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

        memories = [
            m for m in self.canonical.list_memories()
            if m.subject_id == person_id and self.auth.can_view_memory(account_id, m, context)
        ]

        media_items = [
            mi for mi in self.canonical.list_media_items()
            if (account and mi.owner_id == account.id) and self.auth.can_view_media_item(account_id, mi, context)
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

        due_reminders = [
            r for r in self.canonical.list_reminders()
            if (r.family_context_id == family_context_id or r.created_by_id == account_id)
        ]

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
            entry = DashboardProjectionEntry(
                family_context_id=family_context_id,
                item_type=DashboardEntryType.DUE_REMINDER,
                title=f"Reminder: {rem.reminder_type.value if hasattr(rem.reminder_type, 'value') else str(rem.reminder_type)}",
                subtitle=f"Offset {rem.offset_minutes} mins",
                date_or_time=rem.created_at,
                ref_id=rem.id,
                visibility=VisibilityLevel.FAMILY,
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
        return entries

    def rebuild_dashboard_projections(self, family_context_id: str) -> None:
        context = self.canonical.get_family_context(family_context_id)
        if context is None or not context.member_ids:
            self.derived.clear_dashboard_entries(family_context_id)
            return
        admin_id = context.member_ids[0]
        self.project_dashboard_entries(admin_id, family_context_id)


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

        st_str = start_time.isoformat() if start_time else (datetime.datetime.utcnow() + datetime.timedelta(days=1)).isoformat()

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
                st = datetime.datetime.fromisoformat(st_raw) if st_raw else datetime.datetime.utcnow()

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


class VelGuardianService:
    def __init__(
        self,
        canonical: CanonicalRepository,
        derived: DerivedRepository,
        auth: AuthorizationService,
        calendar_service: CalendarService,
        timeline_service: TimelineService,
        dashboard_service: Optional[DashboardService] = None,
    ) -> None:
        self.canonical = canonical
        self.derived = derived
        self.auth = auth
        self.calendar_service = calendar_service
        self.timeline_service = timeline_service
        self.dashboard_service = dashboard_service

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


        is_valid = len(anomalies) == 0
        return ValidationReport(
            is_valid=is_valid,
            checked_at=datetime.datetime.utcnow(),
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
                except Exception as e:
                    # Atomicity: if rebuild fails, proposal state stays unchanged and is_executed remains False
                    raise RuntimeError(f"Derived projection rebuild failed: {str(e)}") from e
            else:
                raise ValueError(f"Unknown derived repair action: '{proposal.proposed_repair_action}'")

        proposal.is_executed = True

        if proposal.provenance and proposal.provenance.audit_trail is not None:
            proposal.provenance.audit_trail.append(f"repair-executed-by:{account_id}")

        return proposal








