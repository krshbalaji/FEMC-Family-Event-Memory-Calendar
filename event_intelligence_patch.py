from __future__ import annotations


def install(runtime):
    html = runtime.HTML_TEMPLATE
    marker = "FEMC_EVENT_INTELLIGENCE_V4_PATCH"
    if marker in html:
        return

    script = r'''<script id="FEMC_EVENT_INTELLIGENCE_V4_PATCH">
(() => {
  const DAY_MS = 86400000;
  const pad = n => String(n).padStart(2,'0');
  const esc = v => String(v ?? '').replace(/[&<>\"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const clone = o => JSON.parse(JSON.stringify(o || {}));
  const DRAFT_KEY = 'femc.eventSchedulerDraft.v2';

  const getTimeZone = () => window.FEMC_TIME_ZONE || Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
  const zonedParts = (value = new Date(), timeZone = getTimeZone()) => {
    const parts = new Intl.DateTimeFormat('en-US', {timeZone, year:'numeric', month:'2-digit', day:'2-digit'}).formatToParts(value);
    const out = {};
    parts.forEach(p => { if (p.type !== 'literal') out[p.type] = p.value; });
    return out;
  };
  const todayISO = (timeZone = getTimeZone()) => {
    const p = zonedParts(new Date(), timeZone);
    return `${p.year}-${p.month}-${p.day}`;
  };
  const isoDay = iso => {
    const m = String(iso || '').match(/^(\d{4})-(\d{2})-(\d{2})$/);
    return m ? Math.floor(Date.UTC(Number(m[1]), Number(m[2]) - 1, Number(m[3])) / DAY_MS) : null;
  };
  const shiftISO = (iso, days) => {
    const n = isoDay(iso);
    if (n === null) return '';
    return new Date((n + days) * DAY_MS).toISOString().slice(0,10);
  };
  const longDate = iso => {
    if (!iso) return '';
    const n = isoDay(iso);
    if (n === null) return String(iso);
    return new Intl.DateTimeFormat(undefined, {timeZone:'UTC', weekday:'long', year:'numeric', month:'long', day:'numeric'}).format(new Date((n + 0.5) * DAY_MS));
  };
  const delta = (iso, timeZone = getTimeZone()) => {
    const n = isoDay(iso), t = isoDay(todayISO(timeZone));
    return n === null || t === null ? null : n - t;
  };
  const relative = iso => {
    const n = delta(iso);
    if (n === null) return '';
    if (n === 0) return 'Today';
    return n < 0 ? `${Math.abs(n)} day${Math.abs(n)===1?'':'s'} ago` : `In ${n} day${n===1?'':'s'}`;
  };
  const eventList = d => d?.calendar || d?.events || d?.items || [];
  const eventDate = e => String(e?.start_date || e?.date || e?.start_time || '').slice(0,10);
  const normalize = x => String(x || '').trim().toUpperCase();

  let activeDraft = null;
  let activeInsights = null;
  let createOpenOriginal = null;
  let editOpenOriginal = null;
  let createSubmitOriginal = null;
  let editSubmitOriginal = null;

  function saveDraft(d) { try { sessionStorage.setItem(DRAFT_KEY, JSON.stringify(d)); } catch (_) {} }
  function loadDraft() { try { return clone(JSON.parse(sessionStorage.getItem(DRAFT_KEY) || 'null')); } catch (_) { return null; } }
  function clearDraft() { try { sessionStorage.removeItem(DRAFT_KEY); } catch (_) {} }

  function captureDraft(mode, eventId) {
    const p = mode === 'edit' ? 'edit-' : '';
    return {
      mode, eventId:eventId || null,
      title:document.getElementById(`${p}evt-title`)?.value || '',
      category:document.getElementById(`${p}evt-cat`)?.value || 'GENERAL',
      start_date:document.getElementById(`${p}evt-start-date`)?.value || '',
      start_time:document.getElementById(`${p}evt-start-time`)?.value || '',
      end_date:document.getElementById(`${p}evt-end-date`)?.value || '',
      end_time:document.getElementById(`${p}evt-end-time`)?.value || '',
      description:document.getElementById(`${p}evt-description`)?.value || document.getElementById(`${p}evt-desc`)?.value || '',
      visibility:document.getElementById(`${p}evt-visibility`)?.value || '',
      people:Array.from(document.querySelectorAll(`input[name="${mode==='edit'?'edit_target_persons':'target_persons'}"]:checked`)).map(x=>String(x.value)),
      time_zone:getTimeZone(), saved_at:new Date().toISOString()
    };
  }

  function restoreDraft(d) {
    if (!d) return;
    const p = d.mode === 'edit' ? 'edit-' : '';
    const set = (id, value) => {
      const el = document.getElementById(id);
      if (!el || value === undefined) return;
      el.value = value;
      el.dispatchEvent(new Event('input', {bubbles:true}));
      el.dispatchEvent(new Event('change', {bubbles:true}));
    };
    set(`${p}evt-title`, d.title); set(`${p}evt-cat`, d.category); set(`${p}evt-start-date`, d.start_date); set(`${p}evt-start-time`, d.start_time); set(`${p}evt-end-date`, d.end_date); set(`${p}evt-end-time`, d.end_time);
    const desc = document.getElementById(`${p}evt-description`) || document.getElementById(`${p}evt-desc`);
    if (desc) { desc.value = d.description || ''; desc.dispatchEvent(new Event('input', {bubbles:true})); desc.dispatchEvent(new Event('change', {bubbles:true})); }
    set(`${p}evt-visibility`, d.visibility);
    const name = d.mode === 'edit' ? 'edit_target_persons' : 'target_persons';
    document.querySelectorAll(`input[name="${name}"]`).forEach(x => { x.checked = (d.people || []).includes(String(x.value)); x.dispatchEvent(new Event('change', {bubbles:true})); });
  }

  function wireDraftPersistence(form, mode, eventId) {
    if (!form || form.dataset.femcDraftPersistence) return;
    form.dataset.femcDraftPersistence = '1';
    const persist = () => {
      const d = captureDraft(mode, eventId);
      if (d.title || d.start_date || d.description || d.people.length) saveDraft(d);
    };
    form.addEventListener('input', persist, true);
    form.addEventListener('change', persist, true);
  }

  async function reopenSchedulerFromDraft() {
    const d = clone(activeDraft || loadDraft());
    if (!d) return;
    if (d.mode === 'edit' && editOpenOriginal && d.eventId) await editOpenOriginal(d.eventId);
    else if (createOpenOriginal) await createOpenOriginal();
    else return;
    setTimeout(() => {
      restoreDraft(d);
      const form = document.querySelector(d.mode === 'edit' ? 'form[onsubmit*="submitPracticeEventEdit"]' : 'form[onsubmit*="submitCreateEvent"]');
      addControls(form, d.mode === 'edit' ? 'edit-' : '');
      wireDraftPersistence(form, d.mode, d.eventId);
      saveDraft(captureDraft(d.mode, d.eventId));
    }, 80);
  }

  async function insightsFor(v) {
    let history = [];
    try { history = eventList(await fetchAPI('/api/events')); } catch (_) {}
    const other = history.filter(e => String(e.id || e.event_id || '') !== String(v.eventId || ''));
    const sameDay = other.filter(e => eventDate(e) === v.start_date);
    const samePerson = other.filter(e => normalize(e.category) === normalize(v.category) && (e.target_person_ids || e.person_ids || []).map(String).some(id => (v.people || []).includes(id)));
    const titleMatch = other.filter(e => String(e.title || '').trim().toLowerCase() === String(v.title || '').trim().toLowerCase());
    const around = other.filter(e => { const a = isoDay(eventDate(e)), b = isoDay(v.start_date); return a !== null && b !== null && Math.abs(a-b) <= 7; }).sort((a,b) => eventDate(a).localeCompare(eventDate(b)));
    return {sameDay, samePerson, titleMatch, around};
  }

  function relatedRows(list, kind) {
    if (!list?.length) return '<div style="opacity:.72;padding:.6rem 0;">No related records found.</div>';
    return list.slice(0,12).map((e,i) => `<button type="button" class="femc-related-row" data-femc-related="${kind}:${i}" style="width:100%;text-align:left;border:1px solid rgba(127,127,127,.18);background:rgba(127,127,127,.05);border-radius:.65rem;padding:.75rem;margin:.35rem 0;cursor:pointer;"><strong>${esc(e.title || 'Family event')}</strong><br><span style="font-size:.85rem;opacity:.75;">${esc(longDate(eventDate(e)))} · ${esc(e.category || 'EVENT')}</span></button>`).join('');
  }

  async function returnToScheduler() { closeModal(); await reopenSchedulerFromDraft(); }

  function openReviewDrawer() {
    if (!activeDraft || !activeInsights) return;
    const c = document.getElementById('modal-container'); if (!c) return;
    const n = delta(activeDraft.start_date);
    const focus = activeInsights.titleMatch.length ? activeInsights.titleMatch : activeInsights.samePerson.length ? activeInsights.samePerson : activeInsights.sameDay;
    const title = n < 0 ? 'Mayil’s Past-Date Review' : 'Mayil’s Related Family Records';
    c.innerHTML = `<div class="modal-overlay" style="align-items:stretch;justify-content:flex-end;"><aside style="width:min(520px,100vw);height:100%;background:var(--surface,#fff);padding:1rem 1rem 2rem;overflow:auto;box-shadow:-10px 0 30px rgba(0,0,0,.2);"><div style="display:flex;justify-content:space-between;gap:1rem;align-items:center;"><div class="card-title">🌸 ${esc(title)}</div><button type="button" class="btn btn-outline btn-sm" id="femc-review-close">× Close</button></div><div style="margin:1rem 0;padding:.85rem;border-radius:.7rem;background:rgba(127,127,127,.08);"><strong>${esc(activeDraft.title || 'Untitled event')}</strong><br>${esc(longDate(activeDraft.start_date))} · ${esc(relative(activeDraft.start_date))}<br><span style="font-size:.8rem;opacity:.72;">Timezone: ${esc(getTimeZone())}</span></div>${n<0?`<div style="margin:.8rem 0;line-height:1.5;">This selected event is in the past. Review the precise date above, then inspect only related family records if useful. Your event draft is preserved exactly and will reopen when you return.</div>`:''}${focus.length?`<h4 style="margin:1.2rem 0 .4rem;">Most relevant record${focus.length>1?'s':''}</h4>${relatedRows(focus,'focus')}`:''}${activeInsights.sameDay.length?`<h4 style="margin:1.2rem 0 .4rem;">Same-date records</h4>${relatedRows(activeInsights.sameDay,'sameDay')}`:''}${activeInsights.around.length?`<h4 style="margin:1.2rem 0 .4rem;">Related events around this date</h4>${relatedRows(activeInsights.around,'around')}`:''}<div id="femc-related-detail" style="margin-top:1rem;"></div><div style="position:sticky;bottom:0;background:var(--surface,#fff);padding-top:1rem;"><button type="button" class="btn" id="femc-review-return">← Return to Event Scheduler</button></div></aside></div>`;
    c.style.display = 'block';
    document.getElementById('femc-review-close').onclick = returnToScheduler;
    document.getElementById('femc-review-return').onclick = returnToScheduler;
    c.querySelectorAll('[data-femc-related]').forEach(btn => btn.onclick = () => {
      const [kind,index] = btn.dataset.femcRelated.split(':'); const e = (activeInsights[kind] || [])[Number(index)]; const detail = document.getElementById('femc-related-detail'); if (!e || !detail) return;
      detail.innerHTML = `<div style="padding:1rem;border-radius:.7rem;border:1px solid rgba(127,127,127,.18);"><strong>${esc(e.title || 'Family event')}</strong><p>${esc(longDate(eventDate(e)))}</p><p>${esc(e.description || e.details || 'No additional details recorded.')}</p><button type="button" class="btn btn-outline btn-sm" id="femc-related-back">Back to list</button></div>`;
      document.getElementById('femc-related-back').onclick = () => { detail.innerHTML = ''; };
    });
  }

  async function mayilCheck(v) {
    activeDraft = clone(v); saveDraft(activeDraft); activeInsights = await insightsFor(v);
    const c = document.getElementById('modal-container'); if (!c) return true;
    const n = delta(v.start_date);
    const messages = [`📅 <strong>Selected:</strong> ${esc(longDate(v.start_date))} · ${esc(relative(v.start_date))}`, `🌐 <strong>Timezone:</strong> ${esc(getTimeZone())} · <strong>Today:</strong> ${esc(longDate(todayISO()))}`];
    if (n < 0) messages.push('🟠 This event is in the past. Mayil is checking whether this is intentional.');
    if (activeInsights.titleMatch.length) messages.push(`🌸 Mayil found an existing record with the same title on ${esc(longDate(eventDate(activeInsights.titleMatch[0])))}.`);
    else if (activeInsights.samePerson.length) messages.push(`🌸 Mayil found a related family milestone previously recorded on ${esc(longDate(eventDate(activeInsights.samePerson[0])))}.`);
    if (activeInsights.sameDay.length) messages.push(`✨ Mayil recognized ${activeInsights.sameDay.length} existing family record${activeInsights.sameDay.length===1?'':'s'} on this same date.`);
    return await new Promise(resolve => {
      c.innerHTML = `<div class="modal-overlay"><div class="modal-card" style="max-width:620px;"><div class="card-header"><div class="card-title">🌸 Mayil Event Check</div></div><div style="padding:.3rem 0 1rem;">${messages.map(x=>`<div style="padding:.65rem .75rem;margin:.45rem 0;border-radius:.6rem;background:rgba(127,127,127,.07);line-height:1.45;">${x}</div>`).join('')}</div><div style="font-size:.9rem;opacity:.8;margin-bottom:1rem;">Reviewing details preserves this unsaved scheduler draft in this browser session. Return will reopen the same Event Scheduler with every field intact.</div><div style="display:flex;justify-content:flex-end;gap:.5rem;flex-wrap:wrap;"><button type="button" class="btn btn-outline" id="femc-mayil-review">Review Details</button><button type="button" class="btn" id="femc-mayil-confirm">Save with This Date</button></div></div></div>`;
      c.style.display = 'block';
      document.getElementById('femc-mayil-review').onclick = () => { closeModal(); setTimeout(openReviewDrawer, 0); resolve(false); };
      document.getElementById('femc-mayil-confirm').onclick = () => { closeModal(); resolve(true); };
    });
  }

  function enhanceOneInput(el, type) {
    if (!el || el.dataset.femcPickerEnhanced) return;
    el.dataset.femcPickerEnhanced = '1'; el.type = type; el.inputMode = type === 'time' ? 'numeric' : 'text';
    const hint = document.createElement('div'); hint.style.cssText = 'display:flex;align-items:center;justify-content:space-between;gap:.5rem;margin-top:.35rem;font-size:.78rem;opacity:.72;';
    hint.innerHTML = `<span>${type==='date'?'Type the date or use the calendar':'Type the time or use the clock'}</span><button type="button" class="btn btn-outline btn-sm" style="padding:.2rem .45rem;" data-femc-open-picker>${type==='date'?'📅 Calendar':'🕒 Clock'}</button>`;
    el.insertAdjacentElement('afterend', hint);
    hint.querySelector('[data-femc-open-picker]').onclick = () => { try { el.showPicker?.(); } catch (_) { el.focus(); } };
  }

  function enhanceDateTimeInputs(prefix='') {
    ['start-date','end-date'].forEach(x => enhanceOneInput(document.getElementById(`${prefix}evt-${x}`), 'date'));
    ['start-time','end-time'].forEach(x => enhanceOneInput(document.getElementById(`${prefix}evt-${x}`), 'time'));
  }

  function addControls(form, prefix) {
    if (!form) return;
    enhanceDateTimeInputs(prefix);
    const mode = prefix === 'edit-' ? 'edit' : 'create';
    const eventId = form.dataset.eventId || null;
    wireDraftPersistence(form, mode, eventId);
    if (form.querySelector('.femc-event-intelligence')) return;
    const input = document.getElementById(`${prefix}evt-start-date`); if (!input) return;
    const box = document.createElement('div'); box.className = 'form-group femc-event-intelligence';
    box.innerHTML = `<label class="form-label">How should Mayil understand this event?</label><div style="display:flex;gap:.5rem;flex-wrap:wrap;"><button type="button" class="btn btn-outline btn-sm" data-t="past">⏪ Past</button><button type="button" class="btn btn-outline btn-sm" data-t="today">● Today</button><button type="button" class="btn btn-outline btn-sm" data-t="future">⏩ Future</button></div><div class="femc-date-status" style="margin-top:.65rem;padding:.65rem;border-radius:.6rem;background:rgba(127,127,127,.08);"></div>`;
    input.closest('.form-group')?.before(box);
    const status = box.querySelector('.femc-date-status');
    const refresh = () => { status.innerHTML = input.value ? `📅 <strong>${esc(longDate(input.value))}</strong><br>${esc(relative(input.value))}<br><span style="font-size:.78rem;opacity:.72;">Timezone: ${esc(getTimeZone())}</span>` : `Choose a date to see Mayil’s guidance.<br><span style="font-size:.78rem;opacity:.72;">Timezone: ${esc(getTimeZone())}</span>`; };
    input.addEventListener('change', refresh); refresh();
    box.querySelectorAll('[data-t]').forEach(b => b.onclick = () => {
      const base = todayISO(); const next = b.dataset.t === 'past' ? shiftISO(base,-1) : b.dataset.t === 'future' ? shiftISO(base,1) : base;
      input.value = next; input.dispatchEvent(new Event('input', {bubbles:true})); input.dispatchEvent(new Event('change', {bubbles:true}));
    });
  }

  async function runOriginalSubmit(original, ctx, args) {
    const result = await original.apply(ctx, args);
    clearDraft(); activeDraft = null; activeInsights = null;
    return result;
  }

  function installSubmitGuards() {
    if (!createSubmitOriginal && typeof window.submitCreateEvent === 'function' && !window.submitCreateEvent.__femcV4) {
      createSubmitOriginal = window.submitCreateEvent;
      const guarded = async function(evt) {
        evt?.preventDefault?.(); const v = captureDraft('create'); if (!v.start_date) { alert('Please choose an event date.'); return; }
        if (!(await mayilCheck(v))) return;
        return runOriginalSubmit(createSubmitOriginal, this, [evt]);
      };
      guarded.__femcV4 = true; window.submitCreateEvent = guarded;
    }
    if (!editSubmitOriginal && typeof window.submitPracticeEventEdit === 'function' && !window.submitPracticeEventEdit.__femcV4) {
      editSubmitOriginal = window.submitPracticeEventEdit;
      const guarded = async function(evt,eventId) {
        evt?.preventDefault?.(); const v = captureDraft('edit', eventId); if (!v.start_date) { alert('Please choose an event date.'); return; }
        if (!(await mayilCheck(v))) return;
        return runOriginalSubmit(editSubmitOriginal, this, [evt,eventId]);
      };
      guarded.__femcV4 = true; window.submitPracticeEventEdit = guarded;
    }
  }

  function installOpenWrappers() {
    if (!createOpenOriginal && typeof window.openCreateEventModal === 'function' && !window.openCreateEventModal.__femcV4) {
      createOpenOriginal = window.openCreateEventModal;
      const wrapped = async function() {
        const r = await createOpenOriginal.apply(this, arguments);
        setTimeout(() => { const form = document.querySelector('form[onsubmit*="submitCreateEvent"]'); addControls(form,''); const d = loadDraft(); if (d && d.mode === 'create') restoreDraft(d); }, 0);
        return r;
      };
      wrapped.__femcV4 = true; window.openCreateEventModal = wrapped;
    }
    if (!editOpenOriginal && typeof window.openPracticeEventEditor === 'function' && !window.openPracticeEventEditor.__femcV4) {
      editOpenOriginal = window.openPracticeEventEditor;
      const wrapped = async function(id) { const r = await editOpenOriginal.apply(this, arguments); setTimeout(() => addControls(document.querySelector('form[onsubmit*="submitPracticeEventEdit"]'),'edit-'),0); return r; };
      wrapped.__femcV4 = true; window.openPracticeEventEditor = wrapped;
    }
  }

  function installAll() {
    installSubmitGuards(); installOpenWrappers();
    addControls(document.querySelector('form[onsubmit*="submitCreateEvent"]'),'');
    addControls(document.querySelector('form[onsubmit*="submitPracticeEventEdit"]'),'edit-');
  }

  installAll();
  new MutationObserver(installAll).observe(document.documentElement,{childList:true,subtree:true});
})();
</script>'''
    runtime.HTML_TEMPLATE = html.replace('</body>', script + '\n</body>')


__all__ = ["install"]
