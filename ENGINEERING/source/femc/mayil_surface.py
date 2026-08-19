"""Presentation contract for FEMC's persistent Mayil companion.

The companion is deliberately small: it stays present across the product,
responds to the current page, and invites discovery without covering content.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .mayil_experience import MayilSuggestion, build_profile


@dataclass(frozen=True)
class MayilSurface:
    view: str
    mode: str
    greeting: str
    message: str
    suggestions: List[MayilSuggestion]
    visual_state: str = "attentive"
    persistent: bool = True


_GREETINGS: Dict[str, str] = {
    "en": "I'm here with you.",
    "hi": "मैं आपके साथ हूँ।",
    "ta": "நான் உங்களுடன் இருக்கிறேன்.",
}

_MESSAGES: Dict[str, str] = {
    "home": "We can explore your family story together. Start anywhere — I’ll help you discover what connects.",
    "family": "Let’s meet the people behind the memories. I can help you move from a person to their moments.",
    "calendar": "I can help you turn dates into meaningful family moments — and show you what belongs with each event.",
    "memories": "This is where family moments become stories. I can walk you through a memory, its album, or a celebration.",
    "media": "Don’t just browse pictures. Let’s discover the story behind them, open an album, or create something beautiful.",
    "celebrations": "A celebration is more than a card. I can take you back to the memory, enrich it, and help you share it safely.",
    "reminders": "I’ll help keep important family moments from slipping past you.",
    "guardian": "This is VEL Guardian. I can explain what is protected, why it matters, and what you can safely do.",
    "sharing": "Before you share, I can help you understand exactly what family content is being shared.",
    "history": "Your family activity has a story too. I can explain what happened and how moments became connected.",
    "settings": "Your family space belongs to you. I can help you understand settings, ownership, and portability.",
    "mayil": "This is my home. Ask me naturally, or let me guide you through FEMC one meaningful step at a time.",
}


def build_surface(view: str = "home", mode: str = "real", language: str = "en") -> MayilSurface:
    view = (view or "home").lower()
    profile = build_profile(current_view=view, mode=mode, language=language)
    lang = profile.voice.language
    return MayilSurface(
        view=view,
        mode=mode,
        greeting=_GREETINGS.get(lang, _GREETINGS["en"]),
        message=_MESSAGES.get(view, _MESSAGES["home"]),
        suggestions=profile.suggestions[:3],
    )


__all__ = ["MayilSurface", "build_surface"]
