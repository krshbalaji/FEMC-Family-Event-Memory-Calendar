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


def _is_practice(api, session_id):
    try:
        state = api.get_guided_experience_state_for_session(session_id)
        return bool(state and getattr(getattr(state, 'current_mode', None), 'value', '') == 'learn_by_doing')
    except Exception:
        return False


def _date(value):
    try:
        return datetime.date.fromisoformat(str(value)[:10])
    except Exception:
        return None


def install(runtime):
    if getattr(runtime, '_FEMC_PRACTICE_EVENT_STORE_REPAIR_V1', False):
        return
    runtime._FEMC_PRACTICE_EVENT_STORE_REPAIR_V1 = True

    original_get = runtime.DemoHTTPRequestHandler.do_GET
    original_post = runtime.DemoHTTPRequestHandler.do_POST

    def patched_get(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/events':
            api = runtime.demo_state.api
            session_id = runtime.demo_state.session_id
            if _is_practice(api, session_id):
                pw = api.get_practice_world_state_for_session(session_id)
                calendar = []
                for event in (getattr(pw, 'simulated_events', None) or []):
                    item = dict(event)
                    event_id = str(item.get('id') or item.get('event_id') or '')
                    if event_id:
                        item['id'] = event_id
                        item['event_id'] = event_id
                    item['date'] = str(item.get('start_date') or item.get('date') or '')[:10]
                    calendar.append(item)
                self._send_json({'calendar': calendar, 'events': calendar, 'items': calendar})
                return
        return original_get(self)

    def patched_post(self):
        parsed = urlparse(self.path)
        path = parsed.path
        api = runtime.demo_state.api
        session_id = runtime.demo_state.session_id

        if path in ('/api/events/create', '/api/events/update') and _is_practice(api, session_id):
            payload = _read_json(self)
            pw = api.get_practice_world_state_for_session(session_id)
            events = getattr(pw, 'simulated_events', None)
            if events is None:
                events = []
                setattr(pw, 'simulated_events', events)

            if path == '/api/events/create':
                title = str(payload.get('title') or '').strip()
                start_date = str(payload.get('start_date') or payload.get('date') or '').strip()[:10]
                if not title or _date(start_date) is None:
                    self._send_json({'status': 'error', 'message': 'Event title and a valid start date are required.'}, status=400)
                    return
                next_id = f"sim_event_user_{len(events) + 1}"
                existing_ids = {str(e.get('id') or e.get('event_id') or '') for e in events}
                while next_id in existing_ids:
                    next_id = f"sim_event_user_{len(events) + 1}_{len(existing_ids)}"
                event = {
                    'id': next_id,
                    'event_id': next_id,
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

            event_id = str(payload.get('event_id') or payload.get('id') or '')
            event = next((e for e in events if str(e.get('id') or e.get('event_id') or '') == event_id), None)
            if event is None:
                self._send_json({'status': 'error', 'message': 'Practice event not found.'}, status=404)
                return
            for key in ('title', 'description', 'category', 'visibility', 'start_date', 'start_time', 'end_date', 'end_time', 'target_person_ids', 'person_ids', 'time_zone'):
                if key in payload and payload[key] is not None:
                    event[key] = payload[key]
            if event.get('start_date'):
                event['date'] = str(event['start_date'])[:10]
            event['id'] = event_id
            event['event_id'] = event_id
            self._send_json({'status': 'success', 'event': event})
            return

        return original_post(self)

    runtime.DemoHTTPRequestHandler.do_GET = patched_get
    runtime.DemoHTTPRequestHandler.do_POST = patched_post

    html = runtime.HTML_TEMPLATE
    marker = 'FEMC_PRACTICE_NAV_PERFORMANCE_REPAIR_V1'
    if marker not in html:
        script = r'''<script id="FEMC_PRACTICE_NAV_PERFORMANCE_REPAIR_V1">
(() => {
  let pendingView = null;
  let navigationBusy = false;
  function install() {
    if (window.loadView && !window.loadView.__femcFastNavV1) {
      const original = window.loadView;
      const fast = async function(view) {
        if (navigationBusy && pendingView === view) return;
        pendingView = view;
        navigationBusy = true;
        try { return await original.apply(this, arguments); }
        finally { pendingView = null; navigationBusy = false; }
      };
      fast.__femcFastNavV1 = true;
      window.loadView = fast;
    }
  }
  install();
  document.addEventListener('DOMContentLoaded', install, {once:true});
  setTimeout(install, 0);
})();
</script>'''
        runtime.HTML_TEMPLATE = html.replace('</body>', script + '\n</body>')


__all__ = ['install']
