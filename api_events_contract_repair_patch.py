from __future__ import annotations

from urllib.parse import urlparse, urlunparse


def _is_practice(runtime):
    try:
        api = runtime.demo_state.api
        session_id = runtime.demo_state.session_id
        state = api.get_guided_experience_state_for_session(session_id)
        return bool(state and getattr(getattr(state, 'current_mode', None), 'value', '') == 'learn_by_doing')
    except Exception:
        return False


def install(runtime):
    """Repair the frontend/backend event creation contract for the demo host.

    The event intelligence flow falls back to POST /api/events, while the
    practice event store repair owns POST /api/events/create.  Bridge those
    equivalent creation contracts so the host running through run.py persists
    the event instead of returning 404.
    """
    if getattr(runtime, '_FEMC_API_EVENTS_CONTRACT_REPAIR_V1', False):
        return
    runtime._FEMC_API_EVENTS_CONTRACT_REPAIR_V1 = True

    previous_post = runtime.DemoHTTPRequestHandler.do_POST

    def patched_post(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/events' and _is_practice(runtime):
            # Reuse the authoritative practice event-store creation path rather
            # than duplicating persistence logic.  Preserve query parameters.
            rewritten = parsed._replace(path='/api/events/create')
            original_path = self.path
            self.path = urlunparse(rewritten)
            try:
                return previous_post(self)
            finally:
                self.path = original_path
        return previous_post(self)

    runtime.DemoHTTPRequestHandler.do_POST = patched_post


__all__ = ['install']
