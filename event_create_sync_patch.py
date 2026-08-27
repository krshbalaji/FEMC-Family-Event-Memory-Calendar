from __future__ import annotations


def install(runtime):
    html = runtime.HTML_TEMPLATE
    marker = "FEMC_PRACTICE_EVENT_CREATE_SYNC_PATCH"
    if marker in html:
        return

    script = r'''<script id="FEMC_PRACTICE_EVENT_CREATE_SYNC_PATCH">
(() => {
  const field = (...ids) => {
    for (const id of ids) {
      const el = document.getElementById(id);
      if (el) return el;
    }
    return null;
  };
  const value = (...ids) => String(field(...ids)?.value ?? '');

  window.submitCreateEvent = async function (evt) {
    evt.preventDefault();

    // The scheduler has evolved field ids over time. Resolve the live form
    // defensively instead of assuming a legacy id still exists.
    const title = value('evt-title').trim();
    const category = value('evt-cat') || 'GENERAL';
    const visibility = value('evt-visibility', 'evt-vis') || 'FAMILY';
    const description = value('evt-description', 'evt-desc').trim();
    const startDate = value('evt-start-date');
    const startTime = value('evt-start-time');
    const endDate = value('evt-end-date') || startDate;
    const endTime = value('evt-end-time');

    if (!title) {
      alert('Please enter an event title.');
      return;
    }
    if (!startDate || !startTime || !endDate || !endTime) {
      alert('Please enter the start and end date/time.');
      return;
    }

    const start = new Date(`${startDate}T${startTime}`);
    const end = new Date(`${endDate}T${endTime}`);
    if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) {
      alert('Please check the date and time values.');
      return;
    }
    if (!(start.getTime() < end.getTime())) {
      alert('End date/time must be after start date/time.');
      return;
    }

    const target_person_ids = Array.from(
      document.querySelectorAll('input[name="target_persons"]:checked')
    ).map(cb => cb.value);

    const payload = {
      title,
      category,
      visibility,
      description,
      target_person_ids,
      person_ids: target_person_ids,
      start_date: startDate,
      start_time: startTime,
      end_date: endDate,
      end_time: endTime,
      time_zone: window.FEMC_TIME_ZONE || Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC'
    };

    const createdResponse = await fetchAPI('/api/events/create', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(payload)
    });

    // Resolve the authoritative created record. Support both the historical
    // {calendar: [...]} response and the newer direct-array/events shapes.
    const calendarData = await fetchAPI('/api/events');
    const events = Array.isArray(calendarData)
      ? calendarData
      : (calendarData?.calendar || calendarData?.events || calendarData?.items || []);
    const createdId = createdResponse?.event_id || createdResponse?.id || null;
    const matches = events.filter(e =>
      (createdId && String(e.event_id || e.id || '') === String(createdId)) ||
      (e.title === title && String(e.start_date || e.date || '').slice(0, 10) === startDate)
    );
    const created = matches.length ? matches[matches.length - 1] : null;

    if (!created || !(created.event_id || created.id)) {
      throw new Error('FEMC could not resolve the newly created event from the event store.');
    }

    const event_id = created.event_id || created.id;
    await fetchAPI('/api/events/update', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({event_id, ...payload})
    });

    closeModal();
    await loadView('calendar');
  };
})();
</script>'''
    runtime.HTML_TEMPLATE = html.replace('</body>', script + '\n</body>')


__all__ = ["install"]
