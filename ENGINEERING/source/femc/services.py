from __future__ import annotations

import datetime
from typing import List, Optional

from .models import (
    Account,
    AuthenticatedSession,
    CalendarProjectionEntry,
    Consent,
    Event,
    EventStatus,
    FamilyContext,
    Memory,
    ProvenanceMetadata,
    ProvenanceSourceType,
    SearchResultEntry,
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
    ) -> Event:
        context = self.canonical.get_family_context(family_context_id) if family_context_id else None
        if not self.auth.can_create_event(owner_id, context):
            raise PermissionError("Account is not authorized to create events in the target family context")
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


class CalendarService:
    def __init__(self, canonical: CanonicalRepository, derived: DerivedRepository, auth: AuthorizationService) -> None:
        self.canonical = canonical
        self.derived = derived
        self.auth = auth

    def get_calendar_for_context(self, account_id: str, family_context_id: str) -> List[CalendarProjectionEntry]:
        context = self.canonical.get_family_context(family_context_id)
        if context is None:
            return []
        entries = self.derived.get_calendar_entries(family_context_id)
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
