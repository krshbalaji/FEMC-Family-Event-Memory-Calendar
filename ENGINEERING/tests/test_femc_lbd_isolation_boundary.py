import pytest
import datetime
import io
import json
import run
from run import DemoState, DemoHTTPRequestHandler, to_dict
from ENGINEERING.source.femc.models import (
    GuideMode,
    ResourceType,
    ActionType,
    ShareResourceType,
    VisibilityLevel,
)

class TestHandler(DemoHTTPRequestHandler):
    __test__ = False

    def __init__(self, path, method="GET", body=None):
        self.request_version = "HTTP/1.1"
        self.command = method
        self.path = path
        self.headers = {}
        if body is not None:
            body_str = json.dumps(body)
            self.headers["Content-Length"] = str(len(body_str))
            self.rfile = io.BytesIO(body_str.encode('utf-8'))
        else:
            self.rfile = io.BytesIO(b"")
        self.wfile = io.BytesIO()
        self.send_response_called = False
        self.response_status = None
        self.response_headers = {}

    def send_response(self, code, message=None):
        self.send_response_called = True
        self.response_status = code

    def send_header(self, keyword, value):
        self.response_headers[keyword] = value

    def end_headers(self):
        pass

    def log_message(self, format, *args):
        pass

    def handle_request(self):
        if self.command == "GET":
            self.do_GET()
        elif self.command == "POST":
            self.do_POST()

    def get_json_response(self):
        try:
            return json.loads(self.wfile.getvalue().decode('utf-8'))
        except Exception:
            return {}

@pytest.fixture(autouse=True)
def setup_teardown_state():
    old_state = run.demo_state
    yield
    run.demo_state = old_state

def test_a_event_isolation():
    state = DemoState()
    run.demo_state = state
    api = state.api
    sess_id = state.session_alice.session_id
    state.session_id = sess_id
    fc_id = state.family_context.id

    real_count_before = len(api.canonical.list_events())

    api.initialize_guided_experience_for_session(sess_id, fc_id, mode=GuideMode.LEARN_BY_DOING)

    pw = api.start_practice_world_for_session(sess_id, fc_id)
    assert pw is not None
    initial_sim_count = len(pw.simulated_events)

    # Post event creation
    handler = TestHandler("/api/events/create", method="POST", body={
        "title": "Practice Birthday Party",
        "description": "LBD Event",
        "category": "birthday",
        "visibility": "family",
    })
    handler.handle_request()
    res = handler.get_json_response()
    assert res.get("status") == "success"

    # Verify counts
    real_count_after = len(api.canonical.list_events())
    assert real_count_after == real_count_before

    pw = api.get_practice_world_state_for_session(sess_id)
    assert len(pw.simulated_events) == initial_sim_count + 1
    assert pw.simulated_events[-1]["title"] == "Practice Birthday Party"

    # Visible in GET /api/events
    get_handler = TestHandler("/api/events", method="GET")
    get_handler.handle_request()
    get_res = get_handler.get_json_response()
    assert len(get_res.get("calendar", [])) == initial_sim_count + 1
    assert get_res["calendar"][-1]["title"] == "Practice Birthday Party"


def test_b_memory_isolation():
    state = DemoState()
    run.demo_state = state
    api = state.api
    sess_id = state.session_alice.session_id
    state.session_id = sess_id
    fc_id = state.family_context.id

    real_count_before = len(api.canonical.list_memories())
    api.initialize_guided_experience_for_session(sess_id, fc_id, mode=GuideMode.LEARN_BY_DOING)

    pw = api.start_practice_world_for_session(sess_id, fc_id)
    initial_sim_count = len(pw.simulated_memories)

    # Post memory creation
    handler = TestHandler("/api/memories/create", method="POST", body={
        "narrative": "A nice practice memory",
        "event_id": "sim_ev1",
        "visibility": "family",
    })
    handler.handle_request()
    res = handler.get_json_response()
    assert res.get("status") == "success"

    real_count_after = len(api.canonical.list_memories())
    assert real_count_after == real_count_before

    pw = api.get_practice_world_state_for_session(sess_id)
    assert len(pw.simulated_memories) == initial_sim_count + 1
    assert pw.simulated_memories[-1]["summary"] == "A nice practice memory"

    # Visible in GET /api/timeline
    get_handler = TestHandler("/api/timeline", method="GET")
    get_handler.handle_request()
    get_res = get_handler.get_json_response()
    assert len(get_res.get("timeline", [])) == initial_sim_count + 1


def test_c_person_isolation():
    state = DemoState()
    run.demo_state = state
    api = state.api
    sess_id = state.session_alice.session_id
    state.session_id = sess_id
    fc_id = state.family_context.id

    real_count_before = len(api.canonical.list_persons())
    api.initialize_guided_experience_for_session(sess_id, fc_id, mode=GuideMode.LEARN_BY_DOING)

    pw = api.start_practice_world_for_session(sess_id, fc_id)
    initial_sim_count = len(pw.simulated_persons)

    # Post person check
    handler = TestHandler("/api/family/onboard", method="POST", body={
        "name": "Simulated Cousin",
        "email": "cousin@example.com",
        "relationship": "COUSIN",
    })
    handler.handle_request()
    res = handler.get_json_response()
    assert res.get("status") == "success"

    real_count_after = len(api.canonical.list_persons())
    assert real_count_after == real_count_before

    pw = api.get_practice_world_state_for_session(sess_id)
    assert len(pw.simulated_persons) == initial_sim_count + 1
    assert pw.simulated_persons[-1]["name"] == "Simulated Cousin"

    # Visible in GET /api/members
    get_handler = TestHandler("/api/members", method="GET")
    get_handler.handle_request()
    get_res = get_handler.get_json_response()
    simulated_members = [m for m in get_res.get("members", []) if m["account_id"].startswith("sim_res_")]
    assert len(simulated_members) == 1
    assert simulated_members[0]["name"] == "Simulated Cousin"


def test_d_media_isolation():
    state = DemoState()
    run.demo_state = state
    api = state.api
    sess_id = state.session_alice.session_id
    state.session_id = sess_id
    fc_id = state.family_context.id

    real_count_before = len(api.canonical.list_media_items())
    api.initialize_guided_experience_for_session(sess_id, fc_id, mode=GuideMode.LEARN_BY_DOING)

    pw = api.start_practice_world_for_session(sess_id, fc_id)
    initial_sim_count = len(pw.simulated_media_items)

    # Post media creation
    handler = TestHandler("/api/media/create", method="POST", body={
        "uri": "https://example.com/item.jpg",
        "caption": "Simulated Photo",
        "media_type": "photo",
        "memory_id": "sim_mem1",
        "event_id": "sim_ev1",
        "visibility": "family",
    })
    handler.handle_request()
    res = handler.get_json_response()
    assert res.get("status") == "success"

    real_count_after = len(api.canonical.list_media_items())
    assert real_count_after == real_count_before

    pw = api.get_practice_world_state_for_session(sess_id)
    assert len(pw.simulated_media_items) == initial_sim_count + 1
    assert pw.simulated_media_items[-1]["caption"] == "Simulated Photo"

    # Visible in GET /api/media
    get_handler = TestHandler("/api/media", method="GET")
    get_handler.handle_request()
    get_res = get_handler.get_json_response()
    assert len(get_res.get("items", [])) == initial_sim_count + 1


def test_e_celebration_isolation():
    state = DemoState()
    run.demo_state = state
    api = state.api
    sess_id = state.session_alice.session_id
    state.session_id = sess_id
    fc_id = state.family_context.id

    real_count_before = len(api.derived.get_celebration_artifacts(fc_id))
    api.initialize_guided_experience_for_session(sess_id, fc_id, mode=GuideMode.LEARN_BY_DOING)

    pw = api.start_practice_world_for_session(sess_id, fc_id)
    initial_sim_count = len(pw.simulated_celebrations)

    # Post celebration generation
    handler = TestHandler("/api/celebrations/generate", method="POST", body={
        "target_type": "event",
        "target_id": "sim_ev1",
    })
    handler.handle_request()
    res = handler.get_json_response()
    assert res.get("status") == "success"

    real_count_after = len(api.derived.get_celebration_artifacts(fc_id))
    assert real_count_after == real_count_before

    pw = api.get_practice_world_state_for_session(sess_id)
    assert len(pw.simulated_celebrations) == initial_sim_count + 1

    # Visible in GET /api/celebrations
    get_handler = TestHandler("/api/celebrations", method="GET")
    get_handler.handle_request()
    get_res = get_handler.get_json_response()
    assert len(get_res.get("artifacts", [])) == initial_sim_count + 1


def test_f_share_isolation():
    state = DemoState()
    run.demo_state = state
    api = state.api
    sess_id = state.session_alice.session_id
    state.session_id = sess_id
    fc_id = state.family_context.id

    real_count_before = len(api.canonical.list_share_links())
    api.initialize_guided_experience_for_session(sess_id, fc_id, mode=GuideMode.LEARN_BY_DOING)

    pw = api.start_practice_world_for_session(sess_id, fc_id)
    initial_sim_count = len(pw.simulated_share_links)

    # Post sharing create
    handler = TestHandler("/api/sharing/create", method="POST", body={
        "resource_type": "event",
        "resource_id": "sim_ev1",
    })
    handler.handle_request()
    res = handler.get_json_response()
    assert res.get("status") == "success"

    real_count_after = len(api.canonical.list_share_links())
    assert real_count_after == real_count_before

    pw = api.get_practice_world_state_for_session(sess_id)
    assert len(pw.simulated_share_links) == initial_sim_count + 1

    # Visible in GET /api/sharing
    get_handler = TestHandler("/api/sharing", method="GET")
    get_handler.handle_request()
    get_res = get_handler.get_json_response()
    assert len(get_res.get("share_links", [])) == initial_sim_count + 1


def test_g_revoke_isolation():
    state = DemoState()
    run.demo_state = state
    api = state.api
    sess_id = state.session_alice.session_id
    state.session_id = sess_id
    fc_id = state.family_context.id

    api.initialize_guided_experience_for_session(sess_id, fc_id, mode=GuideMode.LEARN_BY_DOING)

    pw = api.start_practice_world_for_session(sess_id, fc_id)
    initial_count = len(pw.simulated_share_links)

    # Initialize a practice link
    post_hand = TestHandler("/api/sharing/create", method="POST", body={
        "resource_type": "event",
        "resource_id": "sim_ev1",
    })
    post_hand.handle_request()
    token = post_hand.get_json_response()["share_link"]["token"]

    pw = api.get_practice_world_state_for_session(sess_id)
    assert len(pw.simulated_share_links) == initial_count + 1

    # Revoke
    revoke_hand = TestHandler("/api/sharing/revoke", method="POST", body={
        "token": token,
    })
    revoke_hand.handle_request()

    # Practice link should be removed, count back to initial
    pw = api.get_practice_world_state_for_session(sess_id)
    assert len(pw.simulated_share_links) == initial_count


def test_h_history_isolation():
    state = DemoState()
    run.demo_state = state
    api = state.api
    sess_id = state.session_alice.session_id
    state.session_id = sess_id
    fc_id = state.family_context.id

    real_tx_count_before = len(state.api.transaction_memory.repository.list_transactions(fc_id))

    api.initialize_guided_experience_for_session(sess_id, fc_id, mode=GuideMode.LEARN_BY_DOING)

    pw = api.start_practice_world_for_session(sess_id, fc_id)
    initial_sim_count = len(pw.simulated_transactions)

    # Post event
    handler = TestHandler("/api/events/create", method="POST", body={
        "title": "Practice Event to Track",
    })
    handler.handle_request()

    real_tx_count_after = len(state.api.transaction_memory.repository.list_transactions(fc_id))
    assert real_tx_count_after == real_tx_count_before

    # Visible in GET /api/history
    get_handler = TestHandler("/api/history", method="GET")
    get_handler.handle_request()
    get_res = get_handler.get_json_response()
    assert len(get_res.get("transactions", [])) == initial_sim_count + 1
    assert "Practice Event to Track" in get_res["transactions"][-1]["resource_label"]


def test_i_reset():
    state = DemoState()
    run.demo_state = state
    api = state.api
    sess_id = state.session_alice.session_id
    state.session_id = sess_id
    fc_id = state.family_context.id

    r_ev_before = len(api.canonical.list_events())

    api.initialize_guided_experience_for_session(sess_id, fc_id, mode=GuideMode.LEARN_BY_DOING)

    # Do a LBD mutation
    handler = TestHandler("/api/events/create", method="POST", body={
        "title": "Temp event",
    })
    handler.handle_request()

    # Reset
    reset_hand = TestHandler("/api/guide/reset", method="POST")
    reset_hand.handle_request()

    # Deactive LBD
    api.switch_guided_experience_mode_for_session(sess_id, GuideMode.WATCH_JOURNEY)

    r_ev_after = len(api.canonical.list_events())
    assert r_ev_before == r_ev_after


def test_j_real_femc_regression():
    state = DemoState()
    run.demo_state = state
    api = state.api
    sess_id = state.session_alice.session_id
    state.session_id = sess_id
    fc_id = state.family_context.id

    real_count_before = len(api.canonical.list_events())

    # Regular post
    handler = TestHandler("/api/events/create", method="POST", body={
        "title": "Real Event Persistent",
    })
    handler.handle_request()

    real_count_after = len(api.canonical.list_events())
    assert real_count_after == real_count_before + 1


def test_k_watch_regression():
    state = DemoState()
    run.demo_state = state
    api = state.api
    sess_id = state.session_alice.session_id
    state.session_id = sess_id
    fc_id = state.family_context.id

    api.initialize_guided_experience_for_session(sess_id, fc_id, mode=GuideMode.WATCH_JOURNEY)

    pw = api.get_practice_world_state_for_session(sess_id)
    if pw:
        assert len(pw.simulated_events) == 0


def test_l_session_isolation():
    state = DemoState()
    run.demo_state = state
    api = state.api
    fc_id = state.family_context.id
    alice_sess = state.session_alice.session_id
    bob_sess = state.session_bob.session_id

    # Alice LBD
    api.initialize_guided_experience_for_session(alice_sess, fc_id, mode=GuideMode.LEARN_BY_DOING)
    # Bob LBD
    api.initialize_guided_experience_for_session(bob_sess, fc_id, mode=GuideMode.LEARN_BY_DOING)

    alice_pw = api.start_practice_world_for_session(alice_sess, fc_id)
    bob_pw = api.start_practice_world_for_session(bob_sess, fc_id)

    alice_initial = len(alice_pw.simulated_events)
    bob_initial = len(bob_pw.simulated_events)

    # Alice posts event
    alice_hand = TestHandler("/api/events/create", method="POST", body={
        "title": "Alice's Event",
    })
    # Switch session context to Alice's session
    run.demo_state.session_id = alice_sess
    alice_hand.handle_request()

    # Bob posts event
    bob_hand = TestHandler("/api/events/create", method="POST", body={
        "title": "Bob's Event",
    })
    run.demo_state.session_id = bob_sess
    bob_hand.handle_request()

    # Verify Alice's PW has only Alice's event added
    alice_pw = api.get_practice_world_state_for_session(alice_sess)
    assert len(alice_pw.simulated_events) == alice_initial + 1
    assert alice_pw.simulated_events[-1]["title"] == "Alice's Event"

    # Verify Bob's PW has only Bob's event added
    bob_pw = api.get_practice_world_state_for_session(bob_sess)
    assert len(bob_pw.simulated_events) == bob_initial + 1
    assert bob_pw.simulated_events[-1]["title"] == "Bob's Event"


def test_m_early_exit():
    state = DemoState()
    run.demo_state = state
    api = state.api
    sess_id = state.session_alice.session_id

    # Guided Experience has NOT initialized any practice_worlds, let's call reset or exit
    # This shouldn't throw AttributeError
    api.guided_experience.reset_guided_session(state.acc_alice.id)
    # Verify it completes without crashing
