from __future__ import annotations


def install(runtime):
    html = runtime.HTML_TEMPLATE
    marker = "FEMC_EVENT_INTELLIGENCE_V2_PATCH"
    if marker in html:
        return

    script = r'''<script id="FEMC_EVENT_INTELLIGENCE_V2_PATCH">
(() => {
  const DAY_MS = 86400000;
  const pad = n => String(n).padStart(2,'0');
  const esc = v => String(v ?? '').replace(/[&<>\"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const date = iso => new Date(`${iso}T12:00:00`);
  const longDate = iso => !iso ? '' : new Intl.DateTimeFormat(undefined,{weekday:'long',year:'numeric',month:'long',day:'numeric'}).format(date(iso));
  const delta = iso => { if(!iso)return null; const a=date(iso); const b=new Date(); b.setHours(0,0,0,0); return Math.round((a-b)/DAY_MS); };
  const relative = iso => { const n=delta(iso); if(n===null)return ''; if(n===0)return 'Today'; return n<0?`${Math.abs(n)} day${Math.abs(n)===1?'':'s'} ago`:`In ${n} day${n===1?'':'s'}`; };
  const eventList = d => d?.calendar || d?.events || d?.items || [];
  const eventDate = e => String(e?.start_date || e?.date || e?.start_time || '').slice(0,10);
  const normalize = x => String(x||'').trim().toUpperCase();
  const clone = o => JSON.parse(JSON.stringify(o||{}));

  let activeDraft = null;
  let activeInsights = null;
  let activeMode = null;

  function captureDraft(mode,eventId) {
    const p=mode==='edit'?'edit-':'';
    return {
      mode,eventId:eventId||null,
      title:document.getElementById(`${p}evt-title`)?.value||'',
      category:document.getElementById(`${p}evt-cat`)?.value||'GENERAL',
      start_date:document.getElementById(`${p}evt-start-date`)?.value||'',
      start_time:document.getElementById(`${p}evt-start-time`)?.value||'',
      end_date:document.getElementById(`${p}evt-end-date`)?.value||'',
      end_time:document.getElementById(`${p}evt-end-time`)?.value||'',
      description:document.getElementById(`${p}evt-description`)?.value||document.getElementById(`${p}evt-desc`)?.value||'',
      visibility:document.getElementById(`${p}evt-visibility`)?.value||'',
      people:Array.from(document.querySelectorAll(`input[name="${mode==='edit'?'edit_target_persons':'target_persons'}"]:checked`)).map(x=>x.value)
    };
  }

  function restoreDraft(d) {
    if(!d)return;
    const p=d.mode==='edit'?'edit-':'';
    const set=(id,v)=>{const el=document.getElementById(id); if(el&&v!==undefined){el.value=v;el.dispatchEvent(new Event('change',{bubbles:true}));}};
    set(`${p}evt-title`,d.title); set(`${p}evt-cat`,d.category); set(`${p}evt-start-date`,d.start_date); set(`${p}evt-start-time`,d.start_time); set(`${p}evt-end-date`,d.end_date); set(`${p}evt-end-time`,d.end_time);
    const desc=document.getElementById(`${p}evt-description`)||document.getElementById(`${p}evt-desc`); if(desc){desc.value=d.description||'';desc.dispatchEvent(new Event('input',{bubbles:true}));}
    if(d.visibility)set(`${p}evt-visibility`,d.visibility);
    const name=d.mode==='edit'?'edit_target_persons':'target_persons';
    document.querySelectorAll(`input[name="${name}"]`).forEach(x=>{x.checked=d.people.includes(x.value);x.dispatchEvent(new Event('change',{bubbles:true}));});
  }

  async function insightsFor(v){
    let history=[];try{history=eventList(await fetchAPI('/api/events'));}catch(_){}
    const other=history.filter(e=>String(e.id||e.event_id||'')!==String(v.eventId||''));
    const sameDay=other.filter(e=>eventDate(e)===v.start_date);
    const samePerson=other.filter(e=>normalize(e.category)===normalize(v.category) && (e.target_person_ids||e.person_ids||[]).some(id=>v.people.includes(String(id))));
    const titleMatch=other.filter(e=>String(e.title||'').trim().toLowerCase()===String(v.title||'').trim().toLowerCase());
    const around=other.filter(e=>{const x=eventDate(e);if(!x||!v.start_date)return false;return Math.abs(delta(x)-delta(v.start_date))<=7;}).sort((a,b)=>eventDate(a).localeCompare(eventDate(b)));
    return {sameDay,samePerson,titleMatch,around};
  }

  function relatedRows(list,kind){
    if(!list?.length)return '<div style="opacity:.72;padding:.6rem 0;">No related records found.</div>';
    return list.slice(0,12).map((e,i)=>`<button type="button" class="femc-related-row" data-femc-related="${kind}:${i}" style="width:100%;text-align:left;border:1px solid rgba(127,127,127,.18);background:rgba(127,127,127,.05);border-radius:.65rem;padding:.75rem;margin:.35rem 0;cursor:pointer;">`+
      `<strong>${esc(e.title||'Family event')}</strong><br><span style="font-size:.85rem;opacity:.75;">${esc(longDate(eventDate(e)))} · ${esc(e.category||'EVENT')}</span></button>`).join('');
  }

  function openReviewDrawer(){
    if(!activeDraft||!activeInsights)return;
    const c=document.getElementById('modal-container'); if(!c)return;
    const n=delta(activeDraft.start_date);
    const focus=activeInsights.titleMatch.length?activeInsights.titleMatch:activeInsights.samePerson.length?activeInsights.samePerson:activeInsights.sameDay;
    const title=n<0?'Mayil’s Past-Date Review':'Mayil’s Related Family Records';
    c.innerHTML=`<div class="modal-overlay" style="align-items:stretch;justify-content:flex-end;">
      <aside style="width:min(520px,100vw);height:100%;background:var(--surface,#fff);padding:1rem 1rem 2rem;overflow:auto;box-shadow:-10px 0 30px rgba(0,0,0,.2);">
        <div style="display:flex;justify-content:space-between;gap:1rem;align-items:center;"><div class="card-title">🌸 ${esc(title)}</div><button type="button" class="btn btn-outline btn-sm" id="femc-review-close">× Close</button></div>
        <div style="margin:1rem 0;padding:.85rem;border-radius:.7rem;background:rgba(127,127,127,.08);"><strong>${esc(activeDraft.title||'Untitled event')}</strong><br>${esc(longDate(activeDraft.start_date))} · ${esc(relative(activeDraft.start_date))}</div>
        ${n<0?`<div style="margin:.8rem 0;line-height:1.5;">This selected event is in the past. Review the precise date above, then inspect only related family records if useful. Your event draft remains open and unchanged behind this aisle.</div>`:''}
        ${focus.length?`<h4 style="margin:1.2rem 0 .4rem;">Most relevant record${focus.length>1?'s':''}</h4>${relatedRows(focus,'focus')}`:''}
        ${activeInsights.sameDay.length?`<h4 style="margin:1.2rem 0 .4rem;">Same-date records</h4>${relatedRows(activeInsights.sameDay,'sameDay')}`:''}
        ${activeInsights.around.length?`<h4 style="margin:1.2rem 0 .4rem;">Related events around this date</h4>${relatedRows(activeInsights.around,'around')}`:''}
        <div id="femc-related-detail" style="margin-top:1rem;"></div>
        <div style="position:sticky;bottom:0;background:var(--surface,#fff);padding-top:1rem;"><button type="button" class="btn" id="femc-review-return">← Return to Event Scheduler</button></div>
      </aside></div>`;
    c.style.display='block';
    const close=()=>{closeModal();setTimeout(()=>restoreDraft(activeDraft),0);};
    document.getElementById('femc-review-close').onclick=close; document.getElementById('femc-review-return').onclick=close;
    c.querySelectorAll('[data-femc-related]').forEach(btn=>btn.onclick=()=>{
      const [kind,index]=btn.dataset.femcRelated.split(':'); const e=(activeInsights[kind]||[])[Number(index)]; const detail=document.getElementById('femc-related-detail'); if(!e)return;
      detail.innerHTML=`<div style="padding:1rem;border-radius:.7rem;border:1px solid rgba(127,127,127,.18);"><strong>${esc(e.title||'Family event')}</strong><p>${esc(longDate(eventDate(e)))}</p><p>${esc(e.description||e.details||'No additional details recorded.')}</p><button type="button" class="btn btn-outline btn-sm" id="femc-related-back">Back to list</button></div>`;
      document.getElementById('femc-related-back').onclick=()=>{detail.innerHTML='';};
    });
  }

  async function mayilCheck(v){
    activeDraft=clone(v); activeMode=v.mode; activeInsights=await insightsFor(v);
    const c=document.getElementById('modal-container');if(!c)return true;
    const n=delta(v.start_date), messages=[`📅 <strong>Selected:</strong> ${esc(longDate(v.start_date))} · ${esc(relative(v.start_date))}`];
    if(n<0)messages.push('🟠 This event is in the past. Mayil is checking whether this is intentional.');
    if(activeInsights.titleMatch.length)messages.push(`🌸 Mayil found an existing record with the same title on ${esc(longDate(eventDate(activeInsights.titleMatch[0])))}.`);
    else if(activeInsights.samePerson.length)messages.push(`🌸 Mayil found a related family milestone previously recorded on ${esc(longDate(eventDate(activeInsights.samePerson[0])))}.`);
    if(activeInsights.sameDay.length)messages.push(`✨ Mayil recognized ${activeInsights.sameDay.length} existing family record${activeInsights.sameDay.length===1?'':'s'} on this same date.`);
    return await new Promise(resolve=>{
      c.innerHTML=`<div class="modal-overlay"><div class="modal-card" style="max-width:620px;"><div class="card-header"><div class="card-title">🌸 Mayil Event Check</div></div><div style="padding:.3rem 0 1rem;">${messages.map(x=>`<div style="padding:.65rem .75rem;margin:.45rem 0;border-radius:.6rem;background:rgba(127,127,127,.07);line-height:1.45;">${x}</div>`).join('')}</div><div style="font-size:.9rem;opacity:.8;margin-bottom:1rem;">Reviewing details will keep this unsaved Event Scheduler open. Nothing you entered will be lost.</div><div style="display:flex;justify-content:flex-end;gap:.5rem;flex-wrap:wrap;"><button type="button" class="btn btn-outline" id="femc-mayil-review">Review Details</button><button type="button" class="btn" id="femc-mayil-confirm">Save with This Date</button></div></div></div>`;
      c.style.display='block';
      document.getElementById('femc-mayil-review').onclick=()=>{closeModal();setTimeout(openReviewDrawer,0);resolve(false);};
      document.getElementById('femc-mayil-confirm').onclick=()=>{closeModal();resolve(true);};
    });
  }

  function addControls(form,prefix){
    if(!form||form.querySelector('.femc-event-intelligence'))return;
    const input=document.getElementById(`${prefix}evt-start-date`);if(!input)return;
    const box=document.createElement('div');box.className='form-group femc-event-intelligence';box.innerHTML=`<label class="form-label">How should Mayil understand this event?</label><div style="display:flex;gap:.5rem;flex-wrap:wrap;"><button type="button" class="btn btn-outline btn-sm" data-t="past">⏪ Past</button><button type="button" class="btn btn-outline btn-sm" data-t="today">● Today</button><button type="button" class="btn btn-outline btn-sm" data-t="future">⏩ Future</button></div><div class="femc-date-status" style="margin-top:.65rem;padding:.65rem;border-radius:.6rem;background:rgba(127,127,127,.08);"></div>`;
    input.closest('.form-group')?.before(box);const status=box.querySelector('.femc-date-status');
    const refresh=()=>status.innerHTML=input.value?`📅 <strong>${esc(longDate(input.value))}</strong><br>${esc(relative(input.value))}`:'Choose a date to see Mayil’s guidance.';
    input.addEventListener('change',refresh);refresh();
    box.querySelectorAll('[data-t]').forEach(b=>b.onclick=()=>{const d=new Date();if(b.dataset.t==='past')d.setDate(d.getDate()-1);if(b.dataset.t==='future')d.setDate(d.getDate()+1);input.value=`${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`;input.dispatchEvent(new Event('change',{bubbles:true}));});
  }

  const createOriginal=window.submitCreateEvent;
  window.submitCreateEvent=async function(evt){evt.preventDefault();const v=captureDraft('create');if(!v.start_date){alert('Please choose an event date.');return;}if(!(await mayilCheck(v)))return;return createOriginal(evt);};
  const editOriginal=window.submitPracticeEventEdit;
  window.submitPracticeEventEdit=async function(evt,eventId){evt.preventDefault();const v=captureDraft('edit',eventId);if(!v.start_date){alert('Please choose an event date.');return;}if(!(await mayilCheck(v)))return;return editOriginal(evt,eventId);};
  const openEdit=window.openPracticeEventEditor;
  if(openEdit)window.openPracticeEventEditor=async function(id){const r=await openEdit(id);setTimeout(()=>addControls(document.querySelector('form[onsubmit*="submitPracticeEventEdit"]'),'edit-'),0);return r;};
  new MutationObserver(()=>addControls(document.querySelector('form[onsubmit*="submitCreateEvent"]'),'' )).observe(document.documentElement,{childList:true,subtree:true});
})();
</script>'''
    runtime.HTML_TEMPLATE = html.replace('</body>', script + '\n</body>')


__all__ = ["install"]
