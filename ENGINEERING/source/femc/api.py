from __future__ import annotations

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
