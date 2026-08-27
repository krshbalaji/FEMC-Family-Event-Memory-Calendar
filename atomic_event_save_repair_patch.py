from __future__ import annotations

import datetime
import json
from urllib.parse import urlparse


def _read_json(handler):
    try:
        length = int(handler.headers.get('Content-Length', 0))
    except Exception:
        length = 0
    raw = handler.rfile.read(length).decode('utf-8') if length else '{}'
    try:
        return json.loads(raw)
    except Exception:
        return {}


def _store(runtime):
    api = runtime.demo_state.api
    session_id = runtime.demo_state.session_id
    try:
        world = api.get_practice_world_state_for_session(session_id)
        events = getattr(world, 'simulated_events', None)
        if events is None:
            events = []
            setattr(world, 'simulated_events', events)
        return events
    except Exception:
        events = getattr(runtime.demo_state, '_femc_atomic_events', None)
        if events is None:
            events = []
            setattr(runtime.demo_state, '_femc_atomic_events', events)
        return events


def install(runtime):
    if getattr(runtime, '_FEMC_ATOMIC_EVENT_SAVE_REPAIR_V1', False):
        return
    runtime._FEMC_ATOMIC_EVENT_SAVE_REPAIR_V1 = True

    previous_get = runtime.DemoHTTPRequestHandler.do_GET
    previous_post = runtime.DemoHTTPRequestHandler.do_POST

    def patched_get(self):
        if urlparse(self.path).path == '/api/events':
            events = [dict(event) for event in _store(runtime)]
            self._send_json({'calendar': events, 'events': events, 'items': events})
            return
        return previous_get(self)

    def patched_post(self):
        path = urlparse(self.path).path
        if path in ('/api/events', '/api/events/create'):
            payload = _read_json(self)
            title = str(payload.get('title') or '').strip()
            start_date = str(payload.get('start_date') or payload.get('date') or '').strip()[:10]
            if not title:
                self._send_json({'status': 'error', 'message': 'Please enter an event title.'}, status=400)
                return
            try:
                datetime.date.fromisoformat(start_date)
            except Exception:
                self._send_json({'status': 'error', 'message': 'Please choose a valid event date.'}, status=400)
                return

            events = _store(runtime)
            existing_ids = {str(e.get('id') or e.get('event_id') or '') for e in events}
            n = len(events) + 1
            event_id = f'sim_event_user_{n}'
            while event_id in existing_ids:
                n += 1
                event_id = f'sim_event_user_{n}'

            event = {
                'id': event_id,
                'event_id': event_id,
                'title': title,
                'description': str(payload.get('description') or ''),
                'category': str(payload.get('category') or 'GENERAL').upper(),
                'visibility': str(payload.get('visibility') or 'FAMILY').upper(),
                'date': start_date,
                'start_date': start_date,
                'start_time': str(payload.get('start_time') or ''),
                'end_date': str(payload.get('end_date') or start_date)[:10],
                'end_time': str(payload.get('end_time') or ''),
                'target_person_ids': list(payload.get('target_person_ids') or payload.get('person_ids') or []),
                'person_ids': list(payload.get('target_person_ids') or payload.get('person_ids') or []),
                'time_zone': str(payload.get('time_zone') or 'Asia/Kolkata'),
                'created_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }
            events.append(event)
            self._send_json({'status': 'success', 'event': event})
            return
        return previous_post(self)

    runtime.DemoHTTPRequestHandler.do_GET = patched_get
    runtime.DemoHTTPRequestHandler.do_POST = patched_post

    marker = 'FEMC_ATOMIC_EVENT_SAVE_REPAIR_V1'
    if marker in runtime.HTML_TEMPLATE:
        return

    script = r'''<script id="FEMC_ATOMIC_EVENT_SAVE_REPAIR_V1">
(() => {
  const DRAFT_KEY = 'femc.eventSchedulerDraft.v5';
  const esc = v => String(v ?? '').replace(/[&<>\"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const tz = () => window.FEMC_TIME_ZONE || Intl.DateTimeFormat().resolvedOptions().timeZone || 'Asia/Kolkata';
  const todayISO = () => new Intl.DateTimeFormat('en-CA',{timeZone:tz(),year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date()).split('/').reverse().join('-');
  const longDate = iso => { try { return new Intl.DateTimeFormat('en-US',{timeZone:tz(),weekday:'long',year:'numeric',month:'long',day:'numeric'}).format(new Date(`${iso}T12:00:00`)); } catch (_) { return iso; } };
  const relative = iso => { const a = Date.UTC(...String(iso).split('-').map((x,i)=>i===1?Number(x)-1:Number(x))); const b = Date.UTC(...todayISO().split('-').map((x,i)=>i===1?Number(x)-1:Number(x))); const d = Math.round((a-b)/86400000); return d===0 ? 'Today' : d>0 ? `In ${d} day${d===1?'':'s'}` : `${Math.abs(d)} day${Math.abs(d)===1?'':'s'} ago`; };
  const field = id => document.getElementById(id);
  const capture = () => ({
    mode:'create',
    title:(field('evt-title')?.value||'').trim(),
    category:field('evt-cat')?.value||'GENERAL',
    start_date:field('evt-start-date')?.value||'',
    start_time:field('evt-start-time')?.value||'',
    end_date:field('evt-end-date')?.value||'',
    end_time:field('evt-end-time')?.value||'',
    description:field('evt-description')?.value||field('evt-desc')?.value||'',
    visibility:field('evt-visibility')?.value||'FAMILY',
    target_person_ids:Array.from(document.querySelectorAll('input[name="target_persons"]:checked')).map(x=>String(x.value)),
    time_zone:tz(),
    saved_at:new Date().toISOString()
  });
  const persistDraft = d => { try { sessionStorage.setItem(DRAFT_KEY, JSON.stringify(d)); } catch (_) {} };
  const clearDraft = () => { try { sessionStorage.removeItem(DRAFT_KEY); } catch (_) {} };

  function showCheck(d) {
    persistDraft(d);
    const c = document.getElementById('modal-container');
    if (!c) return Promise.resolve(true);
    return new Promise(resolve => {
      c.innerHTML = `<div class="modal-overlay"><div class="modal-card" style="max-width:620px;"><div class="card-header"><div class="card-title">🌸 Mayil Event Check</div></div><div style="padding:.3rem 0 1rem;"><div style="padding:.65rem .75rem;margin:.45rem 0;border-radius:.6rem;background:rgba(127,127,127,.07);">📅 <strong>Selected:</strong> ${esc(longDate(d.start_date))} · ${esc(relative(d.start_date))}</div><div style="padding:.65rem .75rem;margin:.45rem 0;border-radius:.6rem;background:rgba(127,127,127,.07);">🌐 <strong>Timezone:</strong> ${esc(d.time_zone)} · <strong>Today:</strong> ${esc(longDate(todayISO()))}</div></div><div style="font-size:.9rem;opacity:.8;margin-bottom:1rem;">Mayil has preserved your complete event draft. Saving will use this exact draft and will not reread cleared scheduler fields.</div><div style="display:flex;justify-content:flex-end;gap:.5rem;"><button type="button" class="btn btn-outline" id="femc-atomic-cancel">Return to Scheduler</button><button type="button" class="btn" id="femc-atomic-save">Save with This Date</button></div></div></div>`;
      c.style.display='block';
      document.getElementById('femc-atomic-cancel').onclick=()=>{c.style.display='none';resolve(false);};
      document.getElementById('femc-atomic-save').onclick=()=>{c.style.display='none';resolve(true);};
    });
  }

  async function saveCanonical(d) {
    const response = await fetch('/api/events/create', {
      method:'POST', credentials:'same-origin',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify(d)
    });
    let data = {};
    try { data = await response.json(); } catch (_) {}
    if (!response.ok || data.status !== 'success' || !data.event) throw new Error(data.message || `Event save failed (${response.status})`);
    const verify = await fetch('/api/events',{credentials:'same-origin'});
    const stored = await verify.json();
    const list = stored.calendar || stored.events || stored.items || [];
    if (!list.some(e => String(e.id||e.event_id||'') === String(data.event.id||data.event.event_id||''))) throw new Error('Event was accepted but could not be verified in the event store.');
    return data.event;
  }

  function install() {
    const current = window.submitCreateEvent;
    if (typeof current !== 'function' || current.__femcAtomicSaveV1) return;
    const guarded = async function(evt) {
      evt?.preventDefault?.(); evt?.stopPropagation?.();
      const d = capture();
      if (!d.title) { alert('Please enter an event title.'); return false; }
      if (!d.start_date) { alert('Please choose an event date.'); return false; }
      if (!(await showCheck(d))) return false;
      try {
        const event = await saveCanonical(d);
        clearDraft();
        alert(`Event saved successfully: ${event.title}`);
        window.dispatchEvent(new CustomEvent('femc:event-saved',{detail:event}));
        if (typeof window.loadView === 'function') {
          const active = document.querySelector('[data-view].active,[data-view].nav-active')?.dataset?.view;
          if (active) setTimeout(()=>window.loadView(active), 0);
        }
        return event;
      } catch (error) {
        persistDraft(d);
        console.error('FEMC atomic event save failed', error);
        alert(`${error.message || 'Event could not be saved.'} Your complete scheduler draft is still safe.`);
        return false;
      }
    };
    guarded.__femcAtomicSaveV1 = true;
    guarded.__femcV5 = true;
    window.submitCreateEvent = guarded;
  }
  install();
  new MutationObserver(install).observe(document.documentElement,{childList:true,subtree:true});
  setInterval(install,500);
})();
</script>'''
    runtime.HTML_TEMPLATE = runtime.HTML_TEMPLATE.replace('</body>', script + '\n</body>')


__all__ = ['install']
