from __future__ import annotations


def install(runtime):
    marker = "FEMC_MAYIL_SCHEDULE_AWARENESS_V1"
    if marker in runtime.HTML_TEMPLATE:
        return

    script = r'''<script id="FEMC_MAYIL_SCHEDULE_AWARENESS_V1">
(() => {
  const esc = v => String(v ?? '').replace(/[&<>\"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const tz = () => window.FEMC_TIME_ZONE || Intl.DateTimeFormat().resolvedOptions().timeZone || 'Asia/Kolkata';
  const field = id => document.getElementById(id);
  const clean = v => String(v || '').trim().toLowerCase().replace(/\s+/g, ' ');
  const eventList = d => Array.isArray(d) ? d : (d?.calendar || d?.events || d?.items || []);
  const dateOf = e => String(e?.start_date || e?.date || e?.start_time || '').slice(0, 10);
  const identityOf = e => String(e?.id || e?.event_id || '');

  function timeOf(value) {
    const s = String(value || '');
    const m = s.match(/T(\d{2}:\d{2})/) || s.match(/\b(\d{1,2}:\d{2})\b/);
    if (!m) return '';
    const [h, min] = m[1].split(':');
    return `${String(Number(h)).padStart(2,'0')}:${min}`;
  }

  function minutes(value) {
    const t = timeOf(value);
    if (!t) return null;
    const [h, m] = t.split(':').map(Number);
    return h * 60 + m;
  }

  async function getEvents() {
    try {
      const r = await fetch('/api/events', {credentials:'same-origin'});
      if (!r.ok) return [];
      return eventList(await r.json());
    } catch (_) { return []; }
  }

  function captureCreate() {
    return {
      mode:'create', eventId:'', title:(field('evt-title')?.value || '').trim(),
      start_date:field('evt-start-date')?.value || '', start_time:field('evt-start-time')?.value || '',
      end_date:field('evt-end-date')?.value || field('evt-start-date')?.value || '',
      end_time:field('evt-end-time')?.value || '', time_zone:tz()
    };
  }

  function captureEdit(eventId) {
    return {
      mode:'edit', eventId:String(eventId || ''), title:(field('edit-evt-title')?.value || '').trim(),
      start_date:field('edit-evt-start-date')?.value || '', start_time:field('edit-evt-start-time')?.value || '',
      end_date:field('edit-evt-end-date')?.value || field('edit-evt-start-date')?.value || '',
      end_time:field('edit-evt-end-time')?.value || '', time_zone:tz()
    };
  }

  function overlaps(d, e) {
    if (!d.start_date || dateOf(e) !== d.start_date) return false;
    const aStart = minutes(d.start_time), aEnd = minutes(d.end_time || d.start_time);
    const bStart = minutes(e.start_time), bEnd = minutes(e.end_time || e.start_time);
    if (aStart === null || bStart === null) return false;
    const aaEnd = aEnd === null || aEnd <= aStart ? aStart + 1 : aEnd;
    const bbEnd = bEnd === null || bEnd <= bStart ? bStart + 1 : bEnd;
    return aStart < bbEnd && bStart < aaEnd;
  }

  function analyze(d, events) {
    const others = events.filter(e => identityOf(e) !== String(d.eventId || ''));
    const exact = others.filter(e => clean(e?.title) === clean(d.title) && dateOf(e) === d.start_date && timeOf(e?.start_time) === timeOf(d.start_time));
    const clashes = others.filter(e => overlaps(d, e) && !exact.includes(e));
    const sameSlot = others.filter(e => dateOf(e) === d.start_date && timeOf(e?.start_time) === timeOf(d.start_time) && !exact.includes(e) && !clashes.includes(e));
    return {exact, clashes, sameSlot};
  }

  function row(e) {
    const when = `${dateOf(e) || 'Unknown date'}${timeOf(e?.start_time) ? ` · ${timeOf(e.start_time)}` : ''}`;
    return `<div style="padding:.65rem .75rem;margin:.45rem 0;border-radius:.6rem;background:rgba(127,127,127,.07);line-height:1.4;"><strong>${esc(e?.title || 'Family event')}</strong><br><span style="font-size:.84rem;opacity:.78;">${esc(when)}</span></div>`;
  }

  async function mayilAwareness(d) {
    const found = analyze(d, await getEvents());
    const total = found.exact.length + found.clashes.length + found.sameSlot.length;
    if (!total) return true;
    const c = document.getElementById('modal-container');
    if (!c) return true;

    const exactText = found.exact.length ? `<div style="padding:.7rem .8rem;border-radius:.65rem;background:rgba(255,180,80,.10);margin-bottom:.65rem;">🌸 <strong>Mayil noticed a matching event.</strong><br>The same title, date and start time already appear in the family schedule. Please check the scheduled event once before saving.</div>${found.exact.slice(0,3).map(row).join('')}` : '';
    const clashText = found.clashes.length ? `<div style="padding:.7rem .8rem;border-radius:.65rem;background:rgba(255,120,120,.10);margin:.65rem 0;">🕒 <strong>Mayil also noticed a possible time clash.</strong><br>A different event overlaps this date and time. It may be intentional, but please check the schedule once before saving.</div>${found.clashes.slice(0,5).map(row).join('')}` : '';
    const slotText = found.sameSlot.length ? `<div style="padding:.7rem .8rem;border-radius:.65rem;background:rgba(120,190,255,.10);margin:.65rem 0;">📅 <strong>Mayil found another event at the same date and time.</strong><br>This may be correct, but please review the scheduled events once to make sure the timing is what you intend.</div>${found.sameSlot.slice(0,5).map(row).join('')}` : '';

    return new Promise(resolve => {
      c.innerHTML = `<div class="modal-overlay"><div class="modal-card" style="max-width:650px;"><div class="card-header"><div class="card-title">🌸 Mayil Schedule Awareness</div></div><div style="padding:.35rem 0 1rem;"><div style="padding:.65rem .75rem;border-radius:.6rem;background:rgba(127,127,127,.07);margin-bottom:.65rem;"><strong>${esc(d.title || 'This event')}</strong><br>${esc(d.start_date)}${timeOf(d.start_time) ? ` · ${esc(timeOf(d.start_time))}` : ''}</div>${exactText}${clashText}${slotText}<div style="font-size:.9rem;opacity:.82;margin-top:.8rem;">Mayil is only bringing this relationship to your attention. Nothing is blocked. If the details are correct, you can continue and save.</div></div><div style="display:flex;justify-content:flex-end;gap:.5rem;flex-wrap:wrap;"><button type="button" class="btn btn-outline" id="femc-mayil-check-form">Check Form Again</button><button type="button" class="btn" id="femc-mayil-continue">Continue to Save</button></div></div></div>`;
      c.style.display = 'block';
      document.getElementById('femc-mayil-check-form').onclick = () => { c.style.display = 'none'; resolve(false); };
      document.getElementById('femc-mayil-continue').onclick = () => { c.style.display = 'none'; resolve(true); };
    });
  }

  function installCreate() {
    const current = window.submitCreateEvent;
    if (typeof current !== 'function' || current.__femcMayilScheduleAwarenessV1) return;
    const guarded = async function(evt, ...rest) {
      const draft = captureCreate();
      if (draft.title && draft.start_date && draft.start_time && !(await mayilAwareness(draft))) return false;
      return current.call(this, evt, ...rest);
    };
    guarded.__femcMayilScheduleAwarenessV1 = true;
    guarded.__femcAtomicSaveV1 = true;
    guarded.__femcV5 = true;
    window.submitCreateEvent = guarded;
  }

  function installEdit() {
    const current = window.submitPracticeEventEdit;
    if (typeof current !== 'function' || current.__femcMayilScheduleAwarenessV1) return;
    const guarded = async function(evt, eventId, ...rest) {
      evt?.preventDefault?.();
      const draft = captureEdit(eventId);
      if (draft.title && draft.start_date && draft.start_time && !(await mayilAwareness(draft))) return false;
      return current.call(this, evt, eventId, ...rest);
    };
    guarded.__femcMayilScheduleAwarenessV1 = true;
    window.submitPracticeEventEdit = guarded;
  }

  function install() { installCreate(); installEdit(); }
  install();
  new MutationObserver(install).observe(document.documentElement,{childList:true,subtree:true});
  setInterval(install,300);
})();
</script>'''
    runtime.HTML_TEMPLATE = runtime.HTML_TEMPLATE.replace('</body>', script + '\n</body>')


__all__ = ['install']
