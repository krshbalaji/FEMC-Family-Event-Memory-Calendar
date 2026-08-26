from __future__ import annotations

import datetime
import html


def _same_id(left, right):
    left = str(left or "")
    right = str(right or "")
    if not left or not right:
        return False
    return left == right or left.endswith("_" + right) or right.endswith("_" + left)


def _friendly_datetime(value):
    text = str(value or "").strip()
    if not text:
        return "—"
    try:
        normalized = text.replace("Z", "+00:00")
        dt = datetime.datetime.fromisoformat(normalized)
        return dt.strftime("%A, %d %B %Y · %I:%M %p").replace(" 0", " ")
    except Exception:
        return text


def _event_context(resource):
    event = resource.get("source_event") if isinstance(resource.get("source_event"), dict) else {}
    if not event:
        event = resource.get("event") if isinstance(resource.get("event"), dict) else {}

    title = (
        resource.get("source_title")
        or event.get("title")
        or resource.get("event_title")
        or ""
    )
    description = (
        resource.get("source_description")
        or event.get("description")
        or resource.get("event_description")
        or resource.get("subtitle")
        or ""
    )
    start_time = (
        resource.get("start_time")
        or event.get("start_time")
        or resource.get("source_start_time")
        or ""
    )
    end_time = (
        resource.get("end_time")
        or event.get("end_time")
        or resource.get("source_end_time")
        or ""
    )
    people = resource.get("target_person_names") or event.get("target_person_names") or []
    if isinstance(people, str):
        people = [people]

    return {
        "title": str(title or "").strip(),
        "description": str(description or "").strip(),
        "start_time": start_time,
        "end_time": end_time,
        "people": [str(name).strip() for name in people if str(name).strip()],
    }


def _when_label(start_time, end_time):
    start = _friendly_datetime(start_time)
    end = _friendly_datetime(end_time)
    if start != "—" and end != "—":
        try:
            start_dt = datetime.datetime.fromisoformat(str(start_time).replace("Z", "+00:00"))
            end_dt = datetime.datetime.fromisoformat(str(end_time).replace("Z", "+00:00"))
            if start_dt.date() == end_dt.date():
                date_part = start_dt.strftime("%A, %d %B %Y")
                start_clock = start_dt.strftime("%I:%M %p").lstrip("0")
                end_clock = end_dt.strftime("%I:%M %p").lstrip("0")
                return f"{date_part} · {start_clock} – {end_clock}"
        except Exception:
            pass
        return f"{start} – {end}"
    if start != "—":
        return start
    return "—"


def _render_practice_share_page(practice_share):
    target_type = str(practice_share.get("target_type", "RESOURCE")).upper()
    resource = practice_share.get("resource") or {}
    if not isinstance(resource, dict):
        resource = {}
    target_id = practice_share.get("target_id", "")

    if target_type not in ("CELEBRATION", "CELEBRATION_ARTIFACT"):
        return None

    context = _event_context(resource)
    title = str(resource.get("title") or "Celebration").strip()
    artifact = str(resource.get("artifact_type") or "celebration").replace("_", " ").title()
    visibility = str(resource.get("visibility") or resource.get("source_visibility") or "family").title()
    rendered_content = str(
        resource.get("rendered_content")
        or resource.get("rendered_text")
        or resource.get("content")
        or ""
    ).strip()

    rows = [("Celebration", title), ("Artifact", artifact)]
    if context["title"]:
        rows.append(("Source event", context["title"]))
    when = _when_label(context["start_time"], context["end_time"])
    if when != "—":
        rows.append(("When", when))
    if context["description"]:
        rows.append(("Description", context["description"]))
    if context["people"]:
        rows.append(("With", ", ".join(context["people"])))
    rows.append(("Visibility", visibility))
    if target_id:
        rows.append(("Celebration ID", str(target_id)))

    body_rows = "".join(
        '<div class="row">'
        f'<div class="label">{html.escape(label)}</div>'
        f'<div class="value">{html.escape(value)}</div>'
        '</div>'
        for label, value in rows
    )
    content_html = (
        '<div class="content">'
        f'{html.escape(rendered_content)}'
        '</div>'
        if rendered_content
        else ""
    )

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)} — Shared via FEMC</title>
<style>
:root {{ --bg:#0f172a; --card:#1e293b; --border:#334155; --accent:#38bdf8; --text:#f8fafc; --sub:#94a3b8; }}
* {{ box-sizing:border-box; margin:0; padding:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif; }}
body {{ background:var(--bg); color:var(--text); min-height:100vh; }}
header {{ background:var(--card); border-bottom:1px solid var(--border); padding:.85rem 1.5rem; }}
.wrap {{ max-width:760px; margin:2rem auto; padding:0 1.25rem; }}
.card {{ background:var(--card); border:1px solid var(--border); border-radius:12px; padding:1.5rem; }}
.practice {{ margin-bottom:1rem; padding:.65rem .8rem; border-radius:8px; background:rgba(168,85,247,.12); border:1px solid rgba(168,85,247,.35); color:#d8b4fe; font-size:.85rem; }}
.badge {{ display:inline-block; background:rgba(56,189,248,.2); color:var(--accent); font-size:.75rem; font-weight:800; letter-spacing:.06em; padding:.25rem .7rem; border-radius:999px; margin-bottom:.6rem; }}
h1 {{ font-size:1.5rem; margin-bottom:1rem; }}
.row {{ display:flex; gap:12px; padding:8px 0; border-bottom:1px solid rgba(255,255,255,.06); }}
.label {{ min-width:140px; color:var(--sub); font-weight:600; }}
.value {{ flex:1; }}
.content {{ margin-top:14px; padding:12px; background:rgba(0,0,0,.25); border:1px solid var(--border); border-radius:8px; white-space:pre-wrap; line-height:1.55; }}
.note {{ color:var(--sub); font-size:.85rem; margin-top:1rem; }}
@media (max-width:560px) {{ .row {{ display:block; }} .label {{ margin-bottom:4px; }} }}
</style>
</head>
<body>
<header><strong>FEMC</strong> — Family Event &amp; Memory Canvas</header>
<div class="wrap"><div class="card">
<div class="practice">PRACTICE MODE · This is simulated family content.</div>
<span class="badge">CELEBRATION ARTIFACT</span>
<h1>{html.escape(title)}</h1>
{body_rows}
{content_html}
<p class="note">This shared celebration preserves its source event context inside the FEMC Practice World. It does not expose real family data.</p>
</div></div>
</body>
</html>'''


def _enrich_from_practice_world(runtime, practice_share):
    enriched = dict(practice_share or {})
    resource = enriched.get("resource")
    if not isinstance(resource, dict):
        resource = {}
    merged = dict(resource)
    target_id = enriched.get("target_id") or merged.get("id")

    try:
        session_id = runtime.demo_state.session_id
        pw = runtime.demo_state.api.get_practice_world_state_for_session(session_id)
        artifacts = list(getattr(pw, "simulated_celebrations", []) or []) if pw is not None else []
        artifact = next((row for row in artifacts if _same_id(row.get("id"), target_id)), None)
        if artifact is None:
            artifact = next((row for row in artifacts if _same_id(row.get("source_event_id"), target_id)), None)
        if artifact:
            merged = {**artifact, **merged}
            if not merged.get("id"):
                merged["id"] = artifact.get("id")
    except Exception:
        pass

    enriched["resource"] = merged
    return enriched


def install(runtime):
    original = runtime._render_practice_share_page
    if getattr(runtime, "_femc_practice_shared_celebration_context_patch", False):
        return

    def patched(practice_share):
        target_type = str((practice_share or {}).get("target_type", "")).upper()
        if target_type in ("CELEBRATION", "CELEBRATION_ARTIFACT"):
            enriched = _enrich_from_practice_world(runtime, practice_share or {})
            rendered = _render_practice_share_page(enriched)
            if rendered is not None:
                return rendered
        return original(practice_share)

    runtime._render_practice_share_page = patched
    runtime._femc_practice_shared_celebration_context_patch = True


__all__ = ["install"]
