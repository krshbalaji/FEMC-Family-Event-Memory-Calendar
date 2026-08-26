from __future__ import annotations

import datetime
import json
from urllib.parse import urlparse

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None


def _today():
    if ZoneInfo is not None:
        try:
            return datetime.datetime.now(ZoneInfo("Asia/Kolkata")).date()
        except Exception:
            pass
    return datetime.date.today()


def _is_practice(api, session_id):
    try:
        state = api.get_guided_experience_state_for_session(session_id)
        return bool(state and getattr(getattr(state, "current_mode", None), "value", "") == "learn_by_doing")
    except Exception:
        return False


def _read_json(handler):
    length = int(handler.headers.get("Content-Length", 0))
    raw = handler.rfile.read(length).decode("utf-8") if length else "{}"
    try:
        return json.loads(raw)
    except Exception:
        return {}


def _parse_date(value):
    try:
        return datetime.date.fromisoformat(str(value)[:10])
    except Exception:
        return None


def install(runtime):
    if getattr(runtime, "_FEMC_PRACTICE_RUNTIME_FIX_V1", False):
        return
    runtime._FEMC_PRACTICE_RUNTIME_FIX_V1 = True

    html = runtime.HTML_TEMPLATE
    marker = "FEMC_PRACTICE_RUNTIME_FIX_V1"
    if marker not in html:
        script = r'''<script id="FEMC_PRACTICE_RUNTIME_FIX_V1">
(() => {
  const esc = v => String(v ?? '').replace(/[&<>\"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const localToday = () => {
    const parts = new Intl.DateTimeFormat('en-CA', {timeZone: window.FEMC_TIME_ZONE || Intl.DateTimeFormat().resolvedOptions().timeZone || 'Asia/Kolkata', year:'numeric', month:'2-digit', day:'2-digit'}).formatToParts(new Date());
    const p = {}; parts.forEach(x => { if (x.type !== 'literal') p[x.type] = x.value; });
    return `${p.year}-${p.month}-${p.day}`;
  };
  const prettyDate = iso => {
    if (!iso) return '';
    const d = new Date(`${String(iso).slice(0,10)}T12:00:00`);
    return isNaN(d.getTime()) ? String(iso) : d.toLocaleDateString(undefined,{weekday:'long',year:'numeric',month:'long',day:'numeric'});
  };

  window.openPracticeReminderEditor = function(id, title, dueDate) {
    const c = document.getElementById('modal-container');
    if (!c) return;
    c.innerHTML = `<div class="modal-overlay"><div class="modal-card" style="max-width:560px;"><div class="card-header"><div class="card-title">🔔 Edit Reminder</div><button class="btn btn-outline btn-sm" id="femc-rem-close">✕</button></div><div class="form-group"><label class="form-label">Reminder</label><input id="femc-rem-title" class="form-input" value="${esc(title)}"></div><div class="form-group"><label class="form-label">Due date</label><input id="femc-rem-date" class="form-input" type="date" value="${esc(dueDate)}"></div><div style="font-size:.8rem;color:var(--text-sub);margin-bottom:1rem;">Mayil will keep the reminder in the correct time context. Past reminders are not shown as active.</div><div style="display:flex;justify-content:flex-end;gap:.5rem;"><button class="btn btn-outline" id="femc-rem-cancel">Cancel</button><button class="btn" id="femc-rem-save">Save Reminder</button></div></div></div>`;
    c.style.display = 'block';
    const close = () => closeModal();
    document.getElementById('femc-rem-close').onclick = close;
    document.getElementById('femc-rem-cancel').onclick = close;
    document.getElementById('femc-rem-save').onclick = async () => {
      const newTitle = document.getElementById('femc-rem-title').value.trim();
      const newDate = document.getElementById('femc-rem-date').value;
      if (!newTitle || !newDate) { alert('Please enter both the reminder and due date.'); return; }
      const res = await fetchAPI('/api/reminders/update', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({reminder_id:id,title:newTitle,due_date:newDate})});
      if (res && res.status === 'success') { closeModal(); await loadView('reminders'); }
      else alert((res && res.message) || 'Reminder could not be saved.');
    };
  };

  window.renderReminders = async function(container) {
    const data = await fetchAPI('/api/reminders');
    const reminders = data.reminders || [];
    const notifications = data.notifications || [];
    const triggered = data.triggered || [];
    container.innerHTML = `
      <div class="page-header"><div><h1 class="section-title">🔔 Reminders & Notifications</h1><div class="section-subtitle">Time-aware family reminders and alerts</div></div></div>
      <div class="card" style="margin-bottom:1.5rem;"><div class="card-header"><div class="card-title">Scheduled Reminders</div><span class="pill pill-general">${reminders.length} Active</span></div><div class="item-list">${reminders.length ? reminders.map(r => `<div class="item-row"><div><div class="item-main">${esc(r.title)}</div><div class="item-sub">Due: ${esc(prettyDate(r.due_date))}</div></div><button class="btn btn-sm btn-outline" onclick="openPracticeReminderEditor('${esc(r.id)}','${esc(r.title).replace(/'/g,'&#39;')}','${esc(r.due_date)}')">✏️ Edit</button></div>`).join('') : '<div class="item-sub">No active reminders. Past reminders are automatically kept out of the active list.</div>'}</div></div>
      <div class="card" style="margin-bottom:1.5rem;"><div class="card-header"><div class="card-title">Active Notifications</div><span class="pill pill-birthday">${notifications.length} Notifications</span></div><div class="item-list">${notifications.length ? notifications.map(n => `<div class="item-row"><div><div class="item-main">${esc(n.title)}</div><div class="item-sub">${esc(n.message)}</div></div>${n.status === 'read' ? '<span class="pill pill-health">READ</span>' : `<button class="btn btn-sm btn-pink" onclick="markNotificationRead('${esc(n.id)}')">Mark Read</button>`}</div>`).join('') : '<div class="item-sub">No active notifications.</div>'}</div></div>
      <div class="card"><div class="card-header"><div class="card-title">Triggered Due Reminders</div><span class="pill pill-general">${triggered.length} Evaluated</span></div><div class="item-list">${triggered.length ? triggered.map(t => `<div class="item-row"><div><div class="item-main">${esc(t.title)}</div><div class="item-sub">${esc(t.message)}</div></div><span class="pill pill-milestone">DUE</span></div>`).join('') : '<div class="item-sub">No due reminders triggered at this time.</div>'}</div></div>`;
  };
})();
</script>'''
        runtime.HTML_TEMPLATE = html.replace('</body>', script + '\n</body>')

    original_get = runtime.DemoHTTPRequestHandler.do_GET
    original_post = runtime.DemoHTTPRequestHandler.do_POST

    def patched_get(self):
        parsed = urlparse(self.path)
        path = parsed.path
        api = runtime.demo_state.api
        session_id = runtime.demo_state.session_id
        fc_id = runtime.demo_state.family_context.id

        if path == '/api/dashboard' and _is_practice(api, session_id):
            pw = api.get_practice_world_state_for_session(session_id)
            today = _today()
            entries = []
            for event in (getattr(pw, 'simulated_events', None) or []):
                event_date = _parse_date(event.get('date'))
                if event_date is None or event_date < today:
                    continue
                entries.append({
                    'item_type': 'upcoming_event',
                    'entry_type': 'upcoming_event',
                    'title': event.get('title', 'Family Event'),
                    'description': event.get('description', ''),
                    'date': event_date.isoformat(),
                    'date_or_time': event_date.isoformat(),
                    'category': event.get('category', 'GENERAL'),
                    'visibility': event.get('visibility', 'FAMILY'),
                    'event_id': event.get('id'),
                })
            for reminder in (getattr(pw, 'simulated_reminders', None) or []):
                due = _parse_date(reminder.get('due_date'))
                if due is None or due < today:
                    continue
                entries.append({
                    'item_type': 'reminder_due',
                    'entry_type': 'reminder_due',
                    'title': reminder.get('title', 'Reminder'),
                    'description': f'Due {due.isoformat()}',
                    'date': due.isoformat(),
                    'date_or_time': due.isoformat(),
                    'reminder_id': reminder.get('id'),
                })
            for memory in (getattr(pw, 'simulated_memories', None) or []):
                entries.append({'item_type':'recent_memory','entry_type':'recent_memory','title':memory.get('title','Family Memory'),'description':memory.get('summary') or memory.get('narrative','')})
            for celebration in (getattr(pw, 'simulated_celebrations', None) or []):
                entries.append({'item_type':'celebration_highlight','entry_type':'celebration_highlight','title':celebration.get('title','Celebration'),'description':'Practice celebration artifact'})
            self._send_json({'summary': {'is_practice': True}, 'entries': entries})
            return

        if path == '/api/reminders' and _is_practice(api, session_id):
            pw = api.get_practice_world_state_for_session(session_id)
            today = _today()
            reminders = []
            for reminder in (getattr(pw, 'simulated_reminders', None) or []):
                due = _parse_date(reminder.get('due_date'))
                if due is None or due < today:
                    continue
                reminders.append({'id': reminder.get('id'), 'title': reminder.get('title', 'Reminder'), 'due_date': due.isoformat()})
            self._send_json({'notifications': [], 'triggered': [], 'reminders': reminders})
            return

        return original_get(self)

    def patched_post(self):
        parsed = urlparse(self.path)
        path = parsed.path
        api = runtime.demo_state.api
        session_id = runtime.demo_state.session_id
        fc_id = runtime.demo_state.family_context.id

        if path in ('/api/events/create', '/api/events/update', '/api/reminders/update'):
            payload = _read_json(self)
            if path == '/api/events/create':
                title = str(payload.get('title', '')).strip()
                start_date = str(payload.get('start_date') or payload.get('date') or '').strip()
                if not title or not start_date:
                    self._send_json({'status':'error','message':'Event title and start date are required.'}, status=400)
                    return
                if _is_practice(api, session_id):
                    action_payload = dict(payload)
                    action_payload['date'] = start_date
                    action_payload['start_date'] = start_date
                    action_payload['category'] = str(payload.get('category','GENERAL')).upper()
                    action_payload['visibility'] = str(payload.get('visibility','FAMILY')).upper()
                    res = api.execute_simulated_action_for_session(session_id, runtime.ActionType.CREATE, 'btn-create-event', runtime.ResourceType.EVENT, action_payload)
                    event = (res or {}).get('event') if isinstance(res, dict) else None
                    self._send_json({'status':'success','event': runtime.to_dict(event) if event is not None else None})
                    return
                try:
                    start = datetime.datetime.fromisoformat(f"{start_date}T{payload.get('start_time') or '00:00'}")
                    end_date = payload.get('end_date') or start_date
                    end = datetime.datetime.fromisoformat(f"{end_date}T{payload.get('end_time') or payload.get('start_time') or '00:00'}")
                    cat = runtime.EventCategory(str(payload.get('category','GENERAL')).lower())
                    vis = runtime.VisibilityLevel(str(payload.get('visibility','FAMILY')).lower())
                    event = api.create_event_for_session(session_id, title, payload.get('description',''), fc_id, start, end, visibility=vis, category=cat, target_person_ids=payload.get('target_person_ids') or [])
                    self._send_json({'status':'success','event':runtime.to_dict(event)})
                except Exception as exc:
                    self._send_json({'status':'error','message':str(exc)}, status=400)
                return

            if path == '/api/events/update':
                event_id = str(payload.get('event_id') or '')
                if _is_practice(api, session_id):
                    pw = api.get_practice_world_state_for_session(session_id)
                    event = next((e for e in (getattr(pw, 'simulated_events', None) or []) if str(e.get('id')) == event_id), None)
                    if event is None:
                        self._send_json({'status':'error','message':'Practice event not found.'}, status=404)
                        return
                    for key in ('title','description','category','visibility','start_date','start_time','end_date','end_time','target_person_ids'):
                        if key in payload:
                            event[key] = payload[key]
                    if payload.get('start_date'):
                        event['date'] = payload['start_date']
                    self._send_json({'status':'success','event':event})
                    return
                self._send_json({'status':'error','message':'Event update is not available in this demo path.'}, status=501)
                return

            reminder_id = str(payload.get('reminder_id') or '')
            if _is_practice(api, session_id):
                pw = api.get_practice_world_state_for_session(session_id)
                reminder = next((r for r in (getattr(pw, 'simulated_reminders', None) or []) if str(r.get('id')) == reminder_id), None)
                if reminder is None:
                    self._send_json({'status':'error','message':'Practice reminder not found.'}, status=404)
                    return
                title = str(payload.get('title') or '').strip()
                due_date = str(payload.get('due_date') or '')
                if not title or _parse_date(due_date) is None:
                    self._send_json({'status':'error','message':'A reminder title and valid date are required.'}, status=400)
                    return
                reminder['title'] = title
                reminder['due_date'] = due_date[:10]
                self._send_json({'status':'success','reminder':reminder})
                return
            self._send_json({'status':'error','message':'Reminder update is not available in this demo path.'}, status=501)
            return

        return original_post(self)

    runtime.DemoHTTPRequestHandler.do_GET = patched_get
    runtime.DemoHTTPRequestHandler.do_POST = patched_post


__all__ = ['install']
