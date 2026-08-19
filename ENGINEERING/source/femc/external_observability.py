from __future__ import annotations

import datetime
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional


def _now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)


def _id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


@dataclass
class PracticeEvent:
    event_id: str = field(default_factory=lambda: _id("E"))
    timestamp: datetime.datetime = field(default_factory=_now)
    event_type: str = "page_view"
    page: str = ""
    action: str = ""
    resource_type: str = ""
    resource_id: str = ""
    outcome: str = "observed"


@dataclass
class PracticeFeedback:
    submitted_at: datetime.datetime = field(default_factory=_now)
    liked: str = ""
    confusing: str = ""
    broken: str = ""
    change_request: str = ""


@dataclass
class ExternalPracticeSession:
    session_id: str = field(default_factory=lambda: _id("P"))
    started_at: datetime.datetime = field(default_factory=_now)
    last_seen_at: datetime.datetime = field(default_factory=_now)
    ended_at: Optional[datetime.datetime] = None
    user_agent_class: str = "browser"
    pages: List[str] = field(default_factory=list)
    events: List[PracticeEvent] = field(default_factory=list)
    feedback: Optional[PracticeFeedback] = None

    @property
    def is_active(self) -> bool:
        return self.ended_at is None


class ExternalPracticeObservability:
    """Anonymous, in-memory observability for external FEMC Practice sessions."""

    IDLE_SECONDS = 180

    def __init__(self) -> None:
        self.sessions: Dict[str, ExternalPracticeSession] = {}

    def start_session(self, user_agent_class: str = "browser") -> ExternalPracticeSession:
        session = ExternalPracticeSession(user_agent_class=(user_agent_class or "browser")[:32])
        self.sessions[session.session_id] = session
        return session

    def touch(self, session_id: str) -> Optional[ExternalPracticeSession]:
        session = self.sessions.get(session_id)
        if session is not None:
            session.last_seen_at = _now()
        return session

    def record_event(
        self,
        session_id: str,
        event_type: str,
        page: str = "",
        action: str = "",
        resource_type: str = "",
        resource_id: str = "",
        outcome: str = "observed",
    ) -> Optional[PracticeEvent]:
        session = self.sessions.get(session_id)
        if session is None or not session.is_active:
            return None
        session.last_seen_at = _now()
        safe_page = (page or "")[:80]
        event = PracticeEvent(
            event_type=(event_type or "observed")[:40],
            page=safe_page,
            action=(action or "")[:80],
            resource_type=(resource_type or "")[:40],
            resource_id=(resource_id or "")[:80],
            outcome=(outcome or "observed")[:40],
        )
        session.events.append(event)
        if safe_page and safe_page not in session.pages:
            session.pages.append(safe_page)
        return event

    def submit_feedback(self, session_id: str, feedback: Dict[str, str]) -> bool:
        session = self.sessions.get(session_id)
        if session is None:
            return False
        session.last_seen_at = _now()
        session.feedback = PracticeFeedback(
            liked=str(feedback.get("liked", ""))[:1200],
            confusing=str(feedback.get("confusing", ""))[:1200],
            broken=str(feedback.get("broken", ""))[:1200],
            change_request=str(feedback.get("change_request", ""))[:1200],
        )
        return True

    def end_session(self, session_id: str) -> bool:
        session = self.sessions.get(session_id)
        if session is None:
            return False
        if session.ended_at is None:
            session.ended_at = _now()
            session.last_seen_at = session.ended_at
        return True

    def _is_recent(self, session: ExternalPracticeSession, now: datetime.datetime) -> bool:
        return (now - session.last_seen_at).total_seconds() <= self.IDLE_SECONDS

    def session_summary(self, session: ExternalPracticeSession, now: Optional[datetime.datetime] = None) -> Dict[str, object]:
        now = now or _now()
        end = session.ended_at or now
        return {
            "session_id": session.session_id,
            "started_at": session.started_at.isoformat(),
            "last_seen_at": session.last_seen_at.isoformat(),
            "ended_at": session.ended_at.isoformat() if session.ended_at else None,
            "active_now": session.is_active and self._is_recent(session, now),
            "duration_seconds": max(0, int((end - session.started_at).total_seconds())),
            "pages": list(session.pages),
            "event_count": len(session.events),
            "feedback_submitted": session.feedback is not None,
        }

    def dashboard(self) -> Dict[str, object]:
        now = _now()
        sessions = list(self.sessions.values())
        active = [s for s in sessions if s.is_active and self._is_recent(s, now)]
        explored = [s for s in sessions if len(s.events) > 0 or len(s.pages) > 1]
        feedback = [s for s in sessions if s.feedback is not None]
        idle = [s for s in sessions if s.is_active and not self._is_recent(s, now)]
        page_counts: Dict[str, int] = {}
        action_counts: Dict[str, int] = {}
        for session in sessions:
            for page in session.pages:
                page_counts[page] = page_counts.get(page, 0) + 1
            for event in session.events:
                key = event.action or event.event_type
                action_counts[key] = action_counts.get(key, 0) + 1
        return {
            "generated_at": now.isoformat(),
            "visitors": len(sessions),
            "active_now": len(active),
            "explored": len(explored),
            "idle_or_abandoned": len(idle),
            "feedback_submitted": len(feedback),
            "feedback_pending": max(0, len(sessions) - len(feedback)),
            "total_events": sum(len(s.events) for s in sessions),
            "page_counts": dict(sorted(page_counts.items(), key=lambda item: (-item[1], item[0]))),
            "action_counts": dict(sorted(action_counts.items(), key=lambda item: (-item[1], item[0]))),
            "sessions": [self.session_summary(s, now) for s in sessions],
        }
