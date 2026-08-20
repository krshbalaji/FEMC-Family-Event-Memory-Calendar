from __future__ import annotations

import datetime
from urllib.parse import parse_qs, urlparse


def _practice_state(runtime):
    session_id = runtime.demo_state.session_id
    api = runtime.demo_state.api
    try:
        state = api.get_guided_experience_state_for_session(session_id)
        if not state or getattr(state, "current_mode", None).value != "learn_by_doing":
            return None
        pw = api.get_practice_world_state_for_session(session_id)
        if pw is None or not getattr(pw, "is_active", False):
            return None
        return pw
    except Exception:
        return None


def _enrich_event_mutation(runtime):
    guided = runtime.demo_state.api.guided_experience
    original = guided.execute_simulated_action
    if getattr(guided, "_femc_projection_patch", False):
        return

    def patched(account_id, action_type, control_id, resource_type, payload=None):
        payload = payload or {}
        result = original(account_id, action_type, control_id, resource_type, payload)
        try:
            if str(resource_type.value if hasattr(resource_type, "value") else resource_type).lower() == "event":
                pw = guided.practice_worlds.get(account_id)
                resource_id = result.get("event", {}).get("id") if isinstance(result.get("event"), dict) else getattr(result.get("event"), "id", None)
                if pw is not None and resource_id:
                    event = next((e for e in pw.simulated_events if e.get("id") == resource_id), None)
                    if event is not None:
                        event["category"] = str(payload.get("category", "GENERAL")).upper()
                        event["visibility"] = str(payload.get("visibility", "FAMILY")).upper()
                        event["description"] = payload.get("description", event.get("description", ""))
                        event["target_person_ids"] = list(payload.get("target_person_ids", event.get("target_person_ids", [])))
        except Exception:
            pass
        return result

    guided.execute_simulated_action = patched
    guided._femc_projection_patch = True


def _event_projection(pw, requested_id=None):
    events = list(pw.simulated_events)
    selected = None
    if requested_id:
        selected = next((e for e in events if e.get("id") == requested_id), None)
    if selected is None and events:
        selected = events[-1]

    calendar = []
    for e in events:
        date = e.get("date", "2026-08-22")
        calendar.append({
            "event_id": e.get("id"),
            "title": e.get("title", "Family Event"),
            "date": date,
            "date_or_time": date,
            "status": e.get("status", "UPCOMING"),
            "visibility": str(e.get("visibility", "FAMILY")).lower(),
            "family_context_id": pw.family_context_id,
            "description": e.get("description", ""),
            "category": str(e.get("category", "GENERAL")).lower(),
        })

    detail = {}
    if selected:
        date = selected.get("date", "2026-08-22")
        start = selected.get("start_time") or f"{date}T18:00:00"
        end = selected.get("end_time") or f"{date}T20:00:00"
        persons = []
        for pid in selected.get("target_person_ids", []):
            person = next((p for p in pw.simulated_persons if p.get("id") == pid), None)
            if person:
                persons.append({"name": person.get("name", "Family Member"), "person_id": pid})

        event = {
            "id": selected.get("id"),
            "title": selected.get("title", "Family Event"),
            "description": selected.get("description", ""),
            "category": str(selected.get("category", "GENERAL")).lower(),
            "visibility": str(selected.get("visibility", "FAMILY")).lower(),
            "status": selected.get("status", "UPCOMING"),
            "start_time": start,
            "end_time": end,
            "target_person_ids": selected.get("target_person_ids", []),
        }
        detail = {
            "event_id": selected.get("id"),
            "event": event,
            "description": event["description"],
            "category": event["category"],
            "visibility": event["visibility"],
            "status": event["status"],
            "start_time": start,
            "end_time": end,
            "target_persons": persons,
            "memories": [],
            "media_items": [],
            "place": None,
            "reminders": [],
        }
    return calendar, detail


def _dashboard_projection(pw):
    entries = []
    for e in pw.simulated_events:
        entries.append({
            "item_type": "upcoming_event",
            "title": e.get("title", "Family Event"),
            "description": e.get("description", ""),
            "date_or_time": e.get("date", ""),
            "category": str(e.get("category", "GENERAL")).lower(),
            "ref_id": e.get("id", ""),
            "visibility": str(e.get("visibility", "FAMILY")).lower(),
        })
    for m in pw.simulated_memories:
        entries.append({
            "item_type": "recent_memory",
            "title": m.get("title", "Family Memory"),
            "description": m.get("narrative") or m.get("summary", ""),
            "date_or_time": m.get("date", ""),
            "ref_id": m.get("id", ""),
            "visibility": "family",
        })
    for r in pw.simulated_reminders:
        entries.append({
            "item_type": "reminder_due",
            "title": r.get("title", "Reminder"),
            "description": r.get("due_date", ""),
            "date_or_time": r.get("due_date", ""),
            "ref_id": r.get("id", ""),
            "visibility": "family",
        })
    for c in pw.simulated_celebrations:
        entries.append({
            "item_type": "celebration_highlight",
            "title": c.get("title", "Celebration"),
            "description": "Practice celebration artifact",
            "date_or_time": "",
            "ref_id": c.get("id", ""),
            "visibility": "family",
        })

    summary = {
        "family_context": {"id": pw.family_context_id, "name": "Practice Family"},
        "member_count": len(pw.simulated_persons),
        "upcoming_events": [e for e in entries if e["item_type"] == "upcoming_event"],
        "recent_memories": [e for e in entries if e["item_type"] == "recent_memory"],
        "due_reminders": [e for e in entries if e["item_type"] == "reminder_due"],
        "celebration_highlights": [e for e in entries if e["item_type"] == "celebration_highlight"],
    }
    return summary, entries


def _family_projection(runtime, pw):
    api = runtime.demo_state.api
    members = api.get_members_projection(
        runtime.demo_state.session_id,
        runtime.demo_state.account_sessions,
        runtime.demo_state.active_account_id,
    )
    practice_names = {p.get("name") for p in pw.simulated_persons}
    relationships = []
    if {"Alice", "Bob"}.issubset(practice_names):
        relationships.append({"source_person_name": "Alice", "target_person_name": "Bob", "relationship_type": "partner", "confidence": "high"})
    if {"Alice", "Charlie"}.issubset(practice_names):
        relationships.append({"source_person_name": "Alice", "target_person_name": "Charlie", "relationship_type": "parent", "confidence": "high"})
    if {"Bob", "Charlie"}.issubset(practice_names):
        relationships.append({"source_person_name": "Bob", "target_person_name": "Charlie", "relationship_type": "parent", "confidence": "high"})
    return {"topology": {"members": members, "relationships": relationships}, "active_person_detail": {}, "members": members}


def _history_projection(pw):
    rows = []
    for tx in pw.simulated_transactions:
        rows.append({
            "transaction_id": tx.get("transaction_id", ""),
            "action_type": tx.get("action_type", ""),
            "resource_type": tx.get("resource_type", ""),
            "resource_id": tx.get("resource_id", ""),
            "resource_label_snapshot": tx.get("resource_label") or tx.get("resource_id", ""),
            "operation": tx.get("details", ""),
            "actor_account_id": "PRACTICE_USER",
            "visibility": "family",
            "timestamp": tx.get("timestamp", ""),
        })
    return rows


def _sharing_projection(pw):
    rows = []
    for link in pw.simulated_share_links:
        rows.append({
            "id": link.get("id", ""),
            "token": link.get("token", ""),
            "resource_type": link.get("target_type", "EVENT"),
            "resource_id": link.get("target_id", ""),
            "resource_label": link.get("target_id", ""),
            "is_revoked": bool(link.get("is_revoked", False)),
            "expires_at": link.get("expires_at"),
        })
    return rows


def install(runtime):
    _enrich_event_mutation(runtime)
    handler = runtime.DemoHTTPRequestHandler
    if getattr(handler, "_femc_live_practice_projection", False):
        return

    original_get = handler.do_GET

    def patched_get(self):
        parsed = urlparse(self.path)
        path = parsed.path
        pw = _practice_state(runtime)
        if pw is None:
            return original_get(self)

        if path == "/api/dashboard":
            summary, entries = _dashboard_projection(pw)
            self._send_json({"summary": summary, "entries": entries})
            return
        if path == "/api/family":
            self._send_json(_family_projection(runtime, pw))
            return
        if path == "/api/events":
            requested = parse_qs(parsed.query).get("event_id", [None])[0]
            calendar, detail = _event_projection(pw, requested)
            self._send_json({"calendar": calendar, "event_detail": detail})
            return
        if path == "/api/history":
            self._send_json({"transactions": _history_projection(pw)})
            return
        if path == "/api/sharing":
            self._send_json({"share_links": _sharing_projection(pw)})
            return
        return original_get(self)

    handler.do_GET = patched_get
    handler._femc_live_practice_projection = True


__all__ = ["install"]
