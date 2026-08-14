import pytest
import datetime
from ENGINEERING.source.femc.api import FEMCApi
from ENGINEERING.source.femc.models import (
    ActionType,
    ResourceType,
    VisibilityLevel,
    ContextType,
    AgeGroup,
    Language,
    GuideMode,
)
from run import DemoState


def test_1_two_modes_exist():
    assert GuideMode.LEARN_BY_DOING.value == "learn_by_doing"
    assert GuideMode.WATCH_JOURNEY.value == "watch_journey"


def test_2_learn_by_doing_mode_starts():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    st = api.initialize_guided_experience_for_session(
        session_id=sess_id,
        family_context_id=fc_id,
        mode=GuideMode.LEARN_BY_DOING,
    )
    assert st.current_mode == GuideMode.LEARN_BY_DOING
    assert st.current_scene_index == 0


def test_3_watch_mode_starts():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    st = api.initialize_guided_experience_for_session(
        session_id=sess_id,
        family_context_id=fc_id,
        mode=GuideMode.WATCH_JOURNEY,
    )
    assert st.current_mode == GuideMode.WATCH_JOURNEY


def test_4_journey_scenes_share_common_definitions():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    api.initialize_guided_experience_for_session(sess_id, fc_id, mode=GuideMode.LEARN_BY_DOING)
    scenes_learn = api.get_shared_journey_scenes_for_session(sess_id)

    api.switch_guided_experience_mode_for_session(sess_id, GuideMode.WATCH_JOURNEY)
    scenes_watch = api.get_shared_journey_scenes_for_session(sess_id)

    assert len(scenes_learn) == 11
    assert len(scenes_watch) == 11
    assert scenes_learn[0].scene_id == scenes_watch[0].scene_id


def test_5_context_selection_works():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    for ctx in [ContextType.FAMILY, ContextType.FRIENDS, ContextType.COMMUNITY]:
        st = api.initialize_guided_experience_for_session(sess_id, fc_id, context_type=ctx)
        assert st.context_type == ctx


def test_6_age_group_selection_works():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    for age in [AgeGroup.TEENS, AgeGroup.YOUNG_ADULTS, AgeGroup.SENIORS]:
        st = api.initialize_guided_experience_for_session(sess_id, fc_id, age_group=age)
        assert st.age_group == age


def test_7_family_inclusion_works():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    st1 = api.initialize_guided_experience_for_session(sess_id, fc_id, include_family=True)
    assert st1.include_family is True

    st2 = api.initialize_guided_experience_for_session(sess_id, fc_id, include_family=False)
    assert st2.include_family is False


def test_8_target_highlighting_exists():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    api.initialize_guided_experience_for_session(sess_id, fc_id)
    scenes = api.get_shared_journey_scenes_for_session(sess_id)
    assert scenes[0].target_control == "nav-home"
    assert scenes[0].animation_type == "glow_pulse"


def test_9_wrong_action_guidance_exists():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    api.initialize_guided_experience_for_session(sess_id, fc_id)
    # Perform wrong action on scene 0
    res = api.validate_guided_action_for_session(
        sess_id,
        action_type=ActionType.DELETE,
        control_id="wrong-btn",
    )
    assert res["status"] == "wrong_action"
    assert "That's okay 😊" in res["message"]


def test_10_correct_action_detection_exists():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    api.initialize_guided_experience_for_session(sess_id, fc_id)
    res = api.validate_guided_action_for_session(
        sess_id,
        action_type=ActionType.PERSPECTIVE_SWITCH,
        control_id="nav-home",
    )
    assert res["status"] == "success"
    assert res["session_state"]["current_scene_index"] == 1


def test_11_real_operation_executes():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    # Create real event
    ev = api.create_event_for_session(
        session_id=sess_id,
        title="Guided Interactive Event",
        description="Real event created during learn-by-doing exercise",
        family_context_id=fc_id,
        start_time=datetime.datetime.utcnow() + datetime.timedelta(days=1),
        end_time=datetime.datetime.utcnow() + datetime.timedelta(days=1, hours=2),
    )
    assert ev.id is not None
    assert ev.title == "Guided Interactive Event"


def test_12_result_appears():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    ev = api.create_event_for_session(
        session_id=sess_id,
        title="Result Reveal Event",
        description="Event to verify visual result projection",
        family_context_id=fc_id,
        start_time=datetime.datetime.utcnow() + datetime.timedelta(days=1),
        end_time=datetime.datetime.utcnow() + datetime.timedelta(days=1, hours=2),
    )
    calendar = api.get_calendar_for_session(sess_id, fc_id)
    assert any(e.event_id == ev.id for e in calendar)


def test_13_transaction_is_recorded():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    api.initialize_guided_experience_for_session(sess_id, fc_id)
    res = api.validate_guided_action_for_session(
        sess_id,
        action_type=ActionType.PERSPECTIVE_SWITCH,
        control_id="nav-home",
        resource_id="home-view",
        resource_label="Home Dashboard",
        operation="Opened Home Dashboard in Learn By Doing Mode",
    )
    assert res["transaction_recorded"] is not None


def test_14_mayil_can_explain_transaction():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    api.record_transaction_for_session(
        session_id=sess_id,
        family_context_id=fc_id,
        action_type=ActionType.CREATE,
        resource_type=ResourceType.EVENT,
        resource_id=state.event1.id,
        resource_label_snapshot="Alice Birthday",
        operation="Scheduled event",
    )
    explanation = api.explain_resource_history_for_session(sess_id, fc_id, ResourceType.EVENT, state.event1.id)
    assert len(explanation["recorded_facts"]) >= 1


def test_15_watch_to_try_it_yourself_works():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    api.initialize_guided_experience_for_session(sess_id, fc_id, mode=GuideMode.WATCH_JOURNEY)
    assert api.get_guided_experience_state_for_session(sess_id).current_mode == GuideMode.WATCH_JOURNEY

    # Switch to Try It Yourself
    st = api.switch_guided_experience_mode_for_session(sess_id, GuideMode.LEARN_BY_DOING)
    assert st.current_mode == GuideMode.LEARN_BY_DOING


def test_16_reset_restores_demo_world():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    api.initialize_guided_experience_for_session(sess_id, fc_id)
    api.validate_guided_action_for_session(sess_id, action_type=ActionType.PERSPECTIVE_SWITCH, control_id="nav-home")

    res_st = api.reset_guided_experience_for_session(sess_id)
    assert res_st.current_scene_index == 0
    assert len(res_st.completed_scene_ids) == 0


def test_17_english_works():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    api.initialize_guided_experience_for_session(sess_id, fc_id, language=Language.ENGLISH)
    scenes = api.get_shared_journey_scenes_for_session(sess_id)
    assert scenes[0].title["en"] == "Welcome to FEMC"


def test_18_tamil_works():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    api.initialize_guided_experience_for_session(sess_id, fc_id, language=Language.TAMIL)
    scenes = api.get_shared_journey_scenes_for_session(sess_id)
    assert scenes[0].title["ta"] == "FEMC-க்கு நல்வரவு"


def test_19_hindi_works():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    api.initialize_guided_experience_for_session(sess_id, fc_id, language=Language.HINDI)
    scenes = api.get_shared_journey_scenes_for_session(sess_id)
    assert scenes[0].title["hi"] == "FEMC में आपका स्वागत है"


def test_20_existing_femc_capabilities_remain_functional():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    topology = api.get_family_topology_for_session(sess_id, fc_id)
    assert len(topology.members) >= 3

    dashboard = api.get_dashboard_summary_for_session(sess_id, fc_id)
    assert dashboard is not None
