from __future__ import annotations


def _label_for_link(pw, link):
    target_type = str(link.get("target_type", "EVENT")).upper()
    target_id = link.get("target_id", "")

    if target_type == "EVENT":
        event = next((e for e in pw.simulated_events if e.get("id") == target_id), None)
        if event:
            return event.get("title") or "Family Event"

    if target_type in ("CELEBRATION", "CELEBRATION_ARTIFACT"):
        celebration = next((c for c in pw.simulated_celebrations if c.get("id") == target_id), None)
        if celebration:
            return celebration.get("title") or "Celebration"

    if target_type == "MEMORY":
        memory = next((m for m in pw.simulated_memories if m.get("id") == target_id), None)
        if memory:
            return memory.get("title") or memory.get("narrative") or "Family Memory"

    return target_id or "Shared resource"


def install(runtime):
    import launch_projection_patch as projection

    if getattr(projection, "_femc_sharing_label_patch", False):
        return

    def patched_sharing_projection(pw):
        rows = []
        for link in pw.simulated_share_links:
            rows.append({
                "id": link.get("id", ""),
                "token": link.get("token", ""),
                "resource_type": link.get("target_type", "EVENT"),
                "resource_id": link.get("target_id", ""),
                "resource_label": _label_for_link(pw, link),
                "is_revoked": bool(link.get("is_revoked", False)),
                "expires_at": link.get("expires_at"),
            })
        return rows

    projection._sharing_projection = patched_sharing_projection
    projection._femc_sharing_label_patch = True
