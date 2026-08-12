from __future__ import annotations

import datetime
from typing import List, Optional

from .models import Event, Memory, VisibilityLevel
from .repositories import CanonicalRepository, DerivedRepository
from .services import (
    AuthorizationService,
    CalendarService,
    EventService,
    IdentityService,
    MemoryService,
    SearchService,
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
        )

    def get_event_for_session(self, session_id: str, event_id: str) -> Event:
        session = self._validate_session(session_id)
        return self.event.get_event_for_account(event_id, session.account_id)

    def get_calendar_for_session(self, session_id: str, family_context_id: str):
        session = self._validate_session(session_id)
        return self.calendar.get_calendar_for_context(session.account_id, family_context_id)

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
