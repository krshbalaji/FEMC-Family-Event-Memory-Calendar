from __future__ import annotations

from urllib.parse import urlparse


def _practice_state(runtime):
    api = runtime.demo_state.api
    try:
        session_id = runtime.demo_state.session_id
        state = api.get_guided_experience_state_for_session(session_id)
        if not state or getattr(state, "current_mode", None).value != "learn_by_doing":
            return None
        pw = api.get_practice_world_state_for_session(session_id)
        if pw is None or not getattr(pw, "is_active", False):
            return None
        return pw
    except Exception:
        return None


def _norm_type(value):
    return str(value or "").strip().lower().replace("-", "_")


def _same_id(left, right):
    left = str(left or "")
    right = str(right or "")
    if not left or not right:
        return False
    return left == right or left.endswith("_" + right) or right.endswith("_" + left)


def _find_by_id(rows, target_id):
    for row in rows or []:
        if _same_id(row.get("id"), target_id):
            return row
    return None


def _resolve_link(pw, link):
    target_type = _norm_type(link.get("target_type", "event"))
    target_id = str(link.get("target_id", ""))

    if target_type == "event":
        event = _find_by_id(getattr(pw, "simulated_events", []), target_id)
        if event:
            return "event", event.get("id", target_id), event.get("title") or "Family Event"

    if target_type in ("celebration", "celebration_artifact"):
        artifacts = list(getattr(pw, "simulated_celebrations", []) or [])
        artifact = _find_by_id(artifacts, target_id)
        if artifact is None:
            artifact = next(
                (a for a in artifacts if _same_id(a.get("source_event_id"), target_id)),
                None,
            )
        if artifact:
            return "celebration_artifact", artifact.get("id", target_id), artifact.get("title") or "Celebration"

    if target_type == "memory":
        memory = _find_by_id(getattr(pw, "simulated_memories", []), target_id)
        if memory:
            return "memory", memory.get("id", target_id), memory.get("title") or memory.get("narrative") or "Family Memory"

    if target_type in ("media", "media_item"):
        media = _find_by_id(getattr(pw, "simulated_media_items", []), target_id)
        if media:
            return "media_item", media.get("id", target_id), media.get("caption") or "Media item"

    snapshot = (
        link.get("resource_label")
        or link.get("target_title")
        or link.get("title")
        or ""
    )
    return target_type or "resource", target_id, snapshot or "Shared resource"


def _sharing_projection(pw):
    rows = []
    for link in list(getattr(pw, "simulated_share_links", []) or []):
        resource_type, resource_id, resource_label = _resolve_link(pw, link)
        rows.append({
            "id": link.get("id", ""),
            "token": link.get("token", ""),
            "resource_type": resource_type,
            "resource_id": resource_id,
            "resource_label": resource_label,
            "is_revoked": bool(link.get("is_revoked", False)),
            "expires_at": link.get("expires_at"),
        })
    return rows


def _celebrations_projection(pw):
    rows = []
    for artifact in list(getattr(pw, "simulated_celebrations", []) or []):
        source_event_id = artifact.get("source_event_id")
        created_from = str(artifact.get("created_from", "")).lower()
        if not source_event_id and created_from != "event":
            continue

        row = dict(artifact)
        row["id"] = row.get("id") or f"sim_celebration_{source_event_id or len(rows) + 1}"
        row["title"] = row.get("title") or "Celebration"
        row["artifact_type"] = row.get("artifact_type") or "event_highlight"
        row["subtitle"] = row.get("subtitle") or row.get("source_description") or ""
        row["rendered_text"] = (
            row.get("rendered_text")
            or row.get("rendered_content")
            or row.get("content")
            or row.get("subtitle")
            or "Celebration details are being prepared."
        )
        row["visibility"] = str(row.get("visibility") or row.get("source_visibility") or "family").lower()
        rows.append(row)
    return rows


def _install_server_patch(runtime):
    handler = runtime.DemoHTTPRequestHandler
    if getattr(handler, "_femc_practice_sharing_celebration_projection_patch", False):
        return

    original_get = handler.do_GET

    def patched_get(self):
        parsed = urlparse(self.path)
        pw = _practice_state(runtime)
        if pw is not None:
            if parsed.path == "/api/celebrations":
                self._send_json({"artifacts": _celebrations_projection(pw)})
                return
            if parsed.path == "/api/sharing":
                self._send_json({"share_links": _sharing_projection(pw)})
                return
        return original_get(self)

    handler.do_GET = patched_get
    handler._femc_practice_sharing_celebration_projection_patch = True


def install(runtime):
    _install_server_patch(runtime)


__all__ = ["install"]
