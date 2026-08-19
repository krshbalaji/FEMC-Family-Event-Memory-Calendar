from ENGINEERING.source.femc.external_observability import ExternalPracticeObservability


def test_external_practice_session_tracks_presence_and_pages():
    obs = ExternalPracticeObservability()
    session = obs.start_session()

    obs.record_event(session.session_id, "page_view", page="home")
    obs.record_event(session.session_id, "page_view", page="memories")
    obs.touch(session.session_id)

    summary = obs.dashboard()

    assert summary["visitors"] == 1
    assert summary["explored"] == 1
    assert summary["feedback_submitted"] == 0
    assert summary["page_counts"]["home"] == 1
    assert summary["page_counts"]["memories"] == 1


def test_external_practice_feedback_is_optional_and_sanitized():
    obs = ExternalPracticeObservability()
    session = obs.start_session()

    assert obs.submit_feedback(
        session.session_id,
        {
            "liked": "easy",
            "confusing": "sharing",
            "broken": "none",
            "change_request": "make feedback easier",
        },
    )

    summary = obs.dashboard()
    assert summary["feedback_submitted"] == 1
    assert summary["feedback_pending"] == 0


def test_external_practice_session_end_is_idempotent():
    obs = ExternalPracticeObservability()
    session = obs.start_session()

    assert obs.end_session(session.session_id)
    assert obs.end_session(session.session_id)
    assert obs.sessions[session.session_id].ended_at is not None
