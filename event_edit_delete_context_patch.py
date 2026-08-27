from __future__ import annotations

import json
from urllib.parse import urlparse


def _read_json(handler):
    try:
        length = int(handler.headers.get("Content-Length", 0))
    except Exception:
        length = 0
    raw = handler.rfile.read(length).decode("utf-8") if length else "{}"
    try:
        return json.loads(raw)
    except Exception:
        return {}


def _practice_state(runtime):
    try:
        sid = runtime.demo_state.session_id
        api = runtime.demo_state.api
        state = api.get_guided_experience_state_for_session(sid)
        mode = getattr(getattr(state, "current_mode", None), "value", "")
        if mode != "learn_by_doing":
            return None
        pw = api.get_practice_world_state_for_session(sid)
        return pw if pw and getattr(pw, "is_active", False) else None
    except Exception:
        return None


def _events(runtime):
    pw = _practice_state(runtime)
    if pw is None:
        return []
    return getattr(pw, "simulated_events", None) or []


def _find(runtime, event_id):
    sid = str(event_id or "")
    return next((e for e in _events(runtime) if str(e.get("id") or e.get("event_id") or "") == sid), None)


def install(runtime):
    if getattr(runtime, "_FEMC_EVENT_EDIT_DELETE_CONTEXT_V1", False):
        return
    runtime._FEMC_EVENT_EDIT_DELETE_CONTEXT_V1 = True

    handler = runtime.DemoHTTPRequestHandler
    previous_get = handler.do_GET
    previous_post = handler.do_POST

    def send_event(self, event):
        self._send_json({"status": "success", "event": event})

    def patched_get(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/events/detail":
            from urllib.parse import parse_qs
            q = parse_qs(parsed.query)
            event = _find(runtime, (q.get("event_id") or [""])[0])
            if event is None:
                self._send_json({"status": "error", "message": "Event not found."}, status=404)
                return
            self._send_json({"status": "success", "event": dict(event)})
            return
        return previous_get(self)

    def patched_post(self):
        path = urlparse(self.path).path
        if path not in ("/api/events/update", "/api/events/delete"):
            return previous_post(self)

        payload = _read_json(self)
        event_id = payload.get("event_id") or payload.get("id")
        event = _find(runtime, event_id)
        if event is None:
            self._send_json({"status": "error", "message": "Event not found."}, status=404)
            return
        if path == "/api/events/delete":
            events = _events(runtime)
            events[:] = [e for e in events if str(e.get("id") or e.get("event_id") or "") != str(event_id)]
            self._send_json({"status": "success", "deleted_event_id": str(event_id)})
            return

        for key in ("title", "description", "venue"):
            if key in payload:
                event[key] = str(payload.get(key) or "").strip()
        for key in ("category", "visibility"):
            if key in payload:
                event[key] = str(payload.get(key) or "GENERAL").upper()
        for key in ("start_date", "end_date", "start_time", "end_time", "time_zone"):
            if key in payload:
                event[key] = str(payload.get(key) or "").strip()
        if payload.get("start_date"):
            event["date"] = payload["start_date"]
        if "target_person_ids" in payload:
            event["target_person_ids"] = list(payload.get("target_person_ids") or [])
            event["person_ids"] = list(event["target_person_ids"])
        send_event(self, event)

    handler.do_GET = patched_get
    handler.do_POST = patched_post

    html = runtime.HTML_TEMPLATE
    marker = "FEMC_EVENT_EDIT_DELETE_CONTEXT_V1"
    if marker in html:
        return

    script = r'''<script id="FEMC_EVENT_EDIT_DELETE_CONTEXT_V1">
(() => {
  const esc = v => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const jget = async (url) => { const r=await fetch(url,{credentials:'same-origin'}); return r.ok ? r.json() : null; };
  const getEvents = async () => { try { const d=await jget('/api/events'); return d?.events || d?.calendar || d?.items || []; } catch(_) { return []; } };
  const byId = async id => { try { const d=await jget('/api/events/detail?event_id='+encodeURIComponent(id)); return d?.event || null; } catch(_) { return null; } };
  const value = id => document.getElementById(id)?.value || '';

  async function openEditorInPlace(eventId) {
    const ev = await byId(eventId);
    if (!ev) { alert('The selected event could not be found.'); return; }
    const c=document.getElementById('modal-container');
    c.innerHTML=`<div class="modal-overlay"><div class="modal-card" style="max-width:720px;max-height:90vh;overflow:auto;"><div class="card-header"><div class="card-title">✏️ Edit Family Event</div><button class="btn btn-outline btn-sm" id="femc-edit-close">✕</button></div>
      <div class="form-group"><label class="form-label">Event Title</label><input id="femc-edit-title" class="form-input" value="${esc(ev.title)}"></div>
      <div class="form-group"><label class="form-label">Category</label><select id="femc-edit-cat" class="form-select"><option value="GENERAL">General</option><option value="BIRTHDAY">Birthday</option><option value="ANNIVERSARY">Anniversary</option><option value="MILESTONE">Milestone</option></select></div>
      <div class="form-group"><label class="form-label">Start Date</label><input id="femc-edit-sd" type="date" class="form-input" value="${esc((ev.start_date||ev.date||'').slice(0,10))}"></div>
      <div class="form-group"><label class="form-label">Start Time</label><input id="femc-edit-st" type="time" class="form-input" value="${esc(String(ev.start_time||'').slice(-5))}"></div>
      <div class="form-group"><label class="form-label">End Date</label><input id="femc-edit-ed" type="date" class="form-input" value="${esc((ev.end_date||ev.start_date||ev.date||'').slice(0,10))}"></div>
      <div class="form-group"><label class="form-label">End Time</label><input id="femc-edit-et" type="time" class="form-input" value="${esc(String(ev.end_time||'').slice(-5))}"></div>
      <div class="form-group"><label class="form-label">📍 Venue <span style="opacity:.65">(optional)</span></label><input id="femc-edit-venue" class="form-input" placeholder="Enter venue, home, or location" value="${esc(ev.venue)}"></div>
      <div class="form-group"><label class="form-label">Visibility</label><select id="femc-edit-vis" class="form-select"><option value="FAMILY">Family Visible (All Members)</option><option value="PRIVATE">Private (Only You)</option></select></div>
      <div class="form-group"><label class="form-label">Description</label><input id="femc-edit-desc" class="form-input" value="${esc(ev.description)}"></div>
      <div style="display:flex;justify-content:space-between;gap:.5rem;margin-top:1.5rem;"><button class="btn btn-outline" id="femc-event-delete">🗑 Delete Event</button><div style="display:flex;gap:.5rem;"><button class="btn btn-outline" id="femc-event-cancel">Cancel</button><button class="btn" id="femc-event-save">Save Changes</button></div></div></div></div>`;
    c.style.display='block';
    document.getElementById('femc-edit-cat').value=String(ev.category||'GENERAL').toUpperCase();
    document.getElementById('femc-edit-vis').value=String(ev.visibility||'FAMILY').toUpperCase();
    document.getElementById('femc-edit-close').onclick=()=>closeModal();
    document.getElementById('femc-event-cancel').onclick=()=>closeModal();
    document.getElementById('femc-event-save').onclick=async()=>{
      const payload={event_id:eventId,title:value('femc-edit-title').trim(),category:value('femc-edit-cat'),start_date:value('femc-edit-sd'),start_time:value('femc-edit-st'),end_date:value('femc-edit-ed'),end_time:value('femc-edit-et'),venue:value('femc-edit-venue').trim(),visibility:value('femc-edit-vis'),description:value('femc-edit-desc').trim()};
      if(!payload.title){alert('Please enter an event title.');return;}
      if(!payload.start_date || !payload.start_time || !payload.end_date || !payload.end_time){alert('Please complete the date and time.');return;}
      const r=await fetch('/api/events/update',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); const d=await r.json().catch(()=>({}));
      if(!r.ok || d.status!=='success'){alert(d.message||'Event could not be updated.');return;}
      closeModal(); window.__femcEditingEventId=null; window.dispatchEvent(new CustomEvent('femc:event-updated',{detail:d.event})); if(typeof loadView==='function') await loadView('calendar');
    };
    document.getElementById('femc-event-delete').onclick=async()=>{
      if(!confirm(`Delete "${ev.title}"? This removes the recorded event from the Practice World.`)) return;
      const r=await fetch('/api/events/delete',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify({event_id:eventId})}); const d=await r.json().catch(()=>({}));
      if(!r.ok || d.status!=='success'){alert(d.message||'Event could not be deleted.');return;}
      closeModal(); window.__femcEditingEventId=null; window.dispatchEvent(new CustomEvent('femc:event-deleted',{detail:{event_id:eventId}})); if(typeof loadView==='function') await loadView('calendar');
    };
  }

  const install = () => {
    const current = window.openPracticeEventEditor;
    if (typeof current === 'function' && !current.__femcContextV1) {
      const wrapped = async id => { window.__femcEditingEventId=String(id); return openEditorInPlace(id); };
      wrapped.__femcContextV1=true; window.openPracticeEventEditor=wrapped;
    }
    document.querySelectorAll('[onclick*="openPracticeEventEditor"]').forEach(b=>b.addEventListener('click',()=>{}));
  };
  install(); setInterval(install,400);
})();
</script>'''
    runtime.HTML_TEMPLATE = html.replace('</body>', script + '\n</body>')


__all__=['install']
