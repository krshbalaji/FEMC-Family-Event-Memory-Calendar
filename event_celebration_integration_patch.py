from __future__ import annotations

import datetime
import json
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


def _find_event(pw, event_id):
    return next((e for e in getattr(pw, "simulated_events", []) if e.get("id") == event_id), None)


def _iso_parts(value):
    text = str(value or "").strip()
    if not text:
        return "", ""
    if "T" not in text:
        return text[:10], ""
    date, time = text.split("T", 1)
    return date[:10], time[:5]


def _friendly_date(date_text):
    if not date_text:
        return "Date not specified"
    try:
        return datetime.date.fromisoformat(date_text[:10]).strftime("%A, %d %B %Y")
    except Exception:
        return date_text


def _friendly_time(time_text):
    if not time_text:
        return ""
    try:
        return datetime.datetime.strptime(time_text[:5], "%H:%M").strftime("%I:%M %p").lstrip("0")
    except Exception:
        return time_text


def _artifact_type(category):
    category = str(category or "GENERAL").upper()
    return {
        "BIRTHDAY": "birthday_card",
        "ANNIVERSARY": "anniversary_card",
        "MILESTONE": "milestone_card",
    }.get(category, "event_highlight")


def _build_artifact(pw, event):
    start_date, start_clock = _iso_parts(event.get("start_time"))
    if not start_date:
        start_date = str(event.get("start_date") or event.get("date") or "")[:10]
    end_date, end_clock = _iso_parts(event.get("end_time"))
    if not end_date:
        end_date = str(event.get("end_date") or start_date)[:10]

    member_names = []
    ids = list(event.get("target_person_ids") or [])
    for person_id in ids:
        person = next((p for p in getattr(pw, "simulated_persons", []) if p.get("id") == person_id), None)
        if person and person.get("name"):
            member_names.append(person["name"])

    when = _friendly_date(start_date)
    start_label = _friendly_time(start_clock)
    end_label = _friendly_time(end_clock)
    if start_label and end_label:
        when = f"{when} · {start_label} – {end_label}"
    elif start_label:
        when = f"{when} · {start_label} onwards"

    description = str(event.get("description") or "").strip()
    title = str(event.get("title") or "Family Event").strip()
    lines = [when]
    if description:
        lines.append(description)
    if member_names:
        lines.append("With: " + ", ".join(member_names))

    return {
        "id": None,
        "artifact_type": _artifact_type(event.get("category")),
        "title": f"{title} Celebration",
        "subtitle": description or f"A celebration created from the {title} event.",
        "rendered_content": "\n".join(lines),
        "content": "\n".join(lines),
        "family_context_id": getattr(pw, "family_context_id", ""),
        "source_event_id": event.get("id"),
        "source_title": title,
        "source_description": description,
        "source_category": str(event.get("category") or "GENERAL").upper(),
        "source_visibility": str(event.get("visibility") or "FAMILY").upper(),
        "visibility": str(event.get("visibility") or "FAMILY").lower(),
        "target_person_ids": ids,
        "target_person_names": member_names,
        "start_time": event.get("start_time"),
        "end_time": event.get("end_time"),
        "date": start_date,
        "created_from": "event",
    }


def _install_post_patch(runtime):
    handler = runtime.DemoHTTPRequestHandler
    if getattr(handler, "_femc_event_celebration_post_patch", False):
        return

    original_post = handler.do_POST

    def patched_post(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/practice/celebrations/from-event":
            return original_post(self)

        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            payload = json.loads(raw)
        except Exception:
            payload = {}

        pw = _practice_state(runtime)
        if pw is None:
            self._send_json({"status": "error", "message": "Practice World is not active."}, status=409)
            return

        event = _find_event(pw, payload.get("event_id"))
        if event is None:
            self._send_json({"status": "error", "message": "Source event not found."}, status=404)
            return

        artifacts = getattr(pw, "simulated_celebrations", None)
        if artifacts is None:
            artifacts = []
            pw.simulated_celebrations = artifacts

        artifact = _build_artifact(pw, event)
        existing = next((a for a in artifacts if a.get("source_event_id") == event.get("id")), None)
        if existing is not None:
            artifact["id"] = existing.get("id") or f"sim_celebration_{event.get('id')}"
            existing.clear()
            existing.update(artifact)
            artifact = existing
        else:
            artifact["id"] = f"sim_celebration_{event.get('id')}"
            artifacts.append(artifact)

        self._send_json({"status": "success", "artifact": artifact})

    handler.do_POST = patched_post
    handler._femc_event_celebration_post_patch = True


def _install_client_patch(runtime):
    html = runtime.HTML_TEMPLATE
    marker = "FEMC_EVENT_CELEBRATION_INTEGRATION_PATCH"
    if marker in html:
        return

    script = r'''<script id="FEMC_EVENT_CELEBRATION_INTEGRATION_PATCH">
(() => {
  const originalDetail = window.openEventDetailModal;

  function wireCreateCelebration(eventId) {
    const modal = document.getElementById('modal-container');
    if (!modal) return;
    const button = Array.from(modal.querySelectorAll('button')).find(b =>
      (b.textContent || '').trim().includes('Create Celebration')
    );
    if (!button || button.dataset.femcCelebrationWired === 'true') return;

    button.dataset.femcCelebrationWired = 'true';
    const replacement = button.cloneNode(true);
    replacement.dataset.femcCelebrationWired = 'true';
    replacement.onclick = async (evt) => {
      evt.preventDefault();
      evt.stopPropagation();
      replacement.disabled = true;
      try {
        const result = await fetchAPI('/api/practice/celebrations/from-event', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({event_id: eventId})
        });
        if (!result || result.status !== 'success') {
          throw new Error(result?.message || 'Unable to create celebration.');
        }
        closeModal();
        await loadView('celebrations');
      } catch (error) {
        alert(error.message || 'Unable to create celebration.');
      } finally {
        replacement.disabled = false;
      }
    };
    button.replaceWith(replacement);
  }

  window.openEventDetailModal = async function(eventId) {
    await originalDetail(eventId);
    setTimeout(() => wireCreateCelebration(eventId), 0);
  };
})();
</script>'''
    runtime.HTML_TEMPLATE = html.replace('</body>', script + '\n</body>')


def install(runtime):
    _install_post_patch(runtime)
    _install_client_patch(runtime)


__all__ = ["install"]
