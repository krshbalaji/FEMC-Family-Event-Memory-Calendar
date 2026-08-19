from ENGINEERING.source.femc.mayil_surface import build_surface


def test_surface_is_persistent_and_contextual():
    surface = build_surface("media", "real", "en")
    assert surface.persistent is True
    assert surface.visual_state == "attentive"
    assert "story" in surface.message.lower()
    assert any(s.intent == "open_album" for s in surface.suggestions)


def test_surface_uses_tamil_persona():
    surface = build_surface("home", "real", "ta")
    assert surface.greeting == "நான் உங்களுடன் இருக்கிறேன்."


def test_guardian_surface_uses_vel_name():
    surface = build_surface("guardian", "real", "en")
    assert "VEL Guardian" in surface.message
