from __future__ import annotations


def install(runtime):
    marker = "FEMC_EDIT_EVENT_CONTEXT_REPAIR_V1"
    if marker in runtime.HTML_TEMPLATE:
        return

    script = r'''<script id="FEMC_EDIT_EVENT_CONTEXT_REPAIR_V1">
(() => {
  const esc = v => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const getContainer = () => document.getElementById('modal-container');
  const cache = new Map();
  const getEvent = async id => {
    const r = await fetch(`/api/events?event_id=${encodeURIComponent(id)}`, {credentials:'same-origin'});
    if (!r.ok) throw new Error(`Event lookup failed (${r.status})`);
    const data = await r.json();
    return data?.event_detail?.event || data?.event || (data?.events || []).find(e => String(e.id||e.event_id) === String(id)) || null;
  };
  const splitDate = v => String(v||'').slice(0,10);
  const splitTime = v => { const s=String(v||''); const m=s.match(/T(\d{2}:\d{2})/) || s.match(/(\d{2}:\d{2})/); return m?m[1]:''; };
  const editForm = (ev,id) => {
    const c=getContainer();
    const venue = ev.venue || '';
    c.innerHTML = `<div class="modal-overlay"><div class="modal-card" style="max-width:680px;"><div class="card-header"><div class="card-title">✏️ Edit Family Event</div><button type="button" class="btn btn-outline btn-sm" id="femc-edit-close">✕</button></div><form id="femc-edit-form"><input type="hidden" id="femc-edit-id" value="${esc(id)}"><div class="form-group"><label class="form-label">Event Title</label><input id="femc-edit-title" class="form-input" required value="${esc(ev.title)}"></div><div class="form-group"><label class="form-label">Category</label><select id="femc-edit-category" class="form-select"><option ${String(ev.category||'GENERAL').toUpperCase()==='GENERAL'?'selected':''}>GENERAL</option><option ${String(ev.category||'').toUpperCase()==='BIRTHDAY'?'selected':''}>BIRTHDAY</option><option ${String(ev.category||'').toUpperCase()==='ANNIVERSARY'?'selected':''}>ANNIVERSARY</option><option ${String(ev.category||'').toUpperCase()==='MILESTONE'?'selected':''}>MILESTONE</option></select></div><div class="form-group"><label class="form-label">Start Date</label><input type="date" id="femc-edit-start-date" class="form-input" required value="${esc(splitDate(ev.start_date||ev.date))}"></div><div class="form-group"><label class="form-label">Start Time</label><input type="time" id="femc-edit-start-time" class="form-input" required value="${esc(splitTime(ev.start_time))}"></div><div class="form-group"><label class="form-label">End Date</label><input type="date" id="femc-edit-end-date" class="form-input" required value="${esc(splitDate(ev.end_date||ev.start_date||ev.date))}"></div><div class="form-group"><label class="form-label">End Time</label><input type="time" id="femc-edit-end-time" class="form-input" required value="${esc(splitTime(ev.end_time))}"></div><div class="form-group"><label class="form-label">📍 Venue <span style="opacity:.65;font-weight:normal;">(optional)</span></label><input id="femc-edit-venue" class="form-input" value="${esc(venue)}" placeholder="Enter venue, home, or location"></div><div class="form-group"><label class="form-label">Visibility</label><select id="femc-edit-visibility" class="form-select"><option value="FAMILY" ${String(ev.visibility||'FAMILY').toUpperCase()==='FAMILY'?'selected':''}>Family Visible (All Members)</option><option value="PRIVATE" ${String(ev.visibility||'').toUpperCase()==='PRIVATE'?'selected':''}>Private (Only You)</option></select></div><div class="form-group"><label class="form-label">Description</label><input id="femc-edit-description" class="form-input" value="${esc(ev.description||'')}"></div><div style="display:flex;justify-content:flex-end;gap:.5rem;margin-top:1.25rem;"><button type="button" class="btn btn-outline" id="femc-edit-cancel">Cancel</button><button type="submit" class="btn">Save Changes</button></div></form></div></div>`;
    c.style.display='block';
    document.getElementById('femc-edit-close').onclick=()=>window.closeModal?.();
    document.getElementById('femc-edit-cancel').onclick=()=>window.closeModal?.();
    document.getElementById('femc-edit-form').onsubmit=async e=>{
      e.preventDefault();
      const payload={event_id:id,title:document.getElementById('femc-edit-title').value.trim(),category:document.getElementById('femc-edit-category').value,visibility:document.getElementById('femc-edit-visibility').value,description:document.getElementById('femc-edit-description').value.trim(),venue:document.getElementById('femc-edit-venue').value.trim(),start_date:document.getElementById('femc-edit-start-date').value,start_time:document.getElementById('femc-edit-start-time').value,end_date:document.getElementById('femc-edit-end-date').value,end_time:document.getElementById('femc-edit-end-time').value};
      try{
        const r=await fetch('/api/events/update',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
        const data=await r.json().catch(()=>({}));
        if(!r.ok || data.status!=='success') throw new Error(data.message||`Update failed (${r.status})`);
        window.closeModal?.();
        if(typeof window.loadView==='function') await window.loadView('calendar');
      }catch(err){ alert(err.message||'Event could not be updated.'); }
    };
  };

  window.openPracticeEventEditor = async function(eventId){
    const id=String(eventId||'');
    if(!id){ alert('This event has no saved event ID.'); return; }
    try{ const ev=await getEvent(id); if(!ev){ alert('The selected event could not be found.'); return; } cache.set(id,ev); editForm(ev,id); }
    catch(err){ console.error('FEMC edit lookup failed',err); alert(err.message||'Could not open the event for editing.'); }
  };

  const patchDetail=()=>{
    const original=window.openEventDetailModal;
    if(typeof original!=='function' || original.__femcEditContextV1) return;
    const wrapped=async function(eventId){
      await original.call(this,eventId);
      const c=getContainer(); if(!c) return;
      const buttons=[...c.querySelectorAll('button')];
      const share=buttons.find(b=>(b.textContent||'').includes('Share Event'));
      if(!share || buttons.some(b=>(b.textContent||'').includes('Edit Event'))) return;
      const edit=document.createElement('button'); edit.className='btn btn-outline btn-sm'; edit.textContent='✏️ Edit Event'; edit.onclick=()=>window.openPracticeEventEditor(eventId); share.parentElement.insertBefore(edit,share);
    };
    wrapped.__femcEditContextV1=true; window.openEventDetailModal=wrapped;
  };
  patchDetail();
  new MutationObserver(patchDetail).observe(document.documentElement,{childList:true,subtree:true});
  setInterval(patchDetail,400);
})();
</script>'''
    runtime.HTML_TEMPLATE = runtime.HTML_TEMPLATE.replace('</body>', script+'\n</body>')

__all__=['install']
