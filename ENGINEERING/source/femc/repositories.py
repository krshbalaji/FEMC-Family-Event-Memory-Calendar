from __future__ import annotations

from typing import Dict, List, Optional

from .models import (
    Account,
    AuthenticatedSession,
    CalendarProjectionEntry,
    Event,
    FamilyContext,
    Memory,
    Person,
    ProvenanceMetadata,
    Relationship,
    SearchResultEntry,
)


class CanonicalRepository:
    def __init__(self) -> None:
        self.persons: Dict[str, Person] = {}
        self.accounts: Dict[str, Account] = {}
        self.sessions: Dict[str, AuthenticatedSession] = {}
        self.relationships: Dict[str, Relationship] = {}
        self.family_contexts: Dict[str, FamilyContext] = {}
        self.events: Dict[str, Event] = {}
        self.memories: Dict[str, Memory] = {}

    def add_person(self, person: Person) -> Person:
        self.persons[person.id] = person
        return person

    def get_person(self, person_id: str) -> Optional[Person]:
        return self.persons.get(person_id)

    def add_account(self, account: Account) -> Account:
        self.accounts[account.id] = account
        return account

    def get_account(self, account_id: str) -> Optional[Account]:
        return self.accounts.get(account_id)

    def add_session(self, session: AuthenticatedSession) -> AuthenticatedSession:
        self.sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[AuthenticatedSession]:
        return self.sessions.get(session_id)

    def add_relationship(self, relationship: Relationship) -> Relationship:
        self.relationships[relationship.id] = relationship
        return relationship

    def get_relationship(self, relationship_id: str) -> Optional[Relationship]:
        return self.relationships.get(relationship_id)

    def add_family_context(self, context: FamilyContext) -> FamilyContext:
        self.family_contexts[context.id] = context
        return context

    def get_family_context(self, context_id: str) -> Optional[FamilyContext]:
        return self.family_contexts.get(context_id)

    def add_event(self, event: Event) -> Event:
        if event.provenance is None:
            raise ValueError("Event provenance is required for canonical data")
        self.events[event.id] = event
        return event

    def get_event(self, event_id: str) -> Optional[Event]:
        return self.events.get(event_id)

    def add_memory(self, memory: Memory) -> Memory:
        if memory.provenance is None:
            raise ValueError("Memory provenance is required for canonical data")
        self.memories[memory.id] = memory
        return memory

    def get_memory(self, memory_id: str) -> Optional[Memory]:
        return self.memories.get(memory_id)

    def list_events(self) -> List[Event]:
        return list(self.events.values())

    def list_memories(self) -> List[Memory]:
        return list(self.memories.values())

    def list_family_contexts(self) -> List[FamilyContext]:
        return list(self.family_contexts.values())


class DerivedRepository:
    def __init__(self) -> None:
        self.calendar_entries: List[CalendarProjectionEntry] = []
        self.search_entries: List[SearchResultEntry] = []

    def add_calendar_entry(self, entry: CalendarProjectionEntry) -> CalendarProjectionEntry:
        self.calendar_entries.append(entry)
        return entry

    def get_calendar_entries(self, family_context_id: Optional[str] = None) -> List[CalendarProjectionEntry]:
        if family_context_id is None:
            return list(self.calendar_entries)
        return [entry for entry in self.calendar_entries if entry.family_context_id == family_context_id]

    def add_search_entry(self, entry: SearchResultEntry) -> SearchResultEntry:
        self.search_entries.append(entry)
        return entry

    def search(self, query: str) -> List[SearchResultEntry]:
        normalized = query.strip().lower()
        return [entry for entry in self.search_entries if normalized in entry.title.lower() or normalized in entry.excerpt.lower()]
