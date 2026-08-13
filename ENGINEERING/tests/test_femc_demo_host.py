from __future__ import annotations

import json
from run import DemoState, DemoHTTPRequestHandler, HTML_TEMPLATE, to_dict


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
    assert "v1.0 First User Experience Demo" in HTML_TEMPLATE
    assert "🏠 HOME" in HTML_TEMPLATE
    assert "👨‍👩‍👧‍👦 FAMILY" in HTML_TEMPLATE
    assert "📅 CALENDAR" in HTML_TEMPLATE
    assert "📖 MEMORIES" in HTML_TEMPLATE
    assert "🎉 CELEBRATIONS" in HTML_TEMPLATE
    assert "🔔 REMINDERS" in HTML_TEMPLATE
    assert "🧠 MAYIL AI" in HTML_TEMPLATE
    assert "⚙️ SETTINGS / DATA" in HTML_TEMPLATE
    assert "Technical Details" in HTML_TEMPLATE


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

    # 1. Fetch Calendar Projection
    calendar_entries = api.get_calendar_for_session(sess_id, fc_id)
    calendar_event_ids = {c.event_id for c in calendar_entries}
    assert len(calendar_event_ids) >= 2

    # 2. Fetch Dashboard Projection Entries
    dashboard_entries = api.get_dashboard_projection_for_session(sess_id, fc_id)
    dashboard_event_ref_ids = {
        e.ref_id for e in dashboard_entries
        if e.item_type.value in ("upcoming_event", "recurring_event", "celebration_highlight")
    }

    # 3. Verify Calendar event IDs match Dashboard projection ref IDs
    for event_id in calendar_event_ids:
        assert event_id in dashboard_event_ref_ids

    # 4. Fetch Mayil AI Insights
    insight = api.analyze_family_insights_for_session(sess_id, fc_id)
    assert insight.family_context_id == fc_id
    assert "events" in insight.analysis_summary
