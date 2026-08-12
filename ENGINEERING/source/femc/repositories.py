from __future__ import annotations

import datetime
from typing import Dict, List, Optional

from .models import (
    Account,
    ActionProposal,
    AuthenticatedSession,
    CalendarProjectionEntry,
    Event,
    EventStatus,
    FamilyContext,
    InsightAnalysis,
    MediaAlbum,
    MediaItem,
    Memory,
    Notification,
    Person,
    Place,
    ProvenanceMetadata,
    Relationship,
    SearchResultEntry,
    ShareLink,
    TimelineProjectionEntry,
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
        self.places: Dict[str, Place] = {}
        self.media_items: Dict[str, MediaItem] = {}
        self.media_albums: Dict[str, MediaAlbum] = {}
        self.notifications: Dict[str, Notification] = {}
        self.share_links: Dict[str, ShareLink] = {}
        self.action_proposals: Dict[str, ActionProposal] = {}
        self.insight_analyses: Dict[str, InsightAnalysis] = {}




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

    def add_place(self, place: Place) -> Place:
        if place.provenance is None:
            raise ValueError("Place provenance is required for canonical data")
        self.places[place.id] = place
        return place

    def get_place(self, place_id: str) -> Optional[Place]:
        return self.places.get(place_id)

    def list_places(self) -> List[Place]:
        return list(self.places.values())

    def add_media_item(self, item: MediaItem) -> MediaItem:
        if item.provenance is None:
            raise ValueError("Media item provenance is required for canonical data")
        self.media_items[item.id] = item
        return item

    def get_media_item(self, media_id: str) -> Optional[MediaItem]:
        return self.media_items.get(media_id)

    def list_media_items(self) -> List[MediaItem]:
        return list(self.media_items.values())

    def add_media_album(self, album: MediaAlbum) -> MediaAlbum:
        if album.provenance is None:
            raise ValueError("Media album provenance is required for canonical data")
        self.media_albums[album.id] = album
        return album

    def get_media_album(self, album_id: str) -> Optional[MediaAlbum]:
        return self.media_albums.get(album_id)

    def list_media_albums(self) -> List[MediaAlbum]:
        return list(self.media_albums.values())

    def list_relationships(self) -> List[Relationship]:
        return list(self.relationships.values())

    def add_notification(self, notification: Notification) -> Notification:
        if notification.provenance is None:
            raise ValueError("Notification provenance is required for canonical data")
        self.notifications[notification.id] = notification
        return notification

    def get_notification(self, notification_id: str) -> Optional[Notification]:
        return self.notifications.get(notification_id)

    def list_notifications(self) -> List[Notification]:
        return list(self.notifications.values())

    def add_share_link(self, share_link: ShareLink) -> ShareLink:
        if share_link.provenance is None:
            raise ValueError("Share link provenance is required for canonical data")
        self.share_links[share_link.token] = share_link
        return share_link

    def get_share_link_by_token(self, token: str) -> Optional[ShareLink]:
        return self.share_links.get(token)

    def list_share_links(self) -> List[ShareLink]:
        return list(self.share_links.values())

    def add_action_proposal(self, proposal: ActionProposal) -> ActionProposal:
        if proposal.provenance is None:
            raise ValueError("Action proposal provenance is required")
        self.action_proposals[proposal.id] = proposal
        return proposal

    def get_action_proposal(self, proposal_id: str) -> Optional[ActionProposal]:
        return self.action_proposals.get(proposal_id)

    def list_action_proposals(self) -> List[ActionProposal]:
        return list(self.action_proposals.values())

    def add_insight_analysis(self, analysis: InsightAnalysis) -> InsightAnalysis:
        if analysis.provenance is None:
            raise ValueError("Insight analysis provenance is required")
        self.insight_analyses[analysis.id] = analysis
        return analysis

    def get_insight_analysis(self, analysis_id: str) -> Optional[InsightAnalysis]:
        return self.insight_analyses.get(analysis_id)

    def list_insight_analyses(self) -> List[InsightAnalysis]:
        return list(self.insight_analyses.values())







class DerivedRepository:
    def __init__(self) -> None:
        self.calendar_entries: List[CalendarProjectionEntry] = []
        self.search_entries: List[SearchResultEntry] = []
        self.timeline_entries: List[TimelineProjectionEntry] = []

    def add_timeline_entry(self, entry: TimelineProjectionEntry) -> TimelineProjectionEntry:
        self.timeline_entries.append(entry)
        return entry

    def get_timeline_entries(self, family_context_id: Optional[str] = None) -> List[TimelineProjectionEntry]:
        if family_context_id is None:
            return list(self.timeline_entries)
        return [e for e in self.timeline_entries if e.family_context_id == family_context_id]

    def clear_timeline_entries(self) -> None:
        self.timeline_entries.clear()


    def add_calendar_entry(self, entry: CalendarProjectionEntry) -> CalendarProjectionEntry:
        self.calendar_entries.append(entry)
        return entry

    def get_calendar_entries(
        self,
        family_context_id: Optional[str] = None,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
    ) -> List[CalendarProjectionEntry]:
        entries = self.calendar_entries
        if family_context_id is not None:
            entries = [entry for entry in entries if entry.family_context_id == family_context_id]
        if start_date is not None:
            entries = [entry for entry in entries if entry.date >= start_date]
        if end_date is not None:
            entries = [entry for entry in entries if entry.date <= end_date]
        return list(entries)

    def update_calendar_entry_status(self, event_id: str, status: EventStatus) -> bool:
        updated = False
        for entry in self.calendar_entries:
            if entry.event_id == event_id:
                entry.status = status
                updated = True
        return updated


    def add_search_entry(self, entry: SearchResultEntry) -> SearchResultEntry:
        self.search_entries.append(entry)
        return entry

    def search(self, query: str) -> List[SearchResultEntry]:
        normalized = query.strip().lower()
        return [entry for entry in self.search_entries if normalized in entry.title.lower() or normalized in entry.excerpt.lower()]
