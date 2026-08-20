from __future__ import annotations


def install(runtime):
    html = runtime.HTML_TEMPLATE
    marker = "FEMC_PRACTICE_EVENT_CREATE_SYNC_PATCH"
    if marker in html:
        return

    script = r'''<script id="FEMC_PRACTICE_EVENT_CREATE_SYNC_PATCH">
(() => {
  window.submitCreateEvent = async function (evt) {
    evt.preventDefault();
    const title = document.getElementById('evt-title').value.trim();
    const category = document.getElementById('evt-cat').value;
    const visibility = document.getElementById('evt-vis').value;
    const description = document.getElementById('evt-desc').value.trim();
    const startDate = document.getElementById('evt-start-date').value;
    const startTime = document.getElementById('evt-start-time').value;
    const endDate = document.getElementById('evt-end-date').value;
    const endTime = document.getElementById('evt-end-time').value;

    if (!startDate || !startTime || !endDate || !endTime) {
      alert('Please enter the start and end date/time.');
      return;
    }
    const start = new Date(`${startDate}T${startTime}`);
    const end = new Date(`${endDate}T${endTime}`);
    if (!(start.getTime() < end.getTime())) {
      alert('End date/time must be after start date/time.');
      return;
    }

    const target_person_ids = Array.from(document.querySelectorAll('input[name="target_persons"]:checked')).map(cb => cb.value);
    const payload = {
      title,
      category,
      visibility,
      description,
      target_person_ids,
      start_date: startDate,
      start_time: startTime,
      end_date: endDate,
      end_time: endTime
    };

    await fetchAPI('/api/events/create', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(payload)
    });

    // The legacy create endpoint predates the richer Practice date/time fields.
    // Resolve the newly created event and immediately persist the exact user input
    // through the Practice edit path before re-rendering Calendar.
    const calendarData = await fetchAPI('/api/events');
    const matches = (calendarData.calendar || []).filter(e => e.title === title);
    const created = matches.length ? matches[matches.length - 1] : null;
    if (created && created.event_id) {
      await fetchAPI('/api/events/update', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({event_id: created.event_id, ...payload})
      });
    }

    closeModal();
    await loadView('calendar');
  };
})();
</script>'''
    runtime.HTML_TEMPLATE = html.replace('</body>', script + '\n</body>')


__all__ = ["install"]
