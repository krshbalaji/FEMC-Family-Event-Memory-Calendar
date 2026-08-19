"""Immersive visual seeding for the isolated Mayil Practice World.

This module deliberately patches only the fictional practice-world seed data.
Canonical family data, real media, real albums, and real transactions are not
modified. The existing practice-world isolation boundary remains authoritative.
"""

from .services import MayilGuidedExperienceService


_ORIGINAL_SEED = MayilGuidedExperienceService._seed_practice_world_data


# Stable Unsplash image assets used only for fictional training content.
_VISUALS = [
    {
        "id": "sim_med1",
        "caption": "Alice's birthday candles glowing before the big wish",
        "url": "https://images.unsplash.com/photo-1513151233558-d860c5398176",
        "memory_id": "sim_mem1",
        "event_id": "sim_ev1",
        "scene": "birthday",
        "motion": "candle-glow",
    },
    {
        "id": "sim_med2",
        "caption": "Warm campfire stories during the family getaway",
        "url": "https://images.unsplash.com/photo-1475483768296-6163e08872a1",
        "memory_id": "sim_mem2",
        "event_id": "sim_ev2",
        "scene": "getaway",
        "motion": "fire-glow",
    },
    {
        "id": "sim_med3",
        "caption": "Charlie's proud homemade dessert moment",
        "url": "https://images.unsplash.com/photo-1551024506-0bccd828d307",
        "memory_id": "sim_mem3",
        "event_id": "sim_ev1",
        "scene": "family-dinner",
        "motion": "soft-rise",
    },
    {
        "id": "sim_med4",
        "caption": "Birthday cake ready for the family celebration",
        "url": "https://images.unsplash.com/photo-1535140728325-a4d3707eee61",
        "memory_id": "sim_mem1",
        "event_id": "sim_ev1",
        "scene": "birthday",
        "motion": "sparkle",
    },
    {
        "id": "sim_med5",
        "caption": "Colorful birthday decorations waiting for the family",
        "url": "https://images.unsplash.com/photo-1530103862676-de8c9debad1d",
        "memory_id": "sim_mem1",
        "event_id": "sim_ev1",
        "scene": "birthday",
        "motion": "balloon-float",
    },
    {
        "id": "sim_med6",
        "caption": "A family moment captured around the celebration table",
        "url": "https://images.unsplash.com/photo-1511895426328-dc8714191300",
        "memory_id": "sim_mem1",
        "event_id": "sim_ev1",
        "scene": "family",
        "motion": "gentle-zoom",
    },
    {
        "id": "sim_med7",
        "caption": "A playful family afternoon outdoors",
        "url": "https://images.unsplash.com/photo-1503454537195-1dcabb73ffb9",
        "memory_id": "sim_mem2",
        "event_id": "sim_ev2",
        "scene": "getaway",
        "motion": "parallax",
    },
    {
        "id": "sim_med8",
        "caption": "Cake, laughter and a table full of family memories",
        "url": "https://images.unsplash.com/photo-1464349153735-7db50ed83c84",
        "memory_id": "sim_mem3",
        "event_id": "sim_ev1",
        "scene": "family-dinner",
        "motion": "soft-rise",
    },
]


def _immersive_seed(self, pw):
    _ORIGINAL_SEED(self, pw)

    # Keep the existing four canonical practice media IDs intact, but make
    # their presentation richer and add a small fictional gallery.
    existing = {item.get("id"): item for item in pw.simulated_media_items}
    for visual in _VISUALS:
        item = existing.get(visual["id"])
        if item is None:
            item = {
                "id": visual["id"],
                "type": "PHOTO",
                "memory_id": visual["memory_id"],
                "event_id": visual["event_id"],
            }
            pw.simulated_media_items.append(item)
        item["caption"] = visual["caption"]
        item["url"] = visual["url"]
        item["scene"] = visual["scene"]
        item["motion"] = visual["motion"]
        item["is_practice_visual"] = True

    # Turn the single placeholder celebration into a small, browsable
    # fictional set without changing the underlying celebration workflow.
    if pw.simulated_celebrations:
        pw.simulated_celebrations[0].update({
            "subtitle": "Alice's Birthday — Golden Joy",
            "visual_media_id": "sim_med4",
            "is_practice_visual": True,
        })
    pw.simulated_celebrations.extend([
        {
            "id": "sim_cel2",
            "title": "Weekend Getaway Memory Album",
            "theme": "CAMPFIRE_NIGHTS",
            "subtitle": "Stories, stars and family laughter",
            "visual_media_id": "sim_med2",
            "is_practice_visual": True,
        },
        {
            "id": "sim_cel3",
            "title": "Sunday Family Moments",
            "theme": "HOME_WARMTH",
            "subtitle": "The little moments become the big memories",
            "visual_media_id": "sim_med8",
            "is_practice_visual": True,
        },
    ])

    # Make the practice world self-describing for presentation layers.
    pw.practice_visual_theme = "LIVING_FAMILY_STORY"
    pw.practice_visual_notice = (
        "Fictional practice family with synthetic training media. "
        "No real family data is represented."
    )


MayilGuidedExperienceService._seed_practice_world_data = _immersive_seed
