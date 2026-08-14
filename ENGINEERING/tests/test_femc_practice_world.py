"""
Test Suite for FEMC V2.3-D.1 Mayil Practice World / Safe Simulation Experience
Covers all 22 required test cases specified in Section 20 of the directive.
"""

import datetime
import pytest
from ENGINEERING.source.femc.api import FEMCApi
from ENGINEERING.source.femc.models import (
    ActionType,
    AgeGroup,
    ContextType,
    GuideMode,
    Language,
    MayilPracticeWorld,
    ResourceType,
)


from run import DemoState


def test_1_practice_world_initializes():
    state = DemoState()
    pw = state.api.start_practice_world_for_session(
        state.session_alice.session_id, state.family_context.id
    )
    assert pw is not None
    assert pw.is_active is True
    assert pw.account_id == state.acc_alice.id
    assert len(pw.simulated_persons) >= 3


def test_2_practice_world_isolated_from_real_state():
    state = DemoState()
    real_events_before = len(state.api.canonical.list_events())
    real_memories_before = len(state.api.canonical.list_memories())
    real_tx_before = len(state.api.transaction_memory.repository.records)

    state.api.start_practice_world_for_session(state.session_alice.session_id, state.family_context.id)
    state.api.execute_simulated_action_for_session(
        state.session_alice.session_id,
        ActionType.PERSPECTIVE_SWITCH,
        "nav-home",
        ResourceType.EVENT,
        {"title": "Simulated Birthday Party"},
    )

    real_events_after = len(state.api.canonical.list_events())
    real_memories_after = len(state.api.canonical.list_memories())
    real_tx_after = len(state.api.transaction_memory.repository.records)

    # ABSOLUTE ISOLATION REQUIREMENT: Zero real state mutation
    assert real_events_before == real_events_after
    assert real_memories_before == real_memories_after
    assert real_tx_before == real_tx_after


def test_3_simulated_navigation_works():
    state = DemoState()
    state.api.start_practice_world_for_session(state.session_alice.session_id, state.family_context.id)
    res = state.api.execute_simulated_action_for_session(
        state.session_alice.session_id,
        ActionType.PERSPECTIVE_SWITCH,
        "nav-home",
    )
    assert res["status"] == "success"
    assert "current_scene" in res


def test_4_simulated_event_creation_works():
    state = DemoState()
    state.api.start_practice_world_for_session(state.session_alice.session_id, state.family_context.id)
    res = state.api.execute_simulated_action_for_session(
        state.session_alice.session_id,
        ActionType.CREATE,
        "btn-add-event",
        ResourceType.EVENT,
        {"title": "Alice Birthday Party", "date": "2026-08-28"},
    )
    assert res["status"] == "success"
    pw = res["practice_world"]
    assert any(e["title"] == "Alice Birthday Party" for e in pw["simulated_events"])


def test_5_simulated_memory_creation_works():
    state = DemoState()
    state.api.start_practice_world_for_session(state.session_alice.session_id, state.family_context.id)
    res = state.api.execute_simulated_action_for_session(
        state.session_alice.session_id,
        ActionType.ATTACH,
        "btn-add-memory",
        ResourceType.MEMORY,
        {"title": "Sweet Memory", "summary": "Blowing out candles"},
    )
    assert res["status"] == "success"
    pw = res["practice_world"]
    assert any(m["title"] == "Sweet Memory" for m in pw["simulated_memories"])


def test_6_simulated_media_creation_works():
    state = DemoState()
    state.api.start_practice_world_for_session(state.session_alice.session_id, state.family_context.id)
    res = state.api.execute_simulated_action_for_session(
        state.session_alice.session_id,
        ActionType.ATTACH,
        "btn-capture-media",
        ResourceType.MEDIA,
        {"caption": "Cake Snapshot", "type": "PHOTO"},
    )
    assert res["status"] == "success"
    pw = res["practice_world"]
    assert any(m["caption"] == "Cake Snapshot" for m in pw["simulated_media_items"])


def test_7_simulated_celebration_creation_works():
    state = DemoState()
    state.api.start_practice_world_for_session(state.session_alice.session_id, state.family_context.id)
    res = state.api.execute_simulated_action_for_session(
        state.session_alice.session_id,
        ActionType.GENERATE,
        "btn-create-celebration",
        ResourceType.CELEBRATION_ARTIFACT,
        {"title": "Birthday Album", "theme": "FESTIVE"},
    )
    assert res["status"] == "success"
    pw = res["practice_world"]
    assert any(c["title"] == "Birthday Album" for c in pw["simulated_celebrations"])


def test_8_simulated_sharing_works():
    state = DemoState()
    state.api.start_practice_world_for_session(state.session_alice.session_id, state.family_context.id)
    res = state.api.execute_simulated_action_for_session(
        state.session_alice.session_id,
        ActionType.SHARE,
        "btn-share",
        ResourceType.SHARE_LINK,
        {"target_id": "sim_ev1"},
    )
    assert res["status"] == "success"
    pw = res["practice_world"]
    assert len(pw["simulated_share_links"]) >= 2


def test_9_simulated_activity_history_works():
    state = DemoState()
    state.api.start_practice_world_for_session(state.session_alice.session_id, state.family_context.id)
    state.api.execute_simulated_action_for_session(
        state.session_alice.session_id,
        ActionType.CREATE,
        "btn-add-event",
        ResourceType.EVENT,
        {"title": "Practice Dinner"},
    )
    hist = state.api.explain_practice_history_for_session(state.session_alice.session_id)
    assert hist["status"] == "success"
    assert hist["audit_type"] == "PRACTICE WORLD ACTIVITY"
    assert len(hist["simulated_transactions"]) >= 2


def test_10_reset_only_affects_practice_state():
    state = DemoState()
    events_before = len(state.api.canonical.list_events())
    state.api.start_practice_world_for_session(state.session_alice.session_id, state.family_context.id)
    state.api.execute_simulated_action_for_session(
        state.session_alice.session_id,
        ActionType.CREATE,
        "btn-add-event",
        ResourceType.EVENT,
        {"title": "Temporary Event"},
    )
    pw_reset = state.api.reset_practice_world_for_session(state.session_alice.session_id)
    assert pw_reset is not None
    # Real canonical state is unaffected
    assert len(state.api.canonical.list_events()) == events_before


def test_11_exit_preserves_real_state():
    state = DemoState()
    state.api.start_practice_world_for_session(state.session_alice.session_id, state.family_context.id)
    res = state.api.exit_practice_world_for_session(state.session_alice.session_id)
    assert res["status"] == "exited"
    assert "Your real FEMC data was not changed." in res["message"]


def test_12_watch_mode_works():
    state = DemoState()
    st = state.api.initialize_guided_experience_for_session(
        state.session_alice.session_id,
        state.family_context.id,
        mode=GuideMode.WATCH_JOURNEY,
    )
    assert st.current_mode == GuideMode.WATCH_JOURNEY


def test_13_learn_by_doing_works():
    state = DemoState()
    st = state.api.initialize_guided_experience_for_session(
        state.session_alice.session_id,
        state.family_context.id,
        mode=GuideMode.LEARN_BY_DOING,
    )
    assert st.current_mode == GuideMode.LEARN_BY_DOING


def test_14_watch_to_try_it_yourself_works():
    state = DemoState()
    state.api.initialize_guided_experience_for_session(
        state.session_alice.session_id, state.family_context.id, mode=GuideMode.WATCH_JOURNEY
    )
    st = state.api.switch_guided_experience_mode_for_session(
        state.session_alice.session_id, GuideMode.LEARN_BY_DOING
    )
    assert st.current_mode == GuideMode.LEARN_BY_DOING


def test_15_family_context_works():
    state = DemoState()
    pw = state.api.start_practice_world_for_session(
        state.session_alice.session_id, state.family_context.id, context_type=ContextType.FAMILY
    )
    assert pw.context_type == ContextType.FAMILY
    assert any(p["name"] == "Alice" for p in pw.simulated_persons)


def test_16_friends_context_works():
    state = DemoState()
    pw = state.api.start_practice_world_for_session(
        state.session_alice.session_id, state.family_context.id, context_type=ContextType.FRIENDS
    )
    assert pw.context_type == ContextType.FRIENDS
    assert any(p["name"] == "Sam" for p in pw.simulated_persons)


def test_17_community_context_works():
    state = DemoState()
    pw = state.api.start_practice_world_for_session(
        state.session_alice.session_id, state.family_context.id, context_type=ContextType.COMMUNITY
    )
    assert pw.context_type == ContextType.COMMUNITY
    assert any(p["name"] == "Elena (Lead)" for p in pw.simulated_persons)


def test_18_age_group_changes_contextual_simulation():
    state = DemoState()
    pw = state.api.start_practice_world_for_session(
        state.session_alice.session_id,
        state.family_context.id,
        context_type=ContextType.FRIENDS,
        age_group=AgeGroup.TEENS,
    )
    assert pw.age_group == AgeGroup.TEENS


def test_19_family_inclusion_works():
    state = DemoState()
    pw = state.api.start_practice_world_for_session(
        state.session_alice.session_id,
        state.family_context.id,
        context_type=ContextType.FRIENDS,
        include_family=True,
    )
    assert pw.include_family is True
    assert any("Mom" in p["name"] for p in pw.simulated_persons)


def test_20_english_works():
    state = DemoState()
    pw = state.api.start_practice_world_for_session(
        state.session_alice.session_id, state.family_context.id, language=Language.ENGLISH
    )
    assert pw.language == Language.ENGLISH


def test_21_tamil_works():
    state = DemoState()
    pw = state.api.start_practice_world_for_session(
        state.session_alice.session_id, state.family_context.id, language=Language.TAMIL
    )
    assert pw.language == Language.TAMIL


def test_22_hindi_works():
    state = DemoState()
    pw = state.api.start_practice_world_for_session(
        state.session_alice.session_id, state.family_context.id, language=Language.HINDI
    )
    assert pw.language == Language.HINDI
