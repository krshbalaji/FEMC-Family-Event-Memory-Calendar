from __future__ import annotations

import json
from urllib.parse import urlparse, parse_qs


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


def _event_store(runtime):
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


def _eid(event):
    return str(event.get('id') or event.get('event_id') or '')


def install(runtime):
    marker = '_FEMC_EVENT_LIFECYCLE_REPAIR_V1'
    if getattr(runtime, marker, False):
        return
    setattr(runtime, marker, True)

    original_get = runtime.DemoHTTPRequestHandler.do_GET
    original_post = runtime.DemoHTTPRequestHandler.do_POST

    def patched_get(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/events':
            events = [dict(e) for e in _event_store(runtime)]
            qs = parse_qs(parsed.query)
            event_id = (qs.get('event_id') or [''])[0]
            if event_id:
                ev = next((e for e in events if _eid(e) == str(event_id)), None)
                if ev is None:
                    self._send_json({'status':'error','message':'Event not found.'}, status=404)
                    return
                self._send_json({'status':'success','event':ev,'event_detail':{'event':ev,'place':None,'memories':[],'media_items':[],'target_persons':[]}})
                return
            self._send_json({'status':'success','events':events,'calendar':events,'items':events})
            return
        return original_get(self)

    def patched_post(self):
        path = urlparse(self.path).path
        if path in ('/api/events/update','/api/events/edit'):
            payload = _read_json(self)
            event_id = str(payload.get('event_id') or payload.get('id') or '')
            events = _event_store(runtime)
            event = next((e for e in events if _eid(e) == event_id), None)
            if event is None:
                self._send_json({'status':'error','message':'The selected event could not be found.'}, status=404)
                return
            for key in ('title','description','venue','category','visibility','time_zone','start_date','start_time','end_date','end_time'):
                if key in payload:
                    event[key] = payload[key]
            if 'target_person_ids' in payload or 'person_ids' in payload:
                people = list(payload.get('target_person_ids') or payload.get('person_ids') or [])
                event['target_person_ids'] = people
                event['person_ids'] = list(people)
            if event.get('start_date'):
                event['date'] = event['start_date']
            self._send_json({'status':'success','event':event})
            return

        if path in ('/api/events/delete','/api/events/remove'):
            payload = _read_json(self)
            event_id = str(payload.get('event_id') or payload.get('id') or '')
            events = _event_store(runtime)
            idx = next((i for i,e in enumerate(events) if _eid(e) == event_id), None)
            if idx is None:
                self._send_json({'status':'error','message':'The selected event could not be found.'}, status=404)
                return
            deleted = events.pop(idx)
            self._send_json({'status':'success','event':deleted,'deleted_event_id':event_id})
            return

        return original_post(self)

    runtime.DemoHTTPRequestHandler.do_GET = patched_get
    runtime.DemoHTTPRequestHandler.do_POST = patched_post

    script = r'''<script id="FEMC_EVENT_LIFECYCLE_REPAIR_V1">
(() => {
  const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const ctn=()=>document.getElementById('modal-container');
  const getEvents=async()=>{const r=await fetch('/api/events',{credentials:'same-origin'}); const d=await r.json(); return d.events||d.calendar||d.items||[];};
  const getEvent=async id=>{const r=await fetch(`/api/events?event_id=${encodeURIComponent(id)}`,{credentials:'same-origin'}); if(!r.ok) throw new Error('Event lookup failed.'); const d=await r.json(); return d.event||d.event_detail?.event;};
  const date=v=>String(v||'').slice(0,10);
  const time=v=>{const s=String(v||''); const m=s.match(/(?:T)?(\d{1,2}:\d{2})/); return m?m[1]:'';};
  function detailRows(ev){return `<div style="font-size:.9rem;line-height:1.6"><div><strong>When:</strong> ${esc(date(ev.start_date||ev.date))}${time(ev.start_time)?` · ${esc(time(ev.start_time))}`:''}${time(ev.end_time)?` — ${esc(time(ev.end_time))}`:''}</div><div><strong>Venue:</strong> ${esc(ev.venue||'—')}</div><div><strong>Description:</strong> ${esc(ev.description||'—')}</div><div><strong>Category:</strong> ${esc(String(ev.category||'GENERAL').toUpperCase())}</div><div><strong>Visibility:</strong> ${esc(String(ev.visibility||'FAMILY').toUpperCase())}</div></div>`;}
  function showExisting(ev,onClose){const c=ctn(); if(!c) return; c.innerHTML=`<div class="modal-overlay"><div class="modal-card" style="max-width:650px"><div class="card-header"><div class="card-title">📅 ${esc(ev.title||'Existing Event')}</div><button class="btn btn-outline btn-sm" id="femc-el-close">✕</button></div>${detailRows(ev)}<div style="display:flex;justify-content:flex-end;gap:.5rem;margin-top:1rem"><button class="btn btn-outline" id="femc-el-back">Return to Schedule Check</button></div></div></div>`; c.style.display='block'; const close=()=>{if(onClose) onClose(); else c.style.display='none';}; c.querySelector('#femc-el-close').onclick=close; c.querySelector('#femc-el-back').onclick=close;}
  function showDeleteConfirm(id,title){const c=ctn(); if(!c) return; c.innerHTML=`<div class="modal-overlay"><div class="modal-card" style="max-width:560px"><div class="card-header"><div class="card-title">🗑 Delete Event</div></div><p>Delete <strong>${esc(title)}</strong>?</p><p style="opacity:.8">This removes the selected event from the current Practice World. This action cannot be undone from the current screen.</p><div style="display:flex;justify-content:flex-end;gap:.5rem"><button class="btn btn-outline" id="femc-del-cancel">Cancel</button><button class="btn btn-pink" id="femc-del-confirm">Delete Event</button></div></div></div>`; c.style.display='block'; c.querySelector('#femc-del-cancel').onclick=()=>c.style.display='none'; c.querySelector('#femc-del-confirm').onclick=async()=>{const r=await fetch('/api/events/delete',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'same-origin',body:JSON.stringify({event_id:id})}); const d=await r.json().catch(()=>({})); if(!r.ok||d.status!=='success'){alert(d.message||'Event could not be deleted.');return;} c.style.display='none'; if(typeof window.loadView==='function') await window.loadView('calendar');};}
  const originalEditor=window.openPracticeEventEditor;
  window.openPracticeEventEditor=async function(eventId){try{const ev=await getEvent(eventId); if(!ev){alert('The selected event could not be found.');return;} const c=ctn(); c.innerHTML=`<div class="modal-overlay"><div class="modal-card" style="max-width:680px"><div class="card-header"><div class="card-title">✏️ Edit Family Event</div><button class="btn btn-outline btn-sm" id="femc-edit-close">✕</button></div><form id="femc-edit-form"><input type="hidden" id="femc-edit-id" value="${esc(eventId)}"><div class="form-group"><label class="form-label">Event Title</label><input id="femc-edit-title" class="form-input" required value="${esc(ev.title)}"></div><div class="form-group"><label class="form-label">Category</label><select id="femc-edit-category" class="form-select"><option value="GENERAL">General</option><option value="BIRTHDAY">Birthday</option><option value="ANNIVERSARY">Anniversary</option><option value="MILESTONE">Milestone</option></select></div><div class="form-group"><label class="form-label">Start Date</label><input id="femc-edit-start-date" type="date" class="form-input" value="${esc(date(ev.start_date||ev.date))}" required></div><div class="form-group"><label class="form-label">Start Time</label><input id="femc-edit-start-time" type="time" class="form-input" value="${esc(time(ev.start_time))}" required></div><div class="form-group"><label class="form-label">End Date</label><input id="femc-edit-end-date" type="date" class="form-input" value="${esc(date(ev.end_date||ev.start_date||ev.date))}" required></div><div class="form-group"><label class="form-label">End Time</label><input id="femc-edit-end-time" type="time" class="form-input" value="${esc(time(ev.end_time))}" required></div><div class="form-group"><label class="form-label">📍 Venue</label><input id="femc-edit-venue" class="form-input" value="${esc(ev.venue||'')}"></div><div class="form-group"><label class="form-label">Visibility</label><select id="femc-edit-visibility" class="form-select"><option value="FAMILY">Family Visible (All Members)</option><option value="PRIVATE">Private (Only You)</option></select></div><div class="form-group"><label class="form-label">Description</label><input id="femc-edit-description" class="form-input" value="${esc(ev.description||'')}"></div><div style="display:flex;justify-content:flex-end;gap:.5rem;margin-top:1.2rem"><button type="button" class="btn btn-pink" id="femc-edit-delete">🗑 Delete Event</button><button type="button" class="btn btn-outline" id="femc-edit-cancel">Cancel</button><button type="submit" class="btn">Save Changes</button></div></form></div></div>`; c.style.display='block'; c.querySelector('#femc-edit-category').value=String(ev.category||'GENERAL').toUpperCase(); c.querySelector('#femc-edit-visibility').value=String(ev.visibility||'FAMILY').toUpperCase(); c.querySelector('#femc-edit-close').onclick=()=>window.closeModal?.(); c.querySelector('#femc-edit-cancel').onclick=()=>window.closeModal?.(); c.querySelector('#femc-edit-delete').onclick=()=>showDeleteConfirm(eventId,ev.title||'this event'); c.querySelector('#femc-edit-form').onsubmit=async e=>{e.preventDefault(); const payload={event_id:eventId,title:c.querySelector('#femc-edit-title').value.trim(),category:c.querySelector('#femc-edit-category').value,visibility:c.querySelector('#femc-edit-visibility').value,description:c.querySelector('#femc-edit-description').value.trim(),venue:c.querySelector('#femc-edit-venue').value.trim(),start_date:c.querySelector('#femc-edit-start-date').value,start_time:c.querySelector('#femc-edit-start-time').value,end_date:c.querySelector('#femc-edit-end-date').value,end_time:c.querySelector('#femc-edit-end-time').value}; const r=await fetch('/api/events/update',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'same-origin',body:JSON.stringify(payload)}); const d=await r.json().catch(()=>({})); if(!r.ok||d.status!=='success'){alert(d.message||'Event could not be updated.');return;} c.style.display='none'; if(typeof window.loadView==='function') await window.loadView('calendar');};}catch(err){console.error(err);alert(err.message||'Could not open event for editing.');}};
  const originalDetail=window.openEventDetailModal;
  window.openEventDetailModal=async function(eventId){await originalDetail?.call(this,eventId); const c=ctn(); if(!c)return; const buttons=[...c.querySelectorAll('button')]; if(buttons.some(b=>(b.textContent||'').includes('Edit Event'))) return; const share=buttons.find(b=>(b.textContent||'').includes('Share Event')); if(!share)return; const edit=document.createElement('button'); edit.className='btn btn-outline btn-sm'; edit.textContent='✏️ Edit Event'; edit.onclick=()=>window.openPracticeEventEditor(eventId); const del=document.createElement('button'); del.className='btn btn-pink btn-sm'; del.textContent='🗑 Delete Event'; del.onclick=async()=>{try{const ev=await getEvent(eventId); showDeleteConfirm(eventId,ev?.title||'this event');}catch(e){alert(e.message)}}; share.parentElement.insertBefore(edit,share); share.parentElement.insertBefore(del,share);};
  window.femcShowExistingEvent=showExisting;
})();
</script>'''
    runtime.HTML_TEMPLATE = runtime.HTML_TEMPLATE.replace('</body>', script+'\n</body>')

__all__=['install']
