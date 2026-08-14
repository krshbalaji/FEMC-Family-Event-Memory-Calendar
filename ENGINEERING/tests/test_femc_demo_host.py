from __future__ import annotations

import datetime
import json
from run import (
    DemoState,
    DemoHTTPRequestHandler,
    HTML_TEMPLATE,
    to_dict,
    generate_media_download_filename,
)
from ENGINEERING.source.femc.models import (
    VisibilityLevel,
    EventCategory,
    ShareResourceType,
    MediaType,
)


def test_demo_state_initialization():
    state = DemoState()
    assert state.api is not None
    assert state.session_id is not None
    assert state.family_context is not None
    assert state.event1.title == "Alice's Birthday Celebration"
    assert state.event1.category.value == "birthday"
    assert state.event2.title == "Smith Family Weekend Dinner"
    assert state.event2.category.value == "general"
    assert state.memory1.narrative == "We blew out candles and shared old photo albums."


def test_demo_state_reset():
    state = DemoState()
    old_session_id = state.session_id
    state.reset()
    assert state.session_id != old_session_id


def test_demo_api_endpoints_data():
    state = DemoState()
    api = state.api
    sess_id = state.session_id
    fc_id = state.family_context.id

    dashboard = api.get_dashboard_summary_for_session(sess_id, fc_id)
    assert dashboard is not None

    topology = api.get_family_topology_for_session(sess_id, fc_id)
    assert topology is not None

    calendar = api.get_calendar_for_session(sess_id, fc_id)
    assert len(calendar) >= 2

    timeline = api.get_timeline_for_session(sess_id, fc_id)
    assert len(timeline) >= 1

    artifacts = api.list_celebration_artifacts_for_session(sess_id, fc_id)
    assert len(artifacts) >= 1

    audit = api.run_integrity_audit_for_session(sess_id, fc_id)
    assert audit.is_valid is True

    export = api.export_family_context_for_session(sess_id, fc_id)
    val = api.validate_data_export(to_dict(export))
    assert val.is_valid is True


def test_productized_html_template():
    assert "FEMC" in HTML_TEMPLATE
    assert "v2.3-C Complete" in HTML_TEMPLATE
    assert "🏠 HOME" in HTML_TEMPLATE
    assert "👨‍👩‍👧‍👦 FAMILY" in HTML_TEMPLATE
    assert "📅 CALENDAR" in HTML_TEMPLATE
    assert "📖 MEMORIES" in HTML_TEMPLATE
    assert "🎉 CELEBRATIONS" in HTML_TEMPLATE
    assert "🔔 REMINDERS" in HTML_TEMPLATE
    assert "🧠 MAYIL AI" in HTML_TEMPLATE
    assert "🔗 SHARING" in HTML_TEMPLATE
    assert "⚙️ SETTINGS / DATA" in HTML_TEMPLATE
    assert "perspective-select" in HTML_TEMPLATE


def test_notification_mark_read_via_api():
    state = DemoState()
    api = state.api
    sess_id = state.session_id
    notif_id = state.notif1.id

    notif = api.mark_notification_read_for_session(sess_id, notif_id)
    assert notif.status.value == "read"


def test_projection_truth_cross_screen_consistency():
    state = DemoState()
    api = state.api
    sess_id = state.session_id
    fc_id = state.family_context.id

    calendar_entries = api.get_calendar_for_session(sess_id, fc_id)
    calendar_event_ids = {c.event_id for c in calendar_entries}
    assert len(calendar_event_ids) >= 2

    dashboard_entries = api.get_dashboard_projection_for_session(sess_id, fc_id)
    dashboard_event_ref_ids = {
        e.ref_id for e in dashboard_entries
        if e.item_type.value in ("upcoming_event", "recurring_event", "celebration_highlight")
    }

    for event_id in calendar_event_ids:
        assert event_id in dashboard_event_ref_ids

    insight = api.analyze_family_insights_for_session(sess_id, fc_id)
    assert insight.family_context_id == fc_id
    assert "events" in insight.analysis_summary


def test_onboarding_creates_family_member():
    state = DemoState()
    acc, per, sess = state.onboard_member("David Smith", "david@example.com", "MEMBER")

    assert acc is not None
    assert per.name == "David Smith"
    assert acc.email == "david@example.com"
    assert acc.id in state.family_context.member_ids
    assert acc.id in state.account_sessions


def test_perspective_switching_changes_active_session():
    state = DemoState()
    alice_session = state.session_id
    bob_session = state.account_sessions[state.acc_bob.id]

    new_session = state.switch_session(state.acc_bob.id)
    assert new_session == bob_session
    assert state.active_account_id == state.acc_bob.id
    assert state.session_id == bob_session


def test_privacy_proof_alice_private_event_invisible_to_bob():
    state = DemoState()
    api = state.api
    fc_id = state.family_context.id

    alice_session = state.session_alice.session_id
    bob_session = state.session_bob.session_id

    alice_cal = api.get_calendar_for_session(alice_session, fc_id)
    alice_cal_ids = {c.event_id for c in alice_cal}

    bob_cal = api.get_calendar_for_session(bob_session, fc_id)
    bob_cal_ids = {c.event_id for c in bob_cal}

    assert state.event_alice_private.id in alice_cal_ids
    assert state.event_alice_private.id not in bob_cal_ids

    assert state.event_bob_private.id in bob_cal_ids
    assert state.event_bob_private.id not in alice_cal_ids


def test_privacy_proof_family_event_visible_to_both():
    state = DemoState()
    api = state.api
    fc_id = state.family_context.id

    alice_cal = api.get_calendar_for_session(state.session_alice.session_id, fc_id)
    alice_ids = {c.event_id for c in alice_cal}

    bob_cal = api.get_calendar_for_session(state.session_bob.session_id, fc_id)
    bob_ids = {c.event_id for c in bob_cal}

    assert state.event1.id in alice_ids
    assert state.event1.id in bob_ids
    assert state.event2.id in alice_ids
    assert state.event2.id in bob_ids


def test_target_person_ids_survive_event_creation():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    new_event = api.create_event_for_session(
        session_id=sess_id,
        title="Charlie's Graduation",
        description="Milestone ceremony",
        family_context_id=fc_id,
        start_time=datetime.datetime.now() + datetime.timedelta(days=10),
        end_time=None,
        visibility=VisibilityLevel.FAMILY,
        category=EventCategory.MILESTONE,
        target_person_ids=[state.p_charlie.id],
    )

    assert new_event.target_person_ids == [state.p_charlie.id]

    detail = api.build_rich_event_detail_for_session(sess_id, new_event.id)
    assert len(detail.target_persons) == 1
    assert detail.target_persons[0].id == state.p_charlie.id

    person_detail = api.build_rich_person_detail_for_session(sess_id, state.p_charlie.id)
    person_event_ids = {e.id for e in person_detail.events}
    assert new_event.id in person_event_ids


def test_v2_3_b_media_creation_and_attachment():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    media = api.create_media_item_for_session(
        session_id=sess_id,
        uri="https://images.unsplash.com/photo-1513151233558-d860c5398176",
        caption="Birthday Party Photo",
        family_context_id=fc_id,
        event_id=state.event1.id,
        memory_id=state.memory1.id,
        visibility=VisibilityLevel.FAMILY,
    )

    assert media.id is not None
    assert media.event_id == state.event1.id
    assert media.memory_id == state.memory1.id

    event_media = api.list_media_items_for_event_for_session(sess_id, state.event1.id)
    assert any(m.id == media.id for m in event_media)

    memory_media = api.list_media_items_for_memory_for_session(sess_id, state.memory1.id)
    assert any(m.id == media.id for m in memory_media)


def test_v2_3_b_authorized_media_visibility_isolation():
    state = DemoState()
    api = state.api
    fc_id = state.family_context.id
    alice_sess = state.session_alice.session_id
    bob_sess = state.session_bob.session_id

    priv_media = api.create_media_item_for_session(
        session_id=alice_sess,
        uri="https://images.unsplash.com/photo-private",
        caption="Alice Private Journal Photo",
        family_context_id=fc_id,
        visibility=VisibilityLevel.PRIVATE,
    )

    alice_retrieved = api.get_media_item_for_session(alice_sess, priv_media.id)
    assert alice_retrieved.id == priv_media.id

    try:
        api.get_media_item_for_session(bob_sess, priv_media.id)
        assert False, "Bob session should not be authorized to view Alice private media"
    except PermissionError:
        pass


def test_v2_3_b_celebration_artifact_generation_and_canonical_reference():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    # Event artifact
    art_event = api.build_celebration_artifact_for_event_for_session(sess_id, state.event1.id)
    assert art_event.source_event_id == state.event1.id
    assert "Alice's Birthday Celebration" in art_event.title

    # Person artifact
    art_person = api.build_celebration_artifact_for_person_for_session(sess_id, state.p_alice.id, fc_id)
    assert art_person.source_person_id == state.p_alice.id

    # Memory artifact
    art_memory = api.build_celebration_artifact_for_memory_for_session(sess_id, state.memory1.id)
    assert art_memory.source_memory_id == state.memory1.id

    # Album artifact
    art_album = api.build_celebration_album_artifact_for_session(sess_id, state.album1.id)
    assert art_album.artifact_type.value == "celebration_album"
    assert "Summer Celebrations 2026" in art_album.title


def test_v2_3_b_share_link_creation_resolution_and_revocation():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    share_link = api.create_share_link_for_session(
        session_id=sess_id,
        resource_type=ShareResourceType.EVENT,
        resource_id=state.event1.id,
        family_context_id=fc_id,
        expires_in_minutes=60,
    )

    assert share_link.token is not None
    assert share_link.resource_id == state.event1.id

    res = api.resolve_share_token(share_link.token)
    assert res is not None
    assert res.id == state.event1.id

    revoked_link = api.revoke_share_link_for_session(sess_id, share_link.token)
    assert revoked_link.is_revoked is True

    try:
        api.resolve_share_token(share_link.token)
        assert False, "Resolving revoked share link should raise PermissionError"
    except PermissionError:
        pass


def test_v2_3_b_cross_screen_canonical_identity_consistency():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    canonical_event_id = state.event1.id

    # Calendar
    cal = api.get_calendar_for_session(sess_id, fc_id)
    assert any(c.event_id == canonical_event_id for c in cal)

    # Timeline & Memories
    event_memories = api.get_event_with_memories_for_session(sess_id, canonical_event_id)
    assert event_memories.event.id == canonical_event_id

    # Media
    media = api.list_media_items_for_event_for_session(sess_id, canonical_event_id)
    assert any(m.event_id == canonical_event_id for m in media)

    # Celebration Artifact
    artifact = api.build_celebration_artifact_for_event_for_session(sess_id, canonical_event_id)
    assert artifact.source_event_id == canonical_event_id

    # Share Link
    share = api.create_share_link_for_session(
        session_id=sess_id,
        resource_type=ShareResourceType.EVENT,
        resource_id=canonical_event_id,
        family_context_id=fc_id,
    )
    assert share.resource_id == canonical_event_id


def test_v2_3_b_1_av_media_types_and_playback_support():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    video_item = api.create_media_item_for_session(
        session_id=sess_id,
        uri="https://www.w3schools.com/html/mov_bbb.mp4",
        media_type=MediaType.VIDEO,
        caption="Summer Park Video",
        family_context_id=fc_id,
        event_id=state.event2.id,
        memory_id=state.memory1.id,
        visibility=VisibilityLevel.FAMILY,
    )

    assert video_item.id is not None
    assert video_item.media_type.value == "video"
    assert video_item.uri.endswith(".mp4")

    audio_item = api.create_media_item_for_session(
        session_id=sess_id,
        uri="https://www.w3schools.com/html/horse.mp3",
        media_type=MediaType.AUDIO,
        caption="Voice Note",
        family_context_id=fc_id,
        event_id=state.event1.id,
        memory_id=state.memory1.id,
        visibility=VisibilityLevel.FAMILY,
    )

    assert audio_item.id is not None
    assert audio_item.media_type.value == "audio"
    assert audio_item.uri.endswith(".mp3")

    memory_media = api.list_media_items_for_memory_for_session(sess_id, state.memory1.id)
    types_found = {m.media_type.value for m in memory_media}
    assert "photo" in types_found
    assert "video" in types_found
    assert "audio" in types_found


def test_v2_3_b_2_download_filename_generation():
    fn_photo = generate_media_download_filename("Alice Birthday Candles", "photo", "2026-08-13")
    assert fn_photo == "Alice_Birthday_Candles_2026-08-13.jpg"

    fn_video = generate_media_download_filename("Charlie at Summer Park!", "video", "2026-08-13")
    assert fn_video == "Charlie_at_Summer_Park_2026-08-13.mp4"

    fn_audio = generate_media_download_filename("Grandma's Birthday Song", "audio", "2026-08-13")
    assert fn_audio == "Grandma_s_Birthday_Song_2026-08-13.mp3"

    assert "id" not in fn_photo.lower() and len(fn_photo) < 60


def test_v2_3_b_2_media_item_sharing_token_creation_and_resolution():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    share_link = api.create_share_link_for_session(
        session_id=sess_id,
        resource_type=ShareResourceType.MEDIA_ITEM,
        resource_id=state.media1.id,
        family_context_id=fc_id,
        expires_in_minutes=1440,
    )

    assert share_link.token is not None
    assert share_link.resource_type.value == "media_item"
    assert share_link.resource_id == state.media1.id

    res_item = api.resolve_share_token(share_link.token)
    assert res_item is not None
    assert res_item.id == state.media1.id
    assert res_item.caption == "Alice blowing out birthday candles"


def test_v2_3_b_2_revoked_media_share_token_cannot_resolve():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    share_link = api.create_share_link_for_session(
        session_id=sess_id,
        resource_type=ShareResourceType.MEDIA_ITEM,
        resource_id=state.media_video1.id,
        family_context_id=fc_id,
    )

    revoked = api.revoke_share_link_for_session(sess_id, share_link.token)
    assert revoked.is_revoked is True

    try:
        api.resolve_share_token(share_link.token)
        assert False, "Resolving revoked media share link should raise PermissionError"
    except PermissionError:
        pass


def test_v2_3_b_2_all_resource_types_sharing_preservation():
    state = DemoState()
    api = state.api
    sess_id = state.session_alice.session_id
    fc_id = state.family_context.id

    # Event
    link_evt = api.create_share_link_for_session(sess_id, ShareResourceType.EVENT, state.event1.id, fc_id)
    assert api.resolve_share_token(link_evt.token).id == state.event1.id

    # Memory
    link_mem = api.create_share_link_for_session(sess_id, ShareResourceType.MEMORY, state.memory1.id, fc_id)
    assert api.resolve_share_token(link_mem.token).id == state.memory1.id

    # Media Item
    link_item = api.create_share_link_for_session(sess_id, ShareResourceType.MEDIA_ITEM, state.media1.id, fc_id)
    assert api.resolve_share_token(link_item.token).id == state.media1.id

    # Media Album
    link_album = api.create_share_link_for_session(sess_id, ShareResourceType.MEDIA_ALBUM, state.album1.id, fc_id)
    assert api.resolve_share_token(link_album.token).id == state.album1.id


# ==================================================
# WORKSTREAM V2.3-C REGRESSION TESTS
# ==================================================

def test_v2_3_c_mayil_interactive_engine_structure():
    assert "openAskMayilPanel" in HTML_TEMPLATE
    assert "FEMC_INTENTS" in HTML_TEMPLATE
    assert "resolveFEMCIntent" in HTML_TEMPLATE
    assert "JOURNEY_SCENES" in HTML_TEMPLATE
    assert "openAnimatedJourneyModal" in HTML_TEMPLATE
    assert "renderMayilAvatarSVG" in HTML_TEMPLATE


def test_v2_3_c_multilingual_intent_resolution():
    assert "OPEN_FAMILY" in HTML_TEMPLATE
    assert "OPEN_CALENDAR" in HTML_TEMPLATE
    assert "CREATE_EVENT" in HTML_TEMPLATE
    assert "RECORD_MEMORY" in HTML_TEMPLATE
    assert "OPEN_CELEBRATIONS" in HTML_TEMPLATE
    assert "OPEN_GUARDIAN" in HTML_TEMPLATE
    assert "OPEN_SETTINGS" in HTML_TEMPLATE


def test_v2_3_c_animated_journey_scenes_count_and_pillars():
    assert "🌅 Welcome Home" in HTML_TEMPLATE
    assert "👨‍👩‍👧 Meet the Family" in HTML_TEMPLATE
    assert "🌳 Family Relationships" in HTML_TEMPLATE
    assert "📅 Family Calendar" in HTML_TEMPLATE
    assert "📖 Family Memory" in HTML_TEMPLATE
    assert "🎉 Celebration Studio" in HTML_TEMPLATE
    assert "🔔 Reminders" in HTML_TEMPLATE
    assert "🔗 Sharing" in HTML_TEMPLATE
    assert "🤖 Mayil AI" in HTML_TEMPLATE
    assert "🛡️ Guardian" in HTML_TEMPLATE
    assert "💾 Data Ownership" in HTML_TEMPLATE


def test_v2_3_c_mayil_avatar_visual_states():
    assert "mayil-avatar" in HTML_TEMPLATE
    assert "idle" in HTML_TEMPLATE
    assert "speaking" in HTML_TEMPLATE
    assert "listening" in HTML_TEMPLATE
    assert "thinking" in HTML_TEMPLATE
    assert "happy" in HTML_TEMPLATE
