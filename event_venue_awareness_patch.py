from __future__ import annotations

import datetime
from urllib.parse import urlparse

from atomic_event_save_repair_patch import _read_json, _store


def install(runtime):
    if getattr(runtime, "_FEMC_EVENT_VENUE_AWARENESS_V2", False):
        return
    runtime._FEMC_EVENT_VENUE_AWARENESS_V2 = True

    previous_post = runtime.DemoHTTPRequestHandler.do_POST

    def patched_post(self):
        path = urlparse(self.path).path
        if path in ("/api/events", "/api/events/create"):
            payload = _read_json(self)
            title = str(payload.get("title") or "").strip()
            start_date = str(payload.get("start_date") or payload.get("date") or "").strip()[:10]
            if not title:
                self._send_json({"status": "error", "message": "Please enter an event title."}, status=400)
                return
            try:
                datetime.date.fromisoformat(start_date)
            except Exception:
                self._send_json({"status": "error", "message": "Please choose a valid event date."}, status=400)
                return

            events = _store(runtime)
            existing_ids = {str(e.get("id") or e.get("event_id") or "") for e in events}
            n = len(events) + 1
            event_id = f"sim_event_user_{n}"
            while event_id in existing_ids:
                n += 1
                event_id = f"sim_event_user_{n}"

            event = {
                "id": event_id,
                "event_id": event_id,
                "title": title,
                "description": str(payload.get("description") or ""),
                "venue": str(payload.get("venue") or "").strip(),
                "category": str(payload.get("category") or "GENERAL").upper(),
                "visibility": str(payload.get("visibility") or "FAMILY").upper(),
                "date": start_date,
                "start_date": start_date,
                "start_time": str(payload.get("start_time") or ""),
                "end_date": str(payload.get("end_date") or start_date)[:10],
                "end_time": str(payload.get("end_time") or ""),
                "target_person_ids": list(payload.get("target_person_ids") or payload.get("person_ids") or []),
                "person_ids": list(payload.get("target_person_ids") or payload.get("person_ids") or []),
                "time_zone": str(payload.get("time_zone") or "Asia/Kolkata"),
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }
            events.append(event)
            self._send_json({"status": "success", "event": event})
            return

        if path in ("/api/events/update", "/api/events/edit"):
            payload = _read_json(self)
            events = _store(runtime)
            event_id = str(payload.get("event_id") or payload.get("id") or "")
            event = next((e for e in events if str(e.get("id") or e.get("event_id") or "") == event_id), None)
            if event is None:
                self._send_json({"status": "error", "message": "Event not found."}, status=404)
                return

            for key in ("title", "description", "venue", "category", "visibility", "time_zone"):
                if key in payload:
                    value = payload.get(key)
                    event[key] = str(value).upper() if key in ("category", "visibility") else str(value or "").strip()

            if "target_person_ids" in payload or "person_ids" in payload:
                people = list(payload.get("target_person_ids") or payload.get("person_ids") or [])
                event["target_person_ids"] = people
                event["person_ids"] = list(people)

            for key in ("start_date", "end_date", "start_time", "end_time"):
                if key in payload and payload.get(key) is not None:
                    event[key] = str(payload.get(key)).strip()
            if event.get("start_date"):
                event["date"] = event["start_date"]

            self._send_json({"status": "success", "event": event})
            return

        return previous_post(self)

    runtime.DemoHTTPRequestHandler.do_POST = patched_post

    marker = "FEMC_EVENT_VENUE_AWARENESS_V2"
    if marker in runtime.HTML_TEMPLATE:
        return

    script = r'''<script id="FEMC_EVENT_VENUE_AWARENESS_V2">
(() => {
  const esc = v => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const tz = () => window.FEMC_TIME_ZONE || Intl.DateTimeFormat().resolvedOptions().timeZone || 'Asia/Kolkata';
  const field = id => document.getElementById(id);
  const clean = v => String(v || '').trim().toLowerCase().replace(/\s+/g,' ');
  const listOf = d => Array.isArray(d) ? d : (d?.calendar || d?.events || d?.items || []);
  const dateOf = e => String(e?.start_date || e?.date || '').slice(0,10);
  const timeOf = v => {
    const s=String(v || '');
    const m=s.match(/(\d{1,2}):(\d{2})\s*(AM|PM)?/i);
    if(!m) return '';
    let h=Number(m[1]), min=Number(m[2]), ap=(m[3]||'').toUpperCase();
    if(ap==='PM' && h<12) h+=12;
    if(ap==='AM' && h===12) h=0;
    return `${String(h).padStart(2,'0')}:${String(min).padStart(2,'0')}`;
  };
  const mins = v => { const t=timeOf(v); if(!t) return null; const [h,m]=t.split(':').map(Number); return h*60+m; };
  const eventIdOf = e => String(e?.id || e?.event_id || '');

  function addVenue(prefix='') {
    const id = `${prefix}evt-venue`;
    if (field(id)) return;
    const description = field(`${prefix}evt-description`) || field(`${prefix}evt-desc`);
    const group = description?.closest('.form-group');
    if (!group) return;
    const div = document.createElement('div');
    div.className = 'form-group femc-venue-field';
    div.innerHTML = `<label class="form-label">📍 Venue <span style="opacity:.65;font-weight:normal;">(optional)</span></label><input id="${id}" class="form-input" placeholder="Enter venue, home, or location" autocomplete="off" /><div style="font-size:.78rem;opacity:.72;margin-top:.35rem;">Examples: Home, Amma's House, Hotel Sangam, Madurai, Online, or To be decided.</div>`;
    group.before(div);
  }

  function installVenueFields() {
    addVenue('');
    addVenue('edit-');
  }

  async function getEvents() {
    try {
      const r = await fetch('/api/events',{credentials:'same-origin'});
      return r.ok ? listOf(await r.json()) : [];
    } catch (_) { return []; }
  }

  function captureCreate() {
    return {
      title:(field('evt-title')?.value || '').trim(),
      category:field('evt-cat')?.value || 'GENERAL',
      start_date:field('evt-start-date')?.value || '',
      start_time:field('evt-start-time')?.value || '',
      end_date:field('evt-end-date')?.value || field('evt-start-date')?.value || '',
      end_time:field('evt-end-time')?.value || '',
      venue:(field('evt-venue')?.value || '').trim(),
      description:field('evt-description')?.value || field('evt-desc')?.value || '',
      visibility:field('evt-visibility')?.value || field('evt-vis')?.value || 'FAMILY',
      target_person_ids:Array.from(document.querySelectorAll('input[name="target_persons"]:checked')).map(x=>String(x.value)),
      time_zone:tz()
    };
  }

  function overlap(d,e) {
    if (!d.start_date || dateOf(e)!==d.start_date) return false;
    const a=mins(d.start_time), b=mins(e.start_time);
    if (a===null || b===null) return false;
    const ae=mins(d.end_time)||a+1, be=mins(e.end_time)||b+1;
    return a < be && b < ae;
  }

  function analyze(d, events) {
    const exact=[], clashes=[], sameVenue=[];
    for (const e of events) {
      if (clean(e.title)===clean(d.title) && dateOf(e)===d.start_date && timeOf(e.start_time)===timeOf(d.start_time)) exact.push(e);
      else if (overlap(d,e)) clashes.push(e);
      if (d.venue && clean(e.venue)===clean(d.venue) && overlap(d,e)) sameVenue.push(e);
    }
    return {exact, clashes, sameVenue};
  }

  function row(e) {
    const venue = String(e?.venue || '').trim();
    return `<div style="padding:.65rem .75rem;margin:.45rem 0;border-radius:.6rem;background:rgba(127,127,127,.07);line-height:1.4;"><strong>${esc(e?.title || 'Family event')}</strong><br><span style="font-size:.84rem;opacity:.78;">${esc(dateOf(e) || 'Unknown date')}${timeOf(e?.start_time) ? ` · ${esc(timeOf(e.start_time))}` : ''}${venue ? ` · 📍 ${esc(venue)}` : ''}</span></div>`;
  }

  async function awareness(d) {
    const found = analyze(d, await getEvents());
    const total = found.exact.length + found.clashes.length;
    if (!total) return true;
    const c = field('modal-container');
    if (!c) return true;
    return new Promise(resolve => {
      const exact = found.exact.length ? `<div style="padding:.7rem .8rem;border-radius:.65rem;background:rgba(255,180,80,.10);margin-bottom:.65rem;">🌸 <strong>Mayil noticed the same title, date and time already scheduled.</strong><br>Please check the scheduled events once before saving. This may still be intentional, and nothing is blocked.</div>${found.exact.slice(0,3).map(row).join('')}` : '';
      const clash = found.clashes.length ? `<div style="padding:.7rem .8rem;border-radius:.65rem;background:rgba(255,120,120,.10);margin:.65rem 0;">🕒 <strong>Mayil noticed another family event during this time.</strong><br>Please check whether both events are intended to happen at the same or overlapping time before saving.</div>${found.clashes.slice(0,5).map(row).join('')}` : '';
      const venue = found.sameVenue.length ? `<div style="padding:.7rem .8rem;border-radius:.65rem;background:rgba(120,190,255,.10);margin:.65rem 0;">📍 <strong>The same venue is also in use during this time.</strong><br>This gives extra context for your schedule check; Mayil is not blocking the event.</div>` : '';
      c.innerHTML = `<div class="modal-overlay"><div class="modal-card" style="max-width:680px;"><div class="card-header"><div class="card-title">🌸 Mayil Schedule Check</div></div><div style="padding:.35rem 0 1rem;"><div style="padding:.65rem .75rem;border-radius:.6rem;background:rgba(127,127,127,.07);margin-bottom:.65rem;"><strong>${esc(d.title || 'This event')}</strong><br>${esc(d.start_date)}${timeOf(d.start_time)?` · ${esc(timeOf(d.start_time))}`:''}${d.venue?` · 📍 ${esc(d.venue)}`:''}</div>${exact}${clash}${venue}<div style="font-size:.9rem;opacity:.82;margin-top:.8rem;">Mayil is only bringing related schedule information to your attention. Please check once before saving. If your details are correct, you may continue.</div></div><div style="display:flex;justify-content:flex-end;gap:.5rem;flex-wrap:wrap;"><button type="button" class="btn btn-outline" id="femc-venue-check-form">Check Form Again</button><button type="button" class="btn" id="femc-venue-save">Save This Event</button></div></div></div>`;
      c.style.display='block';
      field('femc-venue-check-form').onclick=()=>{c.style.display='none';resolve(false);};
      field('femc-venue-save').onclick=()=>{c.style.display='none';resolve(true);};
    });
  }

  async function saveCreate(evt) {
    evt?.preventDefault?.();
    installVenueFields();
    const d=captureCreate();
    if (!d.title) { alert('Please enter an event title.'); return false; }
    if (!d.start_date) { alert('Please choose an event date.'); return false; }
    if (!(await awareness(d))) return false;
    try {
      const r=await fetch('/api/events/create',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});
      const data=await r.json().catch(()=>({}));
      if (!r.ok || data.status!=='success' || !data.event) throw new Error(data.message || 'Event could not be saved.');
      const verify=await getEvents();
      if (!verify.some(e=>eventIdOf(e)===eventIdOf(data.event))) throw new Error('Event was accepted but could not be verified.');
      try{sessionStorage.removeItem('femc.eventSchedulerDraft.v5');}catch(_){}
      alert(`Event saved successfully: ${data.event.title}`);
      window.dispatchEvent(new CustomEvent('femc:event-saved',{detail:data.event}));
      const active=document.querySelector('[data-view].active,[data-view].nav-active')?.dataset?.view;
      if (typeof window.loadView==='function' && active) setTimeout(()=>window.loadView(active),0);
      return data.event;
    } catch (error) {
      try{sessionStorage.setItem('femc.eventSchedulerDraft.v5',JSON.stringify(d));}catch(_){}
      console.error('FEMC venue-aware event save failed',error);
      alert(`${error.message || 'Event could not be saved.'} Your complete scheduler draft is still safe.`);
      return false;
    }
  }

  function wireCreate() {
    const current=window.submitCreateEvent;
    if (typeof current==='function' && current.__femcVenueAwareV2) return;
    const guarded=saveCreate;
    guarded.__femcVenueAwareV2=true;
    guarded.__femcAtomicSaveV1=true;
    guarded.__femcMayilScheduleAwarenessV1=true;
    guarded.__femcV5=true;
    window.submitCreateEvent=guarded;
  }

  async function loadVenueForEdit(eventId) {
    const events=await getEvents();
    return events.find(e=>eventIdOf(e)===String(eventId))?.venue || '';
  }

  function wireEditor() {
    const original=window.openPracticeEventEditor;
    if (typeof original!=='function' || original.__femcVenueAwareV2) return;
    const wrapped=async function(eventId,...rest) {
      const result=await original.call(this,eventId,...rest);
      setTimeout(async ()=>{
        installVenueFields();
        const v=field('edit-evt-venue');
        if (v && !v.dataset.loaded) { v.value=await loadVenueForEdit(eventId); v.dataset.loaded='1'; }
      },0);
      return result;
    };
    wrapped.__femcVenueAwareV2=true;
    window.openPracticeEventEditor=wrapped;
  }

  function wireEdit() {
    const current=window.submitPracticeEventEdit;
    if (typeof current!=='function' || current.__femcVenueAwareV2) return;
    const wrapped=async function(evt,eventId,...rest) {
      installVenueFields();
      const venue=(field('edit-evt-venue')?.value || '').trim();
      const form=evt?.target?.closest?.('form');
      if (!form) return current.call(this,evt,eventId,...rest);
      evt?.preventDefault?.();
      const startDate=field('edit-evt-start-date')?.value||'';
      const startTime=field('edit-evt-start-time')?.value||'';
      const endDate=field('edit-evt-end-date')?.value||startDate;
      const endTime=field('edit-evt-end-time')?.value||'';
      const title=(field('edit-evt-title')?.value||'').trim();
      if (!title) { alert('Please enter an event title.'); return false; }
      const ids=Array.from(document.querySelectorAll('input[name="edit_target_persons"]:checked')).map(x=>String(x.value));
      const payload={event_id:eventId,title,category:field('edit-evt-cat')?.value||'GENERAL',visibility:field('edit-evt-vis')?.value||field('edit-evt-visibility')?.value||'FAMILY',description:field('edit-evt-desc')?.value||field('edit-evt-description')?.value||'',venue,target_person_ids:ids,start_date:startDate,start_time:startTime,end_date:endDate,end_time:endTime,time_zone:tz()};
      if (startDate && startTime) {
        const d={...payload};
        const events=await getEvents();
        const found=analyze(d,events.filter(e=>eventIdOf(e)!==String(eventId)));
        if ((found.exact.length||found.clashes.length) && !(await awareness(d))) return false;
      }
      try {
        const r=await fetch('/api/events/update',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
        const data=await r.json().catch(()=>({}));
        if (!r.ok || data.status!=='success') throw new Error(data.message || 'Event could not be updated.');
        if (typeof window.closeModal==='function') window.closeModal();
        if (typeof window.loadView==='function') await window.loadView('calendar');
        return data.event;
      } catch (error) {
        console.error('FEMC venue-aware event update failed',error);
        alert(error.message || 'Event could not be updated.');
        return false;
      }
    };
    wrapped.__femcVenueAwareV2=true;
    wrapped.__femcMayilScheduleAwarenessV1=true;
    window.submitPracticeEventEdit=wrapped;
  }

  function install() { installVenueFields(); wireCreate(); wireEditor(); wireEdit(); }
  install();
  new MutationObserver(install).observe(document.documentElement,{childList:true,subtree:true});
  setInterval(install,300);
})();
</script>'''
    runtime.HTML_TEMPLATE = runtime.HTML_TEMPLATE.replace("</body>", script + "\n</body>")


__all__ = ["install"]
