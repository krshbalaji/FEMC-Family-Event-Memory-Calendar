from ENGINEERING.source.femc.mayil_experience import (
    build_profile,
    detect_language,
    suggestions_for_view,
    voice_for,
)


def test_mayil_keeps_same_female_persona_across_languages():
    assert voice_for("en").voice_role == "mayil_female"
    assert voice_for("hi").voice_role == "mayil_female"
    assert voice_for("ta").voice_role == "mayil_female"
    assert voice_for("ta").speech_locale == "ta-IN"


def test_mayil_detects_user_language_without_changing_persona():
    assert detect_language("வணக்கம் மயில்") == "ta"
    assert detect_language("नमस्ते मयिल") == "hi"
    assert detect_language("Show me Alice's story") == "en"


def test_practice_mayil_prioritizes_guided_learning():
    suggestions = suggestions_for_view("memories", mode="practice")
    assert suggestions[0].intent == "practice_coach"
    assert any(item.intent == "view_story" for item in suggestions)
    assert any(item.intent == "celebrate" for item in suggestions)


def test_mayil_profile_is_contextual_and_action_oriented():
    profile = build_profile(
        current_view="media",
        mode="practice",
        language="en",
        state="idle",
    )
    assert profile.current_view == "media"
    assert profile.mode == "practice"
    assert "understand_intent" in profile.capabilities
    assert any(item.intent == "open_album" for item in profile.suggestions)
    assert any(item.intent == "view_story" for item in profile.suggestions)
