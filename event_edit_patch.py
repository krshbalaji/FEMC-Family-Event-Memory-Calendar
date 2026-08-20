from __future__ import annotations

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


def _set_event_values(event, payload):
    event["title"] = payload.get("title", event.get("title", ""))
    event["description"] = payload.get("description", event.get("description", ""))
    event["category"] = str(payload.get("category", event.get("category", "GENERAL"))).upper()
    event["visibility"] = str(payload.get("visibility", event.get("visibility", "FAMILY"))).upper()
    if "target_person_ids" in payload:
        event["target_person_ids"] = list(payload.get("target_person_ids") or [])

    start_date = str(payload.get("start_date") or event.get("start_date") or event.get("date") or "").strip()
    start_time = str(payload.get("start_time") or "").strip()
    end_date = str(payload.get("end_date") or start_date).strip()
    end_time = str(payload.get("end_time") or "").strip()

    if start_date:
        event["date"] = start_date
        event["start_date"] = start_date
    if start_time:
        event["start_time"] = f"{start_date}T{start_time}:00"
    if end_date:
        event["end_date"] = end_date
    if end_time:
        event["end_time"] = f"{end_date}T{end_time}:00"


def _find_event(pw, event_id=None, title=None):
    if event_id:
        found = next((e for e in pw.simulated_events if e.get("id") == event_id), None)
        if found:
            return found
    if title:
        matches = [e for e in pw.simulated_events if e.get("title") == title]
        if matches:
            return matches[-1]
    return pw.simulated_events[-1] if pw.simulated_events else None


def _install_post_patch(runtime):
    handler = runtime.DemoHTTPRequestHandler
    if getattr(handler, "_femc_event_edit_post_patch", False):
        return

    original_post = handler.do_POST

    def patched_post(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path not in ("/api/events/update", "/api/events/edit"):
            # Let the normal handler process all other requests.
            original_post(self)
            # After Practice event creation, normalize the newly created record with the
            # actual values supplied by the form because the legacy endpoint predates the
            # richer Practice event date/time fields.
            return

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

        event = _find_event(pw, payload.get("event_id") or payload.get("id"), payload.get("title"))
        if event is None:
            self._send_json({"status": "error", "message": "Event not found."}, status=404)
            return

        _set_event_values(event, payload)
        self._send_json({"status": "success", "event": event})

    handler.do_POST = patched_post
    handler._femc_event_edit_post_patch = True


def _install_client_patch(runtime):
    html = runtime.HTML_TEMPLATE
    marker = "FEMC_PRACTICE_EVENT_EDIT_PATCH"
    if marker in html:
        return

    script = r'''<script id="FEMC_PRACTICE_EVENT_EDIT_PATCH">
(() => {
  const originalDetail = window.openEventDetailModal;

  function part(value, index, fallback='') {
    const s = String(value || '');
    if (!s) return fallback;
    return (s.split('T')[index] || '').slice(0, index === 0 ? 10 : 5);
  }

  function addEditButton(eventId) {
    const modal = document.getElementById('modal-container');
    if (!modal) return;
    const buttons = Array.from(modal.querySelectorAll('button'));
    const share = buttons.find(b => (b.textContent || '').includes('Share Event'));
    if (!share || buttons.some(b => (b.textContent || '').includes('Edit Event'))) return;
    const edit = document.createElement('button');
    edit.className = 'btn btn-outline btn-sm';
    edit.textContent = '✏️ Edit Event';
    edit.onclick = () => window.openPracticeEventEditor(eventId);
    share.parentElement.insertBefore(edit, share);
  }

  window.openEventDetailModal = async function(eventId) {
    await originalDetail(eventId);
    setTimeout(() => addEditButton(eventId), 0);
  };

  window.openPracticeEventEditor = async function(eventId) {
    const data = await fetchAPI(`/api/events?event_id=${encodeURIComponent(eventId)}`);
    const ev = data?.event_detail?.event || {};
    const persons = data?.event_detail?.target_persons || [];
    const members = window.membersData || [];
    const checkedIds = new Set(persons.map(p => p.person_id));
    const start = ev.start_time || '';
    const end = ev.end_time || '';
    const memberCheckboxes = members.map(m => `
      <label class="checkbox-item">
        <input type="checkbox" name="edit_target_persons" value="${m.person_id}" ${checkedIds.has(m.person_id) ? 'checked' : ''} />
        ${m.name} (${m.email})
      </label>
    `).join('');

    const container = document.getElementById('modal-container');
    container.innerHTML = `
      <div class="modal-overlay">
        <div class="modal-card">
          <div class="card-header">
            <div class="card-title">✏️ Edit Family Event</div>
            <button class="btn btn-outline" style="padding:0.2rem 0.5rem;" onclick="closeModal()">✕</button>
          </div>
          <form onsubmit="submitPracticeEventEdit(event, '${eventId}')">
            <div class="form-group"><label class="form-label">Event Title</label><input id="edit-evt-title" class="form-input" required value="${String(ev.title || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}" /></div>
            <div class="form-group"><label class="form-label">Category</label>
              <select id="edit-evt-cat" class="form-select">
                ${['GENERAL','BIRTHDAY','ANNIVERSARY','MILESTONE'].map(x => `<option value="${x}" ${String(ev.category || 'GENERAL').toUpperCase() === x ? 'selected' : ''}>${x[0] + x.slice(1).toLowerCase()}</option>`).join('')}
              </select>
            </div>
            <div class="form-group"><label class="form-label">Start Date</label><input type="date" id="edit-evt-start-date" class="form-input" required value="${part(start,0)}" /></div>
            <div class="form-group"><label class="form-label">Start Time</label><input type="time" id="edit-evt-start-time" class="form-input" required value="${part(start,1)}" /></div>
            <div class="form-group"><label class="form-label">End Date</label><input type="date" id="edit-evt-end-date" class="form-input" required value="${part(end,0,part(start,0))}" /></div>
            <div class="form-group"><label class="form-label">End Time</label><input type="time" id="edit-evt-end-time" class="form-input" required value="${part(end,1)}" /></div>
            <div class="form-group"><label class="form-label">Target Family Member(s)</label><div class="checkbox-group">${memberCheckboxes}</div></div>
            <div class="form-group"><label class="form-label">Visibility</label>
              <select id="edit-evt-vis" class="form-select">
                <option value="FAMILY" ${String(ev.visibility || 'family').toUpperCase() === 'FAMILY' ? 'selected' : ''}>Family Visible (All Members)</option>
                <option value="PRIVATE" ${String(ev.visibility || '').toUpperCase() === 'PRIVATE' ? 'selected' : ''}>Private (Only You)</option>
              </select>
            </div>
            <div class="form-group"><label class="form-label">Description</label><input id="edit-evt-desc" class="form-input" value="${String(ev.description || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}" /></div>
            <div style="display:flex;justify-content:flex-end;gap:.5rem;margin-top:1.5rem;">
              <button type="button" class="btn btn-outline" onclick="closeModal()">Cancel</button>
              <button type="submit" class="btn">Save Changes</button>
            </div>
          </form>
        </div>
      </div>`;
    container.style.display = 'block';
  };

  window.submitPracticeEventEdit = async function(evt, eventId) {
    evt.preventDefault();
    const startDate = document.getElementById('edit-evt-start-date').value;
    const startTime = document.getElementById('edit-evt-start-time').value;
    const endDate = document.getElementById('edit-evt-end-date').value;
    const endTime = document.getElementById('edit-evt-end-time').value;
    const start = new Date(`${startDate}T${startTime}`);
    const end = new Date(`${endDate}T${endTime}`);
    if (!(start.getTime() < end.getTime())) {
      alert('End date/time must be after start date/time.');
      return;
    }
    const ids = Array.from(document.querySelectorAll('input[name="edit_target_persons"]:checked')).map(x => x.value);
    await fetchAPI('/api/events/update', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        event_id: eventId,
        title: document.getElementById('edit-evt-title').value.trim(),
        category: document.getElementById('edit-evt-cat').value,
        visibility: document.getElementById('edit-evt-vis').value,
        description: document.getElementById('edit-evt-desc').value.trim(),
        target_person_ids: ids,
        start_date: startDate,
        start_time: startTime,
        end_date: endDate,
        end_time: endTime
      })
    });
    closeModal();
    await loadView('calendar');
  };
})();
</script>'''
    runtime.HTML_TEMPLATE = html.replace('</body>', script + '\n</body>')


def _repair_newest_event(runtime, payload):
    pw = _practice_state(runtime)
    if pw is None:
        return
    event = _find_event(pw, None, payload.get("title"))
    if event is not None:
        _set_event_values(event, payload)


def install(runtime):
    _install_post_patch(runtime)
    _install_client_patch(runtime)


__all__ = ["install", "_repair_newest_event"]
