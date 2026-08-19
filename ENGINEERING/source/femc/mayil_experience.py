"""Mayil's experience contract for the FEMC user-facing intelligence layer.

This module is deliberately UI-agnostic. It defines the stable behaviour that
presentation layers can consume so Mayil is treated as an attentive companion,
not merely a question/answer chatbot.

The contract is safe for both Practice and Real modes: it contains no family
content, no identity data, and no persistence. Actions returned by this module
are intents for an authorized caller to execute.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class MayilVoiceProfile:
    """Mayil's consistent persona across supported languages."""

    language: str
    speech_locale: str
    voice_role: str = "mayil_female"
    allow_browser_fallback: bool = True


@dataclass(frozen=True)
class MayilSuggestion:
    """A contextual, non-intrusive suggestion Mayil may offer."""

    intent: str
    label: str
    reason: str
    action: str
    priority: int = 50


@dataclass(frozen=True)
class MayilExperienceProfile:
    """Runtime-neutral contract for an attentive Mayil interaction."""

    mode: str
    current_view: str
    state: str
    voice: MayilVoiceProfile
    suggestions: List[MayilSuggestion]
    capabilities: List[str]


_SUPPORTED_VOICES: Dict[str, MayilVoiceProfile] = {
    "en": MayilVoiceProfile("en", "en-IN"),
    "hi": MayilVoiceProfile("hi", "hi-IN"),
    "ta": MayilVoiceProfile("ta", "ta-IN"),
}

_CAPABILITIES = [
    "understand_intent",
    "remember_current_context",
    "guide_navigation",
    "explain_family_context",
    "show_memory_story",
    "open_album",
    "create_celebration",
    "create_reminder",
    "assist_with_sharing",
    "explain_vel_guardian",
    "coach_practice_journey",
]


_VIEW_SUGGESTIONS: Dict[str, List[MayilSuggestion]] = {
    "home": [
        MayilSuggestion("explore_family", "Meet the family", "Start with the people who make the family story.", "loadView('family')", 90),
        MayilSuggestion("explore_story", "Show me a family story", "See how events, memories and media connect.", "loadView('memories')", 80),
    ],
    "family": [
        MayilSuggestion("explore_calendar", "See their calendar", "Family members become meaningful when their moments have context.", "loadView('calendar')", 80),
    ],
    "calendar": [
        MayilSuggestion("view_memory", "Turn an event into a memory", "Alice's birthday is a good Practice example.", "loadView('memories')", 90),
        MayilSuggestion("ask_mayil", "Ask Mayil what to do next", "Mayil can guide the journey without making you hunt through menus.", "openAskMayilPanel()", 70),
    ],
    "memories": [
        MayilSuggestion("view_story", "Walk through the story", "A memory becomes richer when its related moments are viewed together.", "openPracticeStory()", 100),
        MayilSuggestion("open_album", "Open the family album", "Albums gather related moments into something worth revisiting.", "loadView('media')", 90),
        MayilSuggestion("celebrate", "Create a celebration", "Mayil can turn a meaningful moment into a celebration artifact.", "openPracticeCelebration()", 80),
    ],
    "media": [
        MayilSuggestion("open_album", "Open an album", "See several connected moments rather than isolated photos.", "openPracticeAlbum()", 100),
        MayilSuggestion("view_story", "View the story", "Let the selected moments become a guided story.", "openPracticeStory()", 90),
        MayilSuggestion("celebrate", "Create a celebration", "Turn selected memories into a celebration experience.", "openPracticeCelebration()", 85),
    ],
    "celebrations": [
        MayilSuggestion("replay_story", "Replay the story", "Celebrations are strongest when they remain connected to the memory.", "openPracticeStory()", 80),
        MayilSuggestion("share", "Share this moment", "Mayil can guide you through safe sharing.", "loadView('sharing')", 70),
    ],
    "guardian": [
        MayilSuggestion("guardian_explain", "Explain VEL Guardian", "Understand how FEMC protects the family world.", "openVelGuardianExplanation()", 100),
    ],
}


def detect_language(text: str, preferred: Optional[str] = None) -> str:
    """Choose Mayil's language without changing Mayil's persona."""

    if preferred in _SUPPORTED_VOICES:
        return preferred  # explicit user choice wins
    value = text or ""
    if any("\u0B80" <= ch <= "\u0BFF" for ch in value):
        return "ta"
    if any("\u0900" <= ch <= "\u097F" for ch in value):
        return "hi"
    return "en"


def voice_for(language: str) -> MayilVoiceProfile:
    """Return the consistent female Mayil voice contract for a language."""

    return _SUPPORTED_VOICES.get(language, _SUPPORTED_VOICES["en"])


def suggestions_for_view(view: str, mode: str = "real") -> List[MayilSuggestion]:
    """Return calm, contextual suggestions; no suggestion is a forced prompt."""

    suggestions = list(_VIEW_SUGGESTIONS.get((view or "home").lower(), []))
    if mode == "practice":
        suggestions.insert(
            0,
            MayilSuggestion(
                "practice_coach",
                "Let Mayil guide me",
                "Practice mode is designed to be learned by doing.",
                "startMayilPracticeCoach()",
                110,
            ),
        )
    return sorted(suggestions, key=lambda item: item.priority, reverse=True)


def build_profile(
    current_view: str = "home",
    mode: str = "real",
    language: Optional[str] = None,
    user_text: str = "",
    state: str = "idle",
) -> MayilExperienceProfile:
    """Build the presentation contract for the current Mayil moment."""

    lang = detect_language(user_text, language)
    return MayilExperienceProfile(
        mode=mode,
        current_view=current_view or "home",
        state=state,
        voice=voice_for(lang),
        suggestions=suggestions_for_view(current_view, mode),
        capabilities=list(_CAPABILITIES),
    )


__all__ = [
    "MayilVoiceProfile",
    "MayilSuggestion",
    "MayilExperienceProfile",
    "build_profile",
    "detect_language",
    "voice_for",
    "suggestions_for_view",
]
