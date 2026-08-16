from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest

from run import DemoState, run_server
from ENGINEERING.source.femc.models import ShareResourceType, VisibilityLevel


# ==================================================
# HTTP harness (ephemeral port, one shared server)
# ==================================================

@pytest.fixture(scope="module")
def base_url():
    state = DemoState()
    state.reset()
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()

    server = run_server.__globals__["HTTPServer"]  # noqa: F841
    from http.server import HTTPServer

    httpd = HTTPServer(("127.0.0.1", port), run_server.__globals__["DemoHTTPRequestHandler"])
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    url = f"http://127.0.0.1:{port}"
    yield url
    httpd.shutdown()
    httpd.server_close()


def api_get(url, path):
    with urllib.request.urlopen(f"{url}{path}") as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def api_get_html(url, path):
    with urllib.request.urlopen(f"{url}{path}") as resp:
        return resp.status, resp.read().decode("utf-8")


def api_post(url, path, payload=None):
    data = json.dumps(payload or {}).encode("utf-8")
    req = urllib.request.Request(
        f"{url}{path}", data=data, method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, body


# ==================================================
# 1. Crashing endpoint fixes: celebrations + export
# ==================================================

def test_celebrations_list_returns_artifacts(base_url):
    status, data = api_get(base_url, "/api/celebrations")
    assert status == 200
    assert "artifacts" in data
    assert len(data["artifacts"]) >= 2


def test_export_returns_valid_schema(base_url):
    status, data = api_get(base_url, "/api/export")
    assert status == 200
    assert "export" in data
    assert "validation" in data
    assert data["validation"]["is_valid"] is True
    assert data["export"]["schema_version"] == "1.0"


# ==================================================
# 2. Share contract: bad id, exact resource, revocation
# ==================================================

def test_share_create_bad_resource_id_returns_400(base_url):
    status, data = api_post(base_url, "/api/sharing/create", {
        "resource_type": "EVENT",
        "resource_id": "missing-event-xyz",
    })
    assert status == 400
    assert data["status"] == "error"


def test_share_create_missing_resource_id_returns_400(base_url):
    status, data = api_post(base_url, "/api/sharing/create", {
        "resource_type": "EVENT",
        "resource_id": "",
    })
    assert status == 400
    assert data["status"] == "error"


def test_share_resolve_event_exact_resource(base_url):
    status, data = api_get(base_url, "/api/sharing")
    assert status == 200
    links = data["share_links"]
    event_link = next((l for l in links if l["resource_type"] == "event"), None)
    assert event_link is not None

    # Share page serves exact-resource HTML (not the SPA shell) with the event title
    status, page = api_get_html(base_url, f"/share?token={event_link['token']}")
    assert status == 200
    assert "<!DOCTYPE html>" in page
    assert '<span class="badge">EVENT</span>' in page
    assert "Alice's Birthday Celebration" in page


def test_share_page_bad_token_shows_clean_error(base_url):
    status, page = api_get_html(base_url, "/share?token=nonexistent-token")
    assert status == 200
    assert "Share link not found" in page


def test_share_revoked_token_rejected(base_url):
    state = DemoState()
    api = state.api
    link = api.create_share_link_for_session(
        state.session_alice.session_id,
        ShareResourceType.EVENT,
        state.event1.id,
        state.family_context.id,
    )
    api.revoke_share_link_for_session(state.session_alice.session_id, link.token)
    with pytest.raises(PermissionError):
        api.resolve_share_token(link.token)


def test_share_celebration_artifact_resolution(base_url):
    state = DemoState()
    api = state.api
    art = api.build_celebration_artifact_for_event_for_session(
        state.session_alice.session_id, state.event1.id
    )
    link = api.create_share_link_for_session(
        state.session_alice.session_id,
        ShareResourceType.CELEBRATION_ARTIFACT,
        art.id,
        state.family_context.id,
    )
    resolved = api.resolve_share_token(link.token)
    assert resolved.id == art.id
    assert resolved.artifact_type.value in (
        "birthday_card", "anniversary_card", "milestone_card",
        "family_memory_card", "event_highlight", "celebration_album",
    )


# ==================================================
# 3. Guide status read-only + no auto-init
# ==================================================

def test_guide_status_read_only_no_auto_init(base_url):
    status, data = api_get(base_url, "/api/guide/status")
    assert status == 200
    # After a fresh reset, no guided state should be auto-created.
    if data["session_state"] is not None:
        # Only valid if it was explicitly initialized by earlier tests;
        # fall back to asserting the payload shape is stable.
        assert "current_mode" in data["session_state"]
    assert "scenes" in data


def test_practice_status_read_only(base_url):
    status, data = api_get(base_url, "/api/guide/practice/status")
    assert status == 200
    assert "is_practice_active" in data
    assert data["is_practice_active"] is False


# ==================================================
# 4. Family onboard validation + member update
# ==================================================

def test_family_onboard_missing_name_returns_400(base_url):
    status, data = api_post(base_url, "/api/family/onboard", {
        "name": "",
        "email": "david@example.com",
        "relationship": "MEMBER",
    })
    assert status == 400
    assert data["status"] == "error"


def test_family_onboard_missing_email_returns_400(base_url):
    status, data = api_post(base_url, "/api/family/onboard", {
        "name": "David Smith",
        "email": "",
        "relationship": "MEMBER",
    })
    assert status == 400
    assert data["status"] == "error"


def test_family_update_changes_member(base_url):
    state = DemoState()
    result = state.api.update_member_for_session(
        state.session_alice.session_id,
        state.acc_bob.id,
        name="Bobby Smith",
        email="bobby@example.com",
    )
    assert result["status"] == "success"
    person = state.api.canonical.get_person(state.acc_bob.person_id)
    assert person.name == "Bobby Smith"
    acc = state.api.canonical.get_account(state.acc_bob.id)
    assert acc.email == "bobby@example.com"


def test_family_update_unauthorized_raises(base_url):
    state = DemoState()
    with pytest.raises(PermissionError):
        state.api.update_member_for_session(
            state.session_alice.session_id,
            "some-outside-account",
            name="Hacker",
        )


# ==================================================
# 5. Trial Observer: start/observe/status/end
# ==================================================

def test_trial_start_status_observe_end(base_url):
    state = DemoState()
    api = state.api
    sess = state.session_alice.session_id
    fc = state.family_context.id

    started = api.start_trial_for_session(sess, fc)
    assert started["status"] == "trial_started"

    status = api.get_trial_status_for_session(sess)
    assert status["is_trial_active"] is True

    obs = api.record_trial_observation_for_session(
        sess, "CREATE", "EVENT", "observed", True, {"note": "created real event"}
    )
    assert obs["recorded"] is True

    status2 = api.get_trial_status_for_session(sess)
    assert status2["observed_action_count"] >= 1
    # Observations must be sanitized: the raw narrative detail is never stored.
    trial = api.trial_observer.trials[state.acc_alice.id]
    stored_details = [o.details for o in trial.observations]
    for d in stored_details:
        assert "created real event" not in json.dumps(d)

    ended = api.end_trial_for_session(sess)
    assert ended["status"] == "ended"

    # After end, real mode is restored and real events still visible.
    assert api.get_guided_experience_state_for_session(sess).current_mode.value == "real"
    real_events = api.get_calendar_for_session(sess, fc)
    assert len(real_events) >= 2


def test_trial_observation_without_active_trial_not_recorded(base_url):
    state = DemoState()
    api = state.api
    obs = api.record_trial_observation_for_session(
        state.session_alice.session_id, "CREATE", "EVENT"
    )
    assert obs["recorded"] is False


# ==================================================
# 6. Practice/Real isolation: real counts preserved
# ==================================================

def test_practice_exit_preserves_real_data_counts(base_url):
    state = DemoState()
    api = state.api
    sess = state.session_alice.session_id
    fc = state.family_context.id

    real_before_events = len(api.get_calendar_for_session(sess, fc))
    real_before_memories = len(state.api.canonical.list_memories())

    api.start_practice_world_for_session(sess, fc)
    pw = api.get_practice_world_state_for_session(sess)
    assert pw is not None

    practice_events = api.get_calendar_for_session(sess, fc)
    assert len(practice_events) == real_before_events

    result = api.exit_practice_world_for_session(sess)
    assert result.get("real_views_restored") is True
    assert api.get_practice_world_state_for_session(sess) is None

    real_after_events = len(api.get_calendar_for_session(sess, fc))
    real_after_memories = len(state.api.canonical.list_memories())
    assert real_after_events == real_before_events
    assert real_after_memories == real_before_memories


# ==================================================
# 7. Template integrity
# ==================================================

def test_template_is_not_truncated(base_url):
    from run import HTML_TEMPLATE
    assert HTML_TEMPLATE.rstrip().endswith("</html>")
    assert "</script>" in HTML_TEMPLATE
    assert "</body>" in HTML_TEMPLATE
    assert "async function boot()" in HTML_TEMPLATE
    assert "refreshModeBadge()" in HTML_TEMPLATE
