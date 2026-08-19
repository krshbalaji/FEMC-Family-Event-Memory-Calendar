"""Anonymous external observability for the isolated FEMC Practice World.

Only sanitized metadata is retained. No tester identity, IP address, passwords,
or real family content is stored.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import uuid


IDLE_AFTER = timedelta(minutes=5)
MAX_FEEDBACK = 1200


@dataclass
class ExternalPracticeSession:
    session_id: str
    started_at: str
    last_seen_at: str
    ended_at: Optional[str] = None
    events: List[Dict[str, str]] = field(default_factory=list)
    feedback: List[Dict[str, str]] = field(default_factory=list)

    @property
    def state(self) -> str:
        if self.ended_at:
            return "abandoned" if not self.events else "ended"
        last = datetime.fromisoformat(self.last_seen_at)
        return "idle" if datetime.utcnow() - last > IDLE_AFTER else "active"

    @property
    def explored(self) -> bool:
        return bool(self.events)


class ExternalPracticeObservability:
    """In-memory, anonymous observability store for a single FEMC host."""

    def __init__(self) -> None:
        self._sessions: Dict[str, ExternalPracticeSession] = {}

    @staticmethod
    def _now() -> str:
        return datetime.utcnow().isoformat()

    @staticmethod
    def _new_id() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def _safe(value: Any, limit: int = 120) -> str:
        text = "" if value is None else str(value)
        return text[:limit].replace("\x00", "")

    def start_session(self, session_id: Optional[str] = None) -> ExternalPracticeSession:
        sid = self._safe(session_id, 64) or self._new_id()
        session = self._sessions.get(sid)
        if session is None or session.ended_at:
            now = self._now()
            session = ExternalPracticeSession(sid, now, now)
            self._sessions[sid] = session
        else:
            session.last_seen_at = self._now()
        return session

    def heartbeat(self, session_id: str) -> Optional[ExternalPracticeSession]:
        session = self._sessions.get(self._safe(session_id, 64))
        if session:
            session.last_seen_at = self._now()
        return session

    def end_session(self, session_id: str) -> Optional[ExternalPracticeSession]:
        session = self._sessions.get(self._safe(session_id, 64))
        if session:
            session.ended_at = self._now()
            session.last_seen_at = session.ended_at
        return session

    def record_event(
        self,
        session_id: str,
        event_type: str,
        page: str = "",
        action: str = "",
        resource_type: str = "",
        outcome: str = "",
    ) -> Optional[Dict[str, str]]:
        session = self._sessions.get(self._safe(session_id, 64))
        if not session:
            return None
        session.last_seen_at = self._now()
        event = {
            "event_type": self._safe(event_type, 64),
            "page": self._safe(page, 120),
            "action": self._safe(action, 120),
            "resource_type": self._safe(resource_type, 64),
            "outcome": self._safe(outcome, 120),
            "timestamp": session.last_seen_at,
        }
        session.events.append(event)
        return event

    def submit_feedback(
        self,
        session_id: str,
        category: str,
        text: str = "",
    ) -> Optional[Dict[str, str]]:
        session = self._sessions.get(self._safe(session_id, 64))
        if not session:
            return None
        feedback = {
            "category": self._safe(category, 40),
            "text": self._safe(text, MAX_FEEDBACK),
            "timestamp": self._now(),
        }
        session.feedback.append(feedback)
        session.last_seen_at = feedback["timestamp"]
        return feedback

    def session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        session = self._sessions.get(self._safe(session_id, 64))
        if not session:
            return None
        return {
            "session_id": session.session_id,
            "started_at": session.started_at,
            "last_seen_at": session.last_seen_at,
            "ended_at": session.ended_at,
            "state": session.state,
            "explored": session.explored,
            "event_count": len(session.events),
            "feedback_count": len(session.feedback),
        }

    def summary(self) -> Dict[str, Any]:
        sessions = list(self._sessions.values())
        page_counts: Dict[str, int] = {}
        action_counts: Dict[str, int] = {}
        total_events = 0
        feedback_submitted = 0
        active_now = 0
        explored = 0
        idle_or_abandoned = 0
        for session in sessions:
            state = session.state
            active_now += state == "active"
            explored += session.explored
            idle_or_abandoned += state in {"idle", "abandoned"}
            feedback_submitted += len(session.feedback)
            total_events += len(session.events)
            for event in session.events:
                page = event["page"] or "unknown"
                action = event["action"] or event["event_type"] or "unknown"
                page_counts[page] = page_counts.get(page, 0) + 1
                action_counts[action] = action_counts.get(action, 0) + 1
        pending = max(0, len(sessions) - feedback_submitted)
        return {
            "total_visitors": len(sessions),
            "active_now": active_now,
            "explored": explored,
            "idle_or_abandoned": idle_or_abandoned,
            "feedback_submitted": feedback_submitted,
            "feedback_pending": pending,
            "total_observed_events": total_events,
            "page_counts": dict(sorted(page_counts.items())),
            "action_counts": dict(sorted(action_counts.items())),
            "session_summaries": [self.session_summary(s.session_id) for s in sessions],
        }


__all__ = ["ExternalPracticeObservability", "ExternalPracticeSession"]
