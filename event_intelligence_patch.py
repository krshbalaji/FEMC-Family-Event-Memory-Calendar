from __future__ import annotations


def install(runtime):
    html = runtime.HTML_TEMPLATE
    marker = "FEMC_EVENT_INTELLIGENCE_V1_PATCH"
    if marker in html:
        return

    script = r'''<script id="FEMC_EVENT_INTELLIGENCE_V1_PATCH">
(() => {
  const DAY_MS = 24 * 60 * 60 * 1000;
  const pad = n => String(n).padStart(2, '0');
  const isoToday = () => { const d = new Date(); return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`; };
  const weekday = iso => { const d = new Date(`${iso}T12:00:00`); return isNaN(d) ? '' : new Intl.DateTimeFormat(undefined,{weekday:'long'}).format(d); };
  const longDate = iso => { const d = new Date(`${iso}T12:00:00`); return isNaN(d) ? iso : new Intl.DateTimeFormat(undefined,{weekday:'long',year:'numeric',month:'long',day:'numeric'}).format(d); };
  const dayDelta = iso => {
    if (!iso) return null;
    const today = new Date(); today.setHours(0,0,0,0);
    const selected = new Date(`${iso}T00:00:00`); selected.setHours(0,0,0,0);
    return Math.round((selected - today) / DAY_MS);
  };
  const temporalText = iso => {
    const n = dayDelta(iso); const day = weekday(iso);
    if (n === null) return '';
    if (n === 0) return `Today — ${day}`;
    if (n < 0) return `${Math.abs(n)} day${Math.abs(n)===1?'':'s'} ago — ${day}`;
    return `In ${n} day${n===1?'':'s'} — ${day}`;
  };
  const esc = value => String(value ?? '').replace(/[&<>\"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const eventList = data => data?.calendar || data?.events || data?.items || [];
  const eventDate = e => String(e?.start_date || e?.date || e?.start_time || '').slice(0,10);
  const normalize = x => String(x || '').trim().toUpperCase();

  function addDateIntelligence(form, prefix) {
    if (!form || form.querySelector('.femc-event-intelligence')) return;
    const dateInput = document.getElementById(`${prefix}evt-start-date`);
    const endDate = document.getElementById(`${prefix}evt-end-date`);
    if (!dateInput) return;
    const box = document.createElement('div');
    box.className = 'form-group femc-event-intelligence';
    box.innerHTML = `
      <label class="form-label">How should Mayil understand this event?</label>
      <div style="display:flex;gap:.5rem;flex-wrap:wrap;margin-bottom:.65rem;">
        <button type="button" class="btn btn-outline btn-sm" data-femc-temporal="past">⏪ Past</button>
        <button type="button" class="btn btn-outline btn-sm" data-femc-temporal="today">● Today</button>
        <button type="button" class="btn btn-outline btn-sm" data-femc-temporal="future">⏩ Future</button>
      </div>
      <div class="femc-date-status" style="font-size:.9rem;line-height:1.45;padding:.7rem .8rem;border-radius:.6rem;background:rgba(127,127,127,.08);"></div>
      <div style="font-size:.78rem;opacity:.72;margin-top:.45rem;">Mayil will review the final date and family records before saving. You always decide.</div>`;
    dateInput.closest('.form-group')?.before(box);
    const status = box.querySelector('.femc-date-status');
    const refresh = () => {
      const iso = dateInput.value;
      if (!iso) { status.textContent = 'Choose a date to see Mayil’s date guidance.'; return; }
      const n = dayDelta(iso);
      const icon = n < 0 ? '🟠' : n === 0 ? '🔵' : '🟢';
      status.innerHTML = `${icon} <strong>${esc(longDate(iso))}</strong><br>${esc(temporalText(iso))}`;
    };
    dateInput.addEventListener('change', refresh); refresh();
    box.querySelectorAll('[data-femc-temporal]').forEach(btn => btn.addEventListener('click', () => {
      const mode = btn.dataset.femcTemporal;
      const d = new Date();
      if (mode === 'past') d.setDate(d.getDate()-1);
      if (mode === 'future') d.setDate(d.getDate()+1);
      const iso = `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`;
      dateInput.value = iso;
      if (endDate && !endDate.value) endDate.value = iso;
      refresh();
    }));
  }

  async function collectInsights(values) {
    const selectedDate = values.start_date;
    const selectedCategory = normalize(values.category);
    const selectedIds = new Set(values.target_person_ids || []);
    let history = [];
    try { history = eventList(await fetchAPI('/api/events')); } catch (_) {}
    const sameDay = history.filter(e => eventDate(e) === selectedDate && String(e.id || e.event_id || '') !== String(values.event_id || ''));
    const sameCategory = history.filter(e => normalize(e.category) === selectedCategory && eventDate(e) && String(e.id || e.event_id || '') !== String(values.event_id || ''));
    const samePeople = sameCategory.filter(e => {
      const ids = new Set(e.target_person_ids || e.person_ids || []);
      return [...selectedIds].some(id => ids.has(id));
    });
    const titleHint = String(values.title || '').trim().toLowerCase();
    const titleMatches = sameCategory.filter(e => String(e.title || '').trim().toLowerCase() === titleHint);
    return { selectedDate, sameDay, samePeople, titleMatches };
  }

  function personName(id) {
    const p = (window.membersData || []).find(x => String(x.person_id) === String(id));
    return p?.name || 'selected family member';
  }

  function insightLines(values, insights) {
    const lines = [];
    const n = dayDelta(values.start_date);
    lines.push(`📅 <strong>Selected:</strong> ${esc(longDate(values.start_date))} · ${esc(temporalText(values.start_date))}`);
    if (n < 0) lines.push('🟠 This event is in the past. Mayil is checking whether you intentionally want to record it as a past family event.');
    if (insights.titleMatches.length) {
      const prior = insights.titleMatches[0];
      lines.push(`🌸 <strong>Possible existing family record:</strong> “${esc(prior.title)}” is already recorded on ${esc(longDate(eventDate(prior)))}.`);
    } else if (insights.samePeople.length) {
      const prior = insights.samePeople[0];
      const names = (values.target_person_ids || []).map(personName).join(', ') || 'This family member';
      lines.push(`🌸 <strong>Family date comparison:</strong> ${esc(names)} has a previously recorded ${esc(String(prior.category || 'event').toLowerCase())} on ${esc(longDate(eventDate(prior)))}. Your selected date is ${esc(longDate(values.start_date))}. This may be a separate celebration date.`);
    }
    if (insights.sameDay.length) {
      const other = insights.sameDay[0];
      const otherIds = other.target_person_ids || other.person_ids || [];
      const differentPeople = otherIds.length && !(values.target_person_ids || []).some(id => otherIds.includes(id));
      if (differentPeople) lines.push(`✨ <strong>Shared-date recognition:</strong> ${esc(longDate(values.start_date))} is already recorded for “${esc(other.title || 'another family event')}”. Are both family occasions intentionally on the same date?`);
      else lines.push(`✨ <strong>Same-date recognition:</strong> This date already has “${esc(other.title || 'a family event')}”. Mayil is asking for assurance so you can avoid an accidental duplicate.`);
    }
    return lines;
  }

  async function mayilConfirm(values) {
    const insights = await collectInsights(values);
    const lines = insightLines(values, insights);
    const container = document.getElementById('modal-container');
    if (!container) return true;
    return await new Promise(resolve => {
      container.innerHTML = `
        <div class="modal-overlay">
          <div class="modal-card" style="max-width:620px;">
            <div class="card-header"><div class="card-title">🌸 Mayil Event Check</div></div>
            <div style="padding:.3rem 0 1rem;">${lines.map(x => `<div style="padding:.65rem .75rem;margin:.45rem 0;border-radius:.6rem;background:rgba(127,127,127,.07);line-height:1.45;">${x}</div>`).join('')}</div>
            <div style="font-size:.9rem;opacity:.8;margin-bottom:1rem;">Mayil recognized these dates and family records. Nothing will be changed unless you choose it.</div>
            <div style="display:flex;justify-content:flex-end;gap:.5rem;flex-wrap:wrap;">
              <button type="button" class="btn btn-outline" id="femc-mayil-review">← Review Details</button>
              <button type="button" class="btn" id="femc-mayil-confirm">✓ Save with This Date</button>
            </div>
          </div>
        </div>`;
      container.style.display = 'block';
      document.getElementById('femc-mayil-review').onclick = () => { closeModal(); resolve(false); };
      document.getElementById('femc-mayil-confirm').onclick = () => { closeModal(); resolve(true); };
    });
  }

  function createValues() {
    return {
      title: document.getElementById('evt-title')?.value.trim() || '',
      category: document.getElementById('evt-cat')?.value || 'GENERAL',
      start_date: document.getElementById('evt-start-date')?.value || '',
      start_time: document.getElementById('evt-start-time')?.value || '',
      end_date: document.getElementById('evt-end-date')?.value || '',
      end_time: document.getElementById('evt-end-time')?.value || '',
      target_person_ids: Array.from(document.querySelectorAll('input[name="target_persons"]:checked')).map(x => x.value)
    };
  }

  function editValues(eventId) {
    return {
      event_id: eventId,
      title: document.getElementById('edit-evt-title')?.value.trim() || '',
      category: document.getElementById('edit-evt-cat')?.value || 'GENERAL',
      start_date: document.getElementById('edit-evt-start-date')?.value || '',
      start_time: document.getElementById('edit-evt-start-time')?.value || '',
      end_date: document.getElementById('edit-evt-end-date')?.value || '',
      end_time: document.getElementById('edit-evt-end-time')?.value || '',
      target_person_ids: Array.from(document.querySelectorAll('input[name="edit_target_persons"]:checked')).map(x => x.value)
    };
  }

  function hookCreateForm() {
    const form = document.querySelector('form[onsubmit*="submitCreateEvent"]');
    addDateIntelligence(form, '');
  }

  const originalOpenEditor = window.openPracticeEventEditor;
  window.openPracticeEventEditor = async function(eventId) {
    const result = await originalOpenEditor(eventId);
    setTimeout(() => addDateIntelligence(document.querySelector('form[onsubmit*="submitPracticeEventEdit"]'), 'edit-'), 0);
    return result;
  };

  const originalCreate = window.submitCreateEvent;
  window.submitCreateEvent = async function(evt) {
    evt.preventDefault();
    const values = createValues();
    if (!values.start_date) { alert('Please choose an event date.'); return; }
    if (!(await mayilConfirm(values))) return;
    return originalCreate(evt);
  };

  const originalEdit = window.submitPracticeEventEdit;
  window.submitPracticeEventEdit = async function(evt, eventId) {
    evt.preventDefault();
    const values = editValues(eventId);
    if (!values.start_date) { alert('Please choose an event date.'); return; }
    if (!(await mayilConfirm(values))) return;
    return originalEdit(evt, eventId);
  };

  const observer = new MutationObserver(() => hookCreateForm());
  observer.observe(document.documentElement, {childList:true, subtree:true});
})();
</script>'''
    runtime.HTML_TEMPLATE = html.replace('</body>', script + '\n</body>')


__all__ = ["install"]
