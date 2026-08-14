from __future__ import annotations

import datetime
import enum
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

# Ensure repository root is on Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ENGINEERING.source.femc.api import FEMCApi
from ENGINEERING.source.femc.models import (
    Confidence,
    EventCategory,
    MediaType,
    NotificationType,
    RelationshipType,
    ReminderType,
    ShareResourceType,
    VisibilityLevel,
    _utc_now,
)


def to_dict(obj):
    if hasattr(obj, "__dataclass_fields__"):
        return {k: to_dict(getattr(obj, k)) for k in obj.__dataclass_fields__}
    elif isinstance(obj, list):
        return [to_dict(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, enum.Enum):
        return obj.value
    elif isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    elif isinstance(obj, (int, float, str, bool)) or obj is None:
        return obj
    else:
        return str(obj)


def generate_media_download_filename(caption: str, media_type: str, date_str: str = "2026-08-13") -> str:
    clean = "".join(c if (c.isalnum() or c in ("-", "_")) else "_" for c in (caption or "Family_Moment"))[:30].strip("_")
    mtype = (media_type or "photo").lower()
    ext = ".jpg"
    if mtype == "video":
        ext = ".mp4"
    elif mtype == "audio":
        ext = ".mp3"
    return f"{clean}_{date_str}{ext}"


class DemoState:

    def seed_demo_transactions(self):
        sess_id = self.session_alice.session_id
        fc_id = self.family_context.id
        cid = "demo-journey-chain-1"

        from ENGINEERING.source.femc.models import ActionType, ResourceType, VisibilityLevel

        # 1. Add Person
        self.api.record_transaction_for_session(
            session_id=sess_id, family_context_id=fc_id, action_type=ActionType.CREATE,
            resource_type=ResourceType.PERSON, resource_id=self.p_alice.id,
            resource_label_snapshot="Alice Smith", operation="Added Alice Smith to family group",
            correlation_id=cid
        )
        # 2. Schedule Event
        if hasattr(self, 'event1') and self.event1:
            self.api.record_transaction_for_session(
                session_id=sess_id, family_context_id=fc_id, action_type=ActionType.CREATE,
                resource_type=ResourceType.EVENT, resource_id=self.event1.id,
                resource_label_snapshot="Grandma's 80th Birthday", operation="Scheduled family birthday dinner for Aug 20",
                correlation_id=cid
            )
        # 3. Attach Photos
        if hasattr(self, 'media1') and self.media1:
            self.api.record_transaction_for_session(
                session_id=sess_id, family_context_id=fc_id, action_type=ActionType.ATTACH,
                resource_type=ResourceType.MEDIA, resource_id=self.media1.id,
                resource_label_snapshot="Birthday Cake & Candles Photo", operation="Attached photo to Grandma's 80th Birthday",
                correlation_id=cid
            )
        # 4. Create Memory Story
        if hasattr(self, 'memory1') and self.memory1:
            self.api.record_transaction_for_session(
                session_id=sess_id, family_context_id=fc_id, action_type=ActionType.CREATE,
                resource_type=ResourceType.MEMORY, resource_id=self.memory1.id,
                resource_label_snapshot="Grandma's Birthday Dinner", operation="Created narrative memory story with 3 attached photos",
                correlation_id=cid
            )
        # 5. Generate Celebration Album
        self.api.record_transaction_for_session(
            session_id=sess_id, family_context_id=fc_id, action_type=ActionType.GENERATE,
            resource_type=ResourceType.CELEBRATION_ARTIFACT, resource_id="artifact-album-1",
            resource_label_snapshot="Grandma 80th Birthday Album", operation="Generated Celebration Album derived artifact",
            correlation_id=cid
        )
        # 6. Share Link
        if hasattr(self, 'share_link1') and self.share_link1:
            self.api.record_transaction_for_session(
                session_id=sess_id, family_context_id=fc_id, action_type=ActionType.SHARE,
                resource_type=ResourceType.SHARE_LINK, resource_id=self.share_link1.token,
                resource_label_snapshot="Share Link for Birthday Event", operation="Generated tokenized public share link",
                correlation_id=cid
            )
        # 7. Revoke Share Link
        self.api.record_transaction_for_session(
            session_id=sess_id, family_context_id=fc_id, action_type=ActionType.REVOKE_SHARE,
            resource_type=ResourceType.SHARE_LINK, resource_id="revoked-token-sample",
            resource_label_snapshot="Share Link for Family Album", operation="Revoked share link by user request",
            correlation_id=cid
        )

    def __init__(self):
        self.api = None
        self.reset()

    def reset(self):
        self.api = FEMCApi()

        # 1. Create Initial People
        self.p_alice = self.api.identity.create_person("Alice Smith", birth_date=datetime.date(1990, 5, 15))
        self.p_bob = self.api.identity.create_person("Bob Smith", birth_date=datetime.date(1988, 10, 20))
        self.p_charlie = self.api.identity.create_person("Charlie Smith", birth_date=datetime.date(2015, 8, 10))

        # 2. Create Accounts
        self.acc_alice = self.api.identity.create_account("alice_smith", "alice@example.com", person_id=self.p_alice.id)
        self.acc_bob = self.api.identity.create_account("bob_smith", "bob@example.com", person_id=self.p_bob.id)
        self.acc_charlie = self.api.identity.create_account("charlie_smith", "charlie@example.com", person_id=self.p_charlie.id)

        # 3. Relationships
        self.api.identity.create_relationship(self.p_alice.id, self.p_bob.id, RelationshipType.PARTNER, confidence=Confidence.HIGH)
        self.api.identity.create_relationship(self.p_alice.id, self.p_charlie.id, RelationshipType.PARENT, confidence=Confidence.HIGH)
        self.api.identity.create_relationship(self.p_bob.id, self.p_charlie.id, RelationshipType.PARENT, confidence=Confidence.HIGH)

        # 4. Family Context
        self.family_context = self.api.identity.create_family_context(
            "Smith Family",
            member_ids=[self.acc_alice.id, self.acc_bob.id, self.acc_charlie.id],
            created_by_id=self.acc_alice.id,
        )

        # 5. Authenticated Sessions
        self.session_alice = self.api.create_session(self.acc_alice.id)
        self.session_bob = self.api.create_session(self.acc_bob.id)
        self.session_charlie = self.api.create_session(self.acc_charlie.id)

        self.account_sessions = {
            self.acc_alice.id: self.session_alice.session_id,
            self.acc_bob.id: self.session_bob.session_id,
            self.acc_charlie.id: self.session_charlie.session_id,
        }

        self.active_account_id = self.acc_alice.id
        self.session_id = self.session_alice.session_id

        # 6. Events (Deterministic Seed State with Privacy Boundaries)
        now = _utc_now()
        start_bday = now + datetime.timedelta(days=7)
        start_gen = now + datetime.timedelta(days=2)
        start_alice_priv = now + datetime.timedelta(days=3)
        start_bob_priv = now + datetime.timedelta(days=4)

        # Event 1: Birthday (FAMILY visible, targeted to Alice)
        self.event1 = self.api.create_event_for_session(
            session_id=self.session_alice.session_id,
            title="Alice's Birthday Celebration",
            description="Gathering at home for Alice's birthday dinner.",
            family_context_id=self.family_context.id,
            start_time=start_bday,
            end_time=start_bday + datetime.timedelta(hours=3),
            category=EventCategory.BIRTHDAY,
            target_person_ids=[self.p_alice.id],
            visibility=VisibilityLevel.FAMILY,
        )

        # Event 2: General Family Gathering (FAMILY visible)
        self.event2 = self.api.create_event_for_session(
            session_id=self.session_alice.session_id,
            title="Smith Family Weekend Dinner",
            description="Casual Sunday family dinner.",
            family_context_id=self.family_context.id,
            start_time=start_gen,
            end_time=start_gen + datetime.timedelta(hours=2),
            category=EventCategory.GENERAL,
            target_person_ids=[self.p_alice.id, self.p_bob.id],
            visibility=VisibilityLevel.FAMILY,
        )

        # Event 3: Alice's Private Event (PRIVATE visible, owner: Alice)
        self.event_alice_private = self.api.create_event_for_session(
            session_id=self.session_alice.session_id,
            title="Alice's Secret Surprise Notes",
            description="Private gift planning notes.",
            family_context_id=self.family_context.id,
            start_time=start_alice_priv,
            end_time=start_alice_priv + datetime.timedelta(hours=1),
            category=EventCategory.GENERAL,
            target_person_ids=[self.p_alice.id],
            visibility=VisibilityLevel.PRIVATE,
        )

        # Event 4: Bob's Private Event (PRIVATE visible, owner: Bob)
        self.event_bob_private = self.api.create_event_for_session(
            session_id=self.session_bob.session_id,
            title="Bob's Private Health Checkup",
            description="Confidential medical appointment.",
            family_context_id=self.family_context.id,
            start_time=start_bob_priv,
            end_time=start_bob_priv + datetime.timedelta(hours=1),
            category=EventCategory.GENERAL,
            target_person_ids=[self.p_bob.id],
            visibility=VisibilityLevel.PRIVATE,
        )

        # 7. Memory
        self.memory1 = self.api.create_memory_for_session(
            session_id=self.session_alice.session_id,
            event_id=self.event1.id,
            narrative="We blew out candles and shared old photo albums.",
            visibility=VisibilityLevel.FAMILY,
        )

        # 8. Media Items: Photo, Video & Audio Attachments
        self.media1 = self.api.create_media_item_for_session(
            session_id=self.session_alice.session_id,
            uri="https://images.unsplash.com/photo-1513151233558-d860c5398176",
            media_type=MediaType.PHOTO,
            caption="Alice blowing out birthday candles",
            family_context_id=self.family_context.id,
            event_id=self.event1.id,
            memory_id=self.memory1.id,
            visibility=VisibilityLevel.FAMILY,
        )

        self.media_video1 = self.api.create_media_item_for_session(
            session_id=self.session_alice.session_id,
            uri="https://www.w3schools.com/html/mov_bbb.mp4",
            media_type=MediaType.VIDEO,
            caption="Charlie playing at summer park",
            family_context_id=self.family_context.id,
            event_id=self.event2.id,
            memory_id=self.memory1.id,
            visibility=VisibilityLevel.FAMILY,
        )

        self.media_audio1 = self.api.create_media_item_for_session(
            session_id=self.session_alice.session_id,
            uri="https://www.w3schools.com/html/horse.mp3",
            media_type=MediaType.AUDIO,
            caption="Grandma singing birthday song voice memo",
            family_context_id=self.family_context.id,
            event_id=self.event1.id,
            memory_id=self.memory1.id,
            visibility=VisibilityLevel.FAMILY,
        )

        self.media2 = self.api.create_media_item_for_session(
            session_id=self.session_alice.session_id,
            uri="https://images.unsplash.com/photo-1529156069898-49953e39b3ac",
            media_type=MediaType.PHOTO,
            caption="Family group picture at dinner table",
            family_context_id=self.family_context.id,
            event_id=self.event2.id,
            visibility=VisibilityLevel.FAMILY,
        )

        # 9. Media Album
        self.album1 = self.api.create_media_album_for_session(
            session_id=self.session_alice.session_id,
            title="Summer Celebrations 2026",
            description="Best family photo highlights from summer events.",
            family_context_id=self.family_context.id,
            media_ids=[self.media1.id, self.media_video1.id, self.media_audio1.id, self.media2.id],
            visibility=VisibilityLevel.FAMILY,
        )

        # 10. Reminder
        self.reminder1 = self.api.configure_reminder_for_session(
            session_id=self.session_alice.session_id,
            event_id=self.event1.id,
            offset_minutes=60,
            reminder_type=ReminderType.EVENT_START,
        )

        # 11. Notification
        self.notif1 = self.api.create_notification_for_session(
            session_id=self.session_alice.session_id,
            recipient_id=self.acc_alice.id,
            notification_type=NotificationType.SYSTEM_ALERT,
            title="Welcome to FEMC",
            message="Your family event and memory space has been initialized.",
            family_context_id=self.family_context.id,
        )

        # 12. Celebration Artifacts
        self.celebration1 = self.api.build_celebration_artifact_for_event_for_session(
            session_id=self.session_alice.session_id,
            event_id=self.event1.id,
            attach_as_media=False,
        )

        self.celebration_album1 = self.api.build_celebration_album_artifact_for_session(
            session_id=self.session_alice.session_id,
            album_id=self.album1.id,
            attach_as_media=False,
        )

        # 13. Share Links
        self.share1 = self.api.create_share_link_for_session(
            session_id=self.session_alice.session_id,
            resource_type=ShareResourceType.EVENT,
            resource_id=self.event1.id,
            family_context_id=self.family_context.id,
            expires_in_minutes=1440,
        )

        self.share_media1 = self.api.create_share_link_for_session(
            session_id=self.session_alice.session_id,
            resource_type=ShareResourceType.MEDIA_ITEM,
            resource_id=self.media1.id,
            family_context_id=self.family_context.id,
            expires_in_minutes=1440,
        )

        # 14. Mayil AI Insight
        self.insight = self.api.analyze_family_insights_for_session(self.session_alice.session_id, self.family_context.id)

    def switch_session(self, account_id: str) -> str:
        if account_id in self.account_sessions:
            self.active_account_id = account_id
            self.session_id = self.account_sessions[account_id]
            return self.session_id
        raise ValueError("Account not found or session invalid")

    def onboard_member(
        self,
        name: str,
        email: str,
        relationship_type_str: str = "MEMBER",
        birth_date: Optional[datetime.date] = None,
    ):
        person = self.api.identity.create_person(name=name, birth_date=birth_date)
        username = email.split("@")[0].lower()
        account = self.api.identity.create_account(username=username, email=email, person_id=person.id)
        self.api.identity.add_member_to_context(self.family_context.id, account.id)
        session = self.api.create_session(account.id)
        self.account_sessions[account.id] = session.session_id

        active_account = self.api.canonical.get_account(self.active_account_id)
        if active_account and active_account.person_id:
            rel_map = {
                "spouse": RelationshipType.PARTNER,
                "partner": RelationshipType.PARTNER,
                "parent": RelationshipType.PARENT,
                "child": RelationshipType.CHILD,
                "sibling": RelationshipType.SIBLING,
                "member": RelationshipType.MEMBER,
            }
            rel_enum = rel_map.get(relationship_type_str.lower(), RelationshipType.MEMBER)
            self.api.identity.create_relationship(
                source_person_id=active_account.person_id,
                target_person_id=person.id,
                relationship_type=rel_enum,
                confidence=Confidence.HIGH,
            )

        return account, person, session


demo_state = DemoState()


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FEMC — Family Event & Memory Calendar</title>
    <style>
        :root {
            --bg-dark: #0f172a;
            --card-bg: #1e293b;
            --card-border: #334155;
            --accent: #38bdf8;
            --accent-glow: rgba(56, 189, 248, 0.15);
            --text-main: #f8fafc;
            --text-sub: #94a3b8;
            --pink: #f472b6;
            --purple: #c084fc;
            --amber: #fbbf24;
            --green: #4ade80;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        body { background-color: var(--bg-dark); color: var(--text-main); min-height: 100vh; display: flex; flex-direction: column; }

        header { background: #1e293b; border-bottom: 1px solid var(--card-border); padding: 0.85rem 1.5rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; }
        .logo { font-size: 1.25rem; font-weight: 700; color: var(--text-main); display: flex; align-items: center; gap: 0.5rem; }
        .logo-badge { background: var(--accent); color: #000; font-size: 0.75rem; padding: 0.15rem 0.5rem; border-radius: 4px; font-weight: 800; }

        .user-panel { display: flex; align-items: center; gap: 0.6rem; flex-wrap: wrap; }
        .perspective-box { display: flex; align-items: center; gap: 0.5rem; background: rgba(0,0,0,0.3); padding: 0.4rem 0.8rem; border-radius: 6px; border: 1px solid var(--card-border); }
        .perspective-label { font-size: 0.8rem; color: var(--text-sub); font-weight: 600; }
        .perspective-select { background: transparent; color: var(--text-main); border: none; font-size: 0.85rem; font-weight: 600; cursor: pointer; outline: none; }
        .perspective-select option { background: var(--card-bg); color: var(--text-main); }

        /* Reconstructed Coherent Application Ribbon */
        .femc-ribbon {
            background: #111827;
            border-bottom: 1px solid var(--card-border);
            padding: 0.5rem 1.25rem;
            display: flex;
            gap: 0.4rem;
            overflow-x: auto;
            align-items: center;
            scroll-behavior: smooth;
            -webkit-overflow-scrolling: touch;
        }

        .nav-link {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--text-sub);
            text-decoration: none;
            padding: 0.45rem 0.75rem;
            border-radius: 8px;
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.05);
            transition: all 0.2s ease-in-out;
            cursor: pointer;
            white-space: nowrap;
            user-select: none;
            outline: none;
        }

        .nav-link:hover {
            color: var(--text-main);
            background: rgba(56, 189, 248, 0.1);
            border-color: rgba(56, 189, 248, 0.3);
            transform: translateY(-1px);
        }

        .nav-link:focus-visible {
            box-shadow: 0 0 0 2px var(--accent);
        }

        .nav-link.active {
            color: var(--text-main);
            background: linear-gradient(135deg, rgba(56, 189, 248, 0.25) 0%, rgba(192, 132, 252, 0.2) 100%);
            border: 1px solid var(--accent);
            box-shadow: 0 0 10px rgba(56, 189, 248, 0.2);
        }

        .nav-link.highlight {
            background: rgba(244, 114, 182, 0.25);
            border-color: var(--pink);
            color: #fff;
            animation: pulseGlow 1.5s infinite alternate;
        }

        @keyframes pulseGlow {
            0% { box-shadow: 0 0 4px var(--pink); }
            100% { box-shadow: 0 0 14px var(--pink); }
        }

        .nav-icon {
            font-size: 1.1rem;
            line-height: 1;
        }

        .nav-text {
            display: flex;
            flex-direction: column;
            text-align: left;
        }

        .nav-title {
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            line-height: 1.2;
        }

        .nav-subtitle {
            font-size: 0.68rem;
            color: var(--text-sub);
            font-weight: 500;
            line-height: 1.1;
        }

        .nav-link.active .nav-subtitle {
            color: var(--accent);
        }

        main { flex: 1; padding: 1.75rem 1.5rem; max-width: 1240px; margin: 0 auto; width: 100%; }

        .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem; }
        .section-title { font-size: 1.4rem; font-weight: 700; color: var(--text-main); }
        .section-subtitle { font-size: 0.85rem; color: var(--text-sub); margin-top: 0.2rem; }

        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.25rem; margin-bottom: 1.5rem; }
        .card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 10px; padding: 1.25rem; position: relative; }
        .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
        .card-title { font-size: 1rem; font-weight: 600; color: var(--text-main); }

        .pill { font-size: 0.72rem; font-weight: 700; padding: 0.2rem 0.55rem; border-radius: 9999px; text-transform: uppercase; }
        .pill-birthday { background: rgba(244, 114, 182, 0.2); color: var(--pink); border: 1px solid var(--pink); }
        .pill-anniversary { background: rgba(192, 132, 252, 0.2); color: var(--purple); border: 1px solid var(--purple); }
        .pill-milestone { background: rgba(251, 191, 36, 0.2); color: var(--amber); border: 1px solid var(--amber); }
        .pill-general { background: rgba(56, 189, 248, 0.2); color: var(--accent); border: 1px solid var(--accent); }
        .pill-health { background: rgba(74, 222, 128, 0.2); color: var(--green); border: 1px solid var(--green); }
        .pill-private { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #f87171; }

        .item-list { display: flex; flex-direction: column; gap: 0.75rem; }
        .item-row { background: rgba(15, 23, 42, 0.6); padding: 0.75rem; border-radius: 6px; border: 1px solid rgba(255, 255, 255, 0.05); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem; }
        .item-main { font-size: 0.9rem; font-weight: 600; color: var(--text-main); }
        .item-sub { font-size: 0.8rem; color: var(--text-sub); margin-top: 0.2rem; }

        /* Media Gallery & Player Grid */
        .media-gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 1rem; margin-top: 0.75rem; }
        .media-card { background: #0f172a; border-radius: 8px; overflow: hidden; border: 1px solid var(--card-border); text-align: left; display: flex; flex-direction: column; justify-content: space-between; }
        .media-card img { width: 100%; height: 150px; object-fit: cover; display: block; }
        .audio-waveform-box { background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%); padding: 1.25rem 1rem; height: 150px; display: flex; flex-direction: column; justify-content: center; align-items: center; border-bottom: 1px solid var(--card-border); }
        .audio-waveform-visual { display: flex; gap: 3px; align-items: center; margin-bottom: 0.75rem; height: 30px; }
        .waveform-bar { width: 4px; background: var(--pink); border-radius: 2px; animation: wavePulse 1.2s infinite ease-in-out alternate; }
        @keyframes wavePulse { 0% { height: 6px; } 100% { height: 28px; } }
        .media-caption { font-size: 0.85rem; font-weight: 600; color: var(--text-main); padding: 0.6rem 0.6rem 0.2rem 0.6rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .media-meta { font-size: 0.75rem; color: var(--text-sub); padding: 0 0.6rem 0.5rem 0.6rem; }
        .media-actions { display: flex; gap: 0.3rem; padding: 0.5rem 0.6rem; background: rgba(0,0,0,0.25); border-top: 1px solid rgba(255,255,255,0.05); flex-wrap: wrap; }

        .btn { background: var(--accent); color: #0f172a; border: none; padding: 0.45rem 0.9rem; border-radius: 6px; font-weight: 600; font-size: 0.82rem; cursor: pointer; transition: opacity 0.2s; display: inline-flex; align-items: center; gap: 0.35rem; }
        .btn:hover { opacity: 0.9; }
        .btn-outline { background: transparent; color: var(--text-main); border: 1px solid var(--card-border); }
        .btn-outline:hover { background: rgba(255,255,255,0.05); }
        .btn-pink { background: var(--pink); color: #000; }
        .btn-sm { padding: 0.25rem 0.5rem; font-size: 0.75rem; }

        /* Modal Styles */
        .modal-overlay { position: fixed; top:0; left:0; right:0; bottom:0; background: rgba(0,0,0,0.75); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 1rem; }
        .modal-card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 12px; width: 100%; max-width: 640px; padding: 1.5rem; max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5); }
        .form-group { margin-bottom: 1rem; }
        .form-label { display: block; font-size: 0.85rem; font-weight: 600; color: var(--text-sub); margin-bottom: 0.4rem; }
        .form-input, .form-select { width: 100%; background: #0f172a; border: 1px solid var(--card-border); color: var(--text-main); padding: 0.6rem; border-radius: 6px; font-size: 0.9rem; outline: none; }
        .checkbox-group { display: flex; flex-direction: column; gap: 0.4rem; background: #0f172a; padding: 0.6rem; border-radius: 6px; border: 1px solid var(--card-border); }
        .checkbox-item { display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; color: var(--text-main); }

        /* Drag & Drop Dropzone */
        .dropzone { border: 2px dashed var(--accent); background: rgba(56, 189, 248, 0.05); border-radius: 8px; padding: 2rem 1rem; text-align: center; cursor: pointer; transition: background 0.2s; margin-bottom: 1rem; }
        .dropzone.hover { background: rgba(56, 189, 248, 0.15); }
        .dropzone-title { font-size: 1rem; font-weight: 700; color: var(--accent); margin-bottom: 0.25rem; }
        .dropzone-sub { font-size: 0.8rem; color: var(--text-sub); }

        .capture-tabs { display: flex; gap: 0.5rem; overflow-x: auto; margin-bottom: 1rem; border-bottom: 1px solid var(--card-border); padding-bottom: 0.5rem; }
        .capture-tab { padding: 0.5rem 0.8rem; border-radius: 6px; font-size: 0.8rem; font-weight: 600; cursor: pointer; background: transparent; color: var(--text-sub); border: 1px solid transparent; white-space: nowrap; }
        .capture-tab.active { background: var(--accent); color: #0f172a; }

        /* Guided Tour Subtitles Bar */
        .subtitle-bar { background: rgba(15, 23, 42, 0.9); border: 1px solid var(--accent); padding: 0.75rem 1rem; border-radius: 8px; font-size: 0.9rem; color: var(--text-main); margin-top: 1rem; display: flex; align-items: center; gap: 0.6rem; }

        /* Animated Mayil Character Avatar */
        .mayil-avatar { width: 70px; height: 70px; margin: 0 auto 0.75rem auto; position: relative; transition: all 0.3s ease; }
        .mayil-svg { width: 100%; height: 100%; display: block; filter: drop-shadow(0 4px 10px rgba(56, 189, 248, 0.3)); }
        .mayil-avatar.idle { transform: scale(1); }
        .mayil-avatar.speaking { animation: mayilSpeak 0.8s infinite alternate; }
        .mayil-avatar.listening { animation: mayilPulse 1.2s infinite ease-in-out; }
        .mayil-avatar.thinking { animation: mayilSpin 2s infinite linear; }
        .mayil-avatar.happy { animation: mayilBounce 0.6s infinite alternate; }
        @keyframes mayilSpeak { 0% { transform: scale(1); } 100% { transform: scale(1.08); filter: drop-shadow(0 0 12px #38bdf8); } }
        @keyframes mayilPulse { 0% { transform: scale(1); filter: drop-shadow(0 0 4px #f472b6); } 50% { transform: scale(1.1); filter: drop-shadow(0 0 16px #f472b6); } 100% { transform: scale(1); filter: drop-shadow(0 0 4px #f472b6); } }
        @keyframes mayilSpin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        @keyframes mayilBounce { 0% { transform: translateY(0); } 100% { transform: translateY(-8px); } }

        @media (max-width: 900px) {
            .nav-subtitle { display: none; }
            .femc-ribbon { padding: 0.4rem 0.75rem; }
            .nav-link { padding: 0.4rem 0.6rem; }
        }

        .practice-world-banner {
            background: linear-gradient(135deg, #4c1d95 0%, #1e1b4b 100%);
            border: 2px solid var(--pink);
            box-shadow: 0 0 20px rgba(244, 114, 182, 0.4);
            color: #ffffff;
            padding: 0.75rem 1.25rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .target-glow {
            border: 2px solid var(--pink) !important;
            box-shadow: 0 0 15px var(--pink), 0 0 25px rgba(244, 114, 182, 0.4) !important;
            animation: pulseGlow 1.2s infinite alternate !important;
            position: relative;
            z-index: 100;
        }

        .mayil-guide-banner {
            background: linear-gradient(135deg, #1e1b4b 0%, #311b92 100%);
            border: 1px solid var(--purple);
            border-radius: 12px;
            padding: 1rem 1.25rem;
            margin-bottom: 1.25rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            box-shadow: 0 4px 20px rgba(192, 132, 252, 0.25);
        }
        .mayil-avatar-glow {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--accent), var(--pink));
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            box-shadow: 0 0 12px var(--pink);
        }
    </style></head>
<body>
    <header>
        <div class="logo">
            FEMC <span class="logo-badge">v2.3-C Complete</span>
        </div>
        <div class="user-panel">
            <button class="btn btn-pink" onclick="openAskMayilPanel()">🤖 Ask Mayil</button>
            <button class="btn btn-outline" onclick="openAnimatedJourneyModal()">🎬 Mayil's Journey</button>
            <div class="perspective-box">
                <span class="perspective-label">👁️ Viewing as:</span>
                <select id="perspective-select" class="perspective-select" onchange="switchPerspective(this.value)">
                    <!-- Dynamically Loaded -->
                </select>
            </div>
            <button class="btn btn-outline" onclick="resetDemoState()">🔄 Reset State</button>
        </div>
    </header>

    <nav class="femc-ribbon" aria-label="Main Navigation">
        <a id="nav-home" class="nav-link active" tabindex="0" onclick="loadView('home', event)" onkeydown="if(event.key==='Enter'||event.key===' ')loadView('home', event)">
            <span class="nav-icon">🏠</span>
            <div class="nav-text">
                <span class="nav-title">HOME</span>
                <span class="nav-subtitle">Overview</span>
            </div>
        </a>
        <a id="nav-family" class="nav-link" tabindex="0" onclick="loadView('family', event)" onkeydown="if(event.key==='Enter'||event.key===' ')loadView('family', event)">
            <span class="nav-icon">👨‍👩‍👧‍👦</span>
            <div class="nav-text">
                <span class="nav-title">FAMILY</span>
                <span class="nav-subtitle">Our Family & Group</span>
            </div>
        </a>
        <a id="nav-calendar" class="nav-link" tabindex="0" onclick="loadView('calendar', event)" onkeydown="if(event.key==='Enter'||event.key===' ')loadView('calendar', event)">
            <span class="nav-icon">📅</span>
            <div class="nav-text">
                <span class="nav-title">CALENDAR</span>
                <span class="nav-subtitle">Events & Plans</span>
            </div>
        </a>
        <a id="nav-memories" class="nav-link" tabindex="0" onclick="loadView('memories', event)" onkeydown="if(event.key==='Enter'||event.key===' ')loadView('memories', event)">
            <span class="nav-icon">📖</span>
            <div class="nav-text">
                <span class="nav-title">MEMORIES & MEDIA</span>
                <span class="nav-subtitle">Photos, Videos, Audio</span>
            </div>
        </a>
        <a id="nav-celebrations" class="nav-link" tabindex="0" onclick="loadView('celebrations', event)" onkeydown="if(event.key==='Enter'||event.key===' ')loadView('celebrations', event)">
            <span class="nav-icon">🎉</span>
            <div class="nav-text">
                <span class="nav-title">CELEBRATIONS</span>
                <span class="nav-subtitle">Studio & Albums</span>
            </div>
        </a>
        <a id="nav-reminders" class="nav-link" tabindex="0" onclick="loadView('reminders', event)" onkeydown="if(event.key==='Enter'||event.key===' ')loadView('reminders', event)">
            <span class="nav-icon">🔔</span>
            <div class="nav-text">
                <span class="nav-title">REMINDERS</span>
                <span class="nav-subtitle">Alerts & Tasks</span>
            </div>
        </a>
        <a id="nav-mayil" class="nav-link" tabindex="0" onclick="loadView('mayil', event)" onkeydown="if(event.key==='Enter'||event.key===' ')loadView('mayil', event)">
            <span class="nav-icon">🧠</span>
            <div class="nav-text">
                <span class="nav-title">MAYIL AI</span>
                <span class="nav-subtitle">Smart Assistant</span>
            </div>
        </a>
        <a id="nav-guardian" class="nav-link" tabindex="0" onclick="loadView('guardian', event)" onkeydown="if(event.key==='Enter'||event.key===' ')loadView('guardian', event)">
            <span class="nav-icon">🛡️</span>
            <div class="nav-text">
                <span class="nav-title">GUARDIAN</span>
                <span class="nav-subtitle">Privacy & Safety</span>
            </div>
        </a>
        <a id="nav-sharing" class="nav-link" tabindex="0" onclick="loadView('sharing', event)" onkeydown="if(event.key==='Enter'||event.key===' ')loadView('sharing', event)">
            <span class="nav-icon">🔗</span>
            <div class="nav-text">
                <span class="nav-title">SHARING</span>
                <span class="nav-subtitle">Share & Connect</span>
            </div>
        </a>
        <a id="nav-history" class="nav-link" tabindex="0" onclick="loadView('history', event)" onkeydown="if(event.key==='Enter'||event.key===' ')loadView('history', event)">
            <span class="nav-icon">🕘</span>
            <div class="nav-text">
                <span class="nav-title">ACTIVITY</span>
                <span class="nav-subtitle">Audit & History</span>
            </div>
        </a>
        <a id="nav-settings"  class="nav-link" tabindex="0" onclick="loadView('settings', event)" onkeydown="if(event.key==='Enter'||event.key===' ')loadView('settings', event)">
            <span class="nav-icon">⚙️</span>
            <div class="nav-text">
                <span class="nav-title">SETTINGS / DATA</span>
                <span class="nav-subtitle">Export & More</span>
            </div>
        </a>
    </nav>

    <main id="content-area">
        <!-- Dynamic Content -->
    </main>

    <!-- Modal Container -->
    <div id="modal-container" style="display:none;"></div>

    <script>
        let currentView = 'home';
        let membersData = [];
        let activeAccountId = '';
        let activeMediaStream = null;
        let mediaRecorder = null;
        let recordedChunks = [];

        // ==========================================
        // COMMON BROWSER INFRASTRUCTURE & LIFECYCLE
        // ==========================================
        async function fetchAPI(endpoint, options = {}) {
            try {
                const res = await fetch(endpoint, options);
                if (!res.ok) throw new Error(`HTTP error ${res.status}`);
                return await res.json();
            } catch (err) {
                console.error("API Error:", err);
                return {};
            }
        }

        function stopMediaStream() {
            if (activeMediaStream) {
                try {
                    activeMediaStream.getTracks().forEach(t => t.stop());
                } catch (e) {}
                activeMediaStream = null;
            }
            if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                try {
                    mediaRecorder.stop();
                } catch (e) {}
            }
        }

        function closeModal() {
            stopNarration();
            stopMediaStream();
            const container = document.getElementById('modal-container');
            if (container) {
                container.style.display = 'none';
                container.innerHTML = '';
            }
            document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('highlight'));
            const navEl = document.getElementById(`nav-${currentView}`);
            if (navEl) navEl.classList.add('active');
        }

        function setActiveNav(viewName) {
            currentView = viewName || 'home';
            document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active', 'highlight'));
            const navEl = document.getElementById(`nav-${currentView}`);
            if (navEl) navEl.classList.add('active');
        }

        async function initMembers() {
            const data = await fetchAPI('/api/members');
            membersData = data.members || [];
            activeAccountId = data.active_account_id || '';

            const select = document.getElementById('perspective-select');
            if (select && membersData.length > 0) {
                select.innerHTML = membersData.map(m => `
                    <option value="${m.account_id}" ${m.is_active ? 'selected' : ''}>
                        ${m.name} (${m.email})
                    </option>
                `).join('');
            }
        }

        async function switchPerspective(accId) {
            if (!accId) return;
            await fetchAPI('/api/session/switch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ account_id: accId })
            });
            await initMembers();
            await loadView(currentView);
        }

        async function resetDemoState() {
            closeModal();
            await fetchAPI('/api/reset', { method: 'POST' });
            await initMembers();
            await loadView(currentView);
        }

        async function loadView(viewName, evt) {
            if (evt) evt.preventDefault();
            setActiveNav(viewName);
            const content = document.getElementById('content-area');
            if (!content) return;
            content.innerHTML = `
                <div style="text-align:center; padding:4rem 2rem; color:var(--text-sub);">
                    <div style="font-size:2rem; margin-bottom:0.75rem; animation: pulseGlow 1s infinite alternate;">⏳</div>
                    <div style="font-size:1.1rem; font-weight:600; color:var(--text-main);">Loading family data...</div>
                    <div style="font-size:0.85rem; color:var(--text-sub); margin-top:0.25rem;">Fetching authorized views for ${viewName.toUpperCase()}</div>
                </div>
            `;

            try {
                if (viewName === 'home') await renderHome(content);
                else if (viewName === 'family') await renderFamily(content);
                else if (viewName === 'calendar') await renderCalendar(content);
                else if (viewName === 'memories') await renderMemories(content);
                else if (viewName === 'celebrations') await renderCelebrations(content);
                else if (viewName === 'reminders') await renderReminders(content);
                else if (viewName === 'mayil') await renderMayil(content);
                else if (viewName === 'guardian') await renderGuardian(content);
                else if (viewName === 'sharing') await renderSharing(content);
                else if (viewName === 'history') await renderHistory(content);
            else if (viewName === 'settings') await renderSettings(content);
                else await renderHome(content);
            } catch (err) {
                console.error("View rendering error:", err);
                content.innerHTML = `
                    <div class="card" style="text-align:center; padding:3rem 2rem; border-color:#f87171; max-width:600px; margin:2rem auto;">
                        <div style="font-size:2.5rem; margin-bottom:0.5rem;">⚠️</div>
                        <div class="card-title" style="color:#f87171; font-size:1.25rem; margin-bottom:0.5rem;">Unable to load screen data</div>
                        <div style="font-size:0.88rem; color:var(--text-sub); margin-bottom:1.5rem; line-height:1.5;">
                            An unexpected error occurred while loading contents for <strong>${viewName.toUpperCase()}</strong>.<br/>
                            <span style="font-family:monospace; font-size:0.78rem; color:#f87171;">${err.message || err}</span>
                        </div>
                        <button class="btn" onclick="loadView('${viewName}')">🔄 Retry Loading ${viewName.toUpperCase()}</button>
                    </div>
                `;
            }
        }

        // ==========================================
        // VIEW RENDERERS (10 CORE PILLARS)
        // ==========================================

        async function openResourceHistoryModal(resType, resId) {
            const modal = document.getElementById('modal-container');
            if (!modal) return;
            modal.style.display = 'flex';
            modal.innerHTML = `
                <div class="modal-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; border-bottom:1px solid var(--card-border); padding-bottom:0.5rem;">
                        <h2 style="font-size:1.1rem; color:var(--accent);">🕘 Resource History & Audit</h2>
                        <button class="btn btn-outline btn-sm" onclick="closeModal()">✕</button>
                    </div>
                    <div style="text-align:center; padding:2rem; color:var(--text-sub);">Loading resource history...</div>
                </div>
            `;
            try {
                const data = await fetchAPI(`/api/resource_history?type=${resType}&id=${resId}`);
                modal.innerHTML = `
                    <div class="modal-card">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; border-bottom:1px solid var(--card-border); padding-bottom:0.5rem;">
                            <h2 style="font-size:1.1rem; color:var(--accent);">🕘 History: ${data.resource_type.toUpperCase()} '${data.resource_id}'</h2>
                            <button class="btn btn-outline btn-sm" onclick="closeModal()">✕</button>
                        </div>
                        <div style="background:#0f172a; padding:0.75rem; border-radius:8px; border:1px solid var(--accent); margin-bottom:1rem; font-size:0.85rem;">
                            <div style="font-weight:700; color:var(--text-main); margin-bottom:0.25rem;">📌 Current Canonical State</div>
                            <div style="color:var(--text-sub);">${data.current_state}</div>
                        </div>
                        <div style="background:rgba(244, 114, 182, 0.1); padding:0.75rem; border-radius:8px; border:1px solid var(--pink); margin-bottom:1rem; font-size:0.85rem;">
                            <div style="font-weight:700; color:var(--pink); margin-bottom:0.25rem;">🤖 Mayil Interpretation</div>
                            <div style="color:var(--text-main);">${data.mayil_interpretation}</div>
                        </div>
                        <div class="item-list">
                            <div style="font-size:0.85rem; font-weight:700; color:var(--text-sub); margin-bottom:0.4rem;">📜 Recorded Activity Facts</div>
                            ${data.recorded_facts.length > 0 ? data.recorded_facts.map(f => `
                                <div class="item-row" style="font-size:0.82rem;">
                                    <div>${f}</div>
                                </div>
                            `).join('') : '<div class="item-sub">No history recorded for this resource.</div>'}
                        </div>
                    </div>
                `;
            } catch (err) {
                modal.innerHTML = `<div class="modal-card"><div class="item-sub">Unable to load resource history.</div><button class="btn" onclick="closeModal()">Close</button></div>`;
            }
        }

        async function renderHistory(container) {
            const data = await fetchAPI('/api/history');
            const txs = data.transactions || [];

            container.innerHTML = `
                <div class="page-header">
                    <div>
                        <h1 class="section-title">🕘 Activity & Transaction History</h1>
                        <div class="section-subtitle">Immutable Audit Memory & Reconstructable Product Journeys</div>
                    </div>
                    <div>
                        <button class="btn btn-pink" onclick="openAskMayilPanel(); setTimeout(()=> { document.getElementById('mayil-query-input').value='What happened today?'; }, 300);">🤖 Ask Mayil About History</button>
                    </div>
                </div>

                <!-- Visual Activity Chain Diagram -->
                <div class="card" style="margin-bottom:1.5rem; background: linear-gradient(135deg, #111827 0%, #1e293b 100%); border: 1px solid var(--accent);">
                    <div class="card-header">
                        <div class="card-title" style="color:var(--accent);">✨ Visual Memory Journey Timeline</div>
                        <span class="pill pill-general">Correlation Chain</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem; padding:0.5rem 0; text-align:center;">
                        <div style="background:#0f172a; padding:0.6rem 0.8rem; border-radius:8px; border:1px solid var(--card-border);">
                            <div style="font-size:1.2rem;">👤</div>
                            <div style="font-size:0.75rem; font-weight:700; color:var(--text-main);">1. Add Member</div>
                        </div>
                        <div style="color:var(--text-sub);">➔</div>
                        <div style="background:#0f172a; padding:0.6rem 0.8rem; border-radius:8px; border:1px solid var(--card-border);">
                            <div style="font-size:1.2rem;">📅</div>
                            <div style="font-size:0.75rem; font-weight:700; color:var(--text-main);">2. Schedule Event</div>
                        </div>
                        <div style="color:var(--text-sub);">➔</div>
                        <div style="background:#0f172a; padding:0.6rem 0.8rem; border-radius:8px; border:1px solid var(--card-border);">
                            <div style="font-size:1.2rem;">📸</div>
                            <div style="font-size:0.75rem; font-weight:700; color:var(--text-main);">3. Attach Photos</div>
                        </div>
                        <div style="color:var(--text-sub);">➔</div>
                        <div style="background:#0f172a; padding:0.6rem 0.8rem; border-radius:8px; border:1px solid var(--card-border);">
                            <div style="font-size:1.2rem;">📖</div>
                            <div style="font-size:0.75rem; font-weight:700; color:var(--text-main);">4. Write Story</div>
                        </div>
                        <div style="color:var(--text-sub);">➔</div>
                        <div style="background:#0f172a; padding:0.6rem 0.8rem; border-radius:8px; border:1px solid var(--card-border);">
                            <div style="font-size:1.2rem;">🎉</div>
                            <div style="font-size:0.75rem; font-weight:700; color:var(--text-main);">5. Celebration Album</div>
                        </div>
                        <div style="color:var(--text-sub);">➔</div>
                        <div style="background:#0f172a; padding:0.6rem 0.8rem; border-radius:8px; border:1px solid var(--card-border);">
                            <div style="font-size:1.2rem;">🔗</div>
                            <div style="font-size:0.75rem; font-weight:700; color:var(--text-main);">6. Share & Revoke</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <div class="card-title">📜 Authorized Activity Feed</div>
                        <span class="pill pill-milestone">${txs.length} Recorded Transactions</span>
                    </div>
                    <div class="item-list">
                        ${txs.length > 0 ? txs.map(t => `
                            <div class="item-row">
                                <div style="flex:1;">
                                    <div style="display:flex; gap:0.5rem; align-items:center; margin-bottom:0.25rem;">
                                        <span class="pill pill-${t.action_type.includes('delete') || t.action_type.includes('revoke') ? 'private' : 'general'}">${t.action_type.toUpperCase()}</span>
                                        <span style="font-size:0.85rem; font-weight:700; color:var(--text-main);">${t.resource_label_snapshot}</span>
                                        <span style="font-size:0.72rem; color:var(--text-sub);">• ${t.timestamp}</span>
                                    </div>
                                    <div style="font-size:0.85rem; color:var(--text-sub);">${t.operation}</div>
                                    <div style="font-size:0.75rem; color:var(--text-sub); margin-top:0.2rem;">
                                        Actor: <strong>${t.actor_account_id}</strong> | Visibility: <strong>${t.visibility}</strong> | Type: <strong>${t.resource_type}</strong>
                                    </div>
                                </div>
                                <div>
                                    <button class="btn btn-sm btn-outline" onclick="openResourceHistoryModal('${t.resource_type}', '${t.resource_id}')">🕘 Inspect History</button>
                                </div>
                            </div>
                        `).join('') : '<div class="item-sub">No transaction history recorded yet.</div>'}
                    </div>
                </div>
            `;
        }


        async function renderHome(container) {
            const data = await fetchAPI('/api/dashboard');
            const summary = data.summary || {};
            const entries = data.entries || [];

            const eventsList = entries.filter(e => {
                const type = e.item_type || e.entry_type;
                return type === 'upcoming_event' || type === 'recurring_event';
            });
            const remindersList = entries.filter(e => {
                const type = e.item_type || e.entry_type;
                return type === 'reminder_due' || type === 'system_alert';
            });
            const memoriesList = entries.filter(e => {
                const type = e.item_type || e.entry_type;
                return type === 'recent_memory';
            });
            const celebrationsList = entries.filter(e => {
                const type = e.item_type || e.entry_type;
                return type === 'celebration_highlight';
            });

            container.innerHTML = `
                <div class="page-header">
                    <div>
                        <h1 class="section-title">🏠 Family Dashboard</h1>
                        <div class="section-subtitle">Smith Family Overview & Active Highlights</div>
                    </div>
                    <div>
                        <button class="btn" onclick="openCreateEventModal()">➕ Schedule Event</button>
                    </div>
                </div>

                <div class="grid">
                    <div class="card">
                        <div class="card-header">
                            <div class="card-title">📅 Upcoming Family Events</div>
                            <span class="pill pill-general">${eventsList.length} Scheduled</span>
                        </div>
                        <div class="item-list">
                            ${eventsList.length > 0 ? eventsList.map(e => `
                                <div class="item-row">
                                    <div>
                                        <div class="item-main">${e.title}</div>
                                        <div class="item-sub">${e.date_or_time || e.date || ''} ${e.description ? `• ${e.description}` : ''}</div>
                                    </div>
                                    <span class="pill pill-${(e.category || 'general').toLowerCase()}">${e.category || 'EVENT'}</span>
                                </div>
                            `).join('') : '<div class="item-sub">No upcoming events scheduled.</div>'}
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <div class="card-title">🔔 Reminders & Alerts</div>
                            <span class="pill pill-birthday">${remindersList.length} Active</span>
                        </div>
                        <div class="item-list">
                            ${remindersList.length > 0 ? remindersList.map(e => `
                                <div class="item-row">
                                    <div>
                                        <div class="item-main">${e.title}</div>
                                        <div class="item-sub">${e.description || 'Action required'}</div>
                                    </div>
                                    <button class="btn btn-sm btn-outline" onclick="loadView('reminders')">View</button>
                                </div>
                            `).join('') : '<div class="item-sub">All reminders up to date!</div>'}
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <div class="card-title">📖 Recent Family Memories</div>
                            <span class="pill pill-milestone">${memoriesList.length} Memories</span>
                        </div>
                        <div class="item-list">
                            ${memoriesList.length > 0 ? memoriesList.map(e => `
                                <div class="item-row">
                                    <div>
                                        <div class="item-main">${e.title}</div>
                                        <div class="item-sub">${e.description || ''}</div>
                                    </div>
                                    <button class="btn btn-sm btn-outline" onclick="loadView('memories')">Timeline</button>
                                </div>
                            `).join('') : '<div class="item-sub">No memories captured yet.</div>'}
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <div class="card-title">🎉 Celebration Highlights</div>
                            <span class="pill pill-anniversary">${celebrationsList.length} Cards</span>
                        </div>
                        <div class="item-list">
                            ${celebrationsList.length > 0 ? celebrationsList.map(e => `
                                <div class="item-row">
                                    <div>
                                        <div class="item-main">${e.title}</div>
                                        <div class="item-sub">${e.description || ''}</div>
                                    </div>
                                    <button class="btn btn-sm btn-pink" onclick="loadView('celebrations')">Cards</button>
                                </div>
                            `).join('') : '<div class="item-sub">No celebration highlights yet.</div>'}
                        </div>
                    </div>
                </div>

                <div class="card" style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border: 1px solid var(--accent);">
                    <div class="card-header">
                        <div class="card-title" style="color:var(--accent);">🤖 Mayil AI Assistant & Guided Journey</div>
                        <div style="display:flex; gap:0.5rem;">
                            <button class="btn btn-pink btn-sm" onclick="openAskMayilPanel()">🤖 Ask Mayil</button>
                            <button class="btn btn-outline btn-sm" onclick="openAnimatedJourneyModal()">🎬 Mayil's Journey</button>
                        </div>
                    </div>
                    <div style="font-size:0.85rem; color:var(--text-sub); line-height:1.5;">
                        Mayil AI continuously analyzes family events, memories, and reminders to offer context insights and proposal actions. Click <strong>Mayil's Journey</strong> for a guided visual tour of all 10 FEMC product pillars.
                    </div>
                </div>
            `;
        }

        async function renderFamily(container) {
            const data = await fetchAPI('/api/family');
            const topology = data.topology || {};
            const members = topology.members || [];
            const relationships = topology.relationships || [];

            container.innerHTML = `
                <div class="page-header">
                    <div>
                        <h1 class="section-title">👨‍👩‍👧‍👦 Family Tree & Identity</h1>
                        <div class="section-subtitle">Smith Family Members, Topology, and Relationships</div>
                    </div>
                    <div>
                        <button class="btn" onclick="openOnboardModal()">➕ Add Family Member</button>
                    </div>
                </div>

                <div class="grid">
                    ${members.map(m => `
                        <div class="card">
                            <div class="card-header">
                                <div class="card-title">${m.name}</div>
                                ${m.account_id === activeAccountId ? '<span class="pill pill-health">Active User</span>' : '<span class="pill pill-general">Member</span>'}
                            </div>
                            <div style="font-size:0.85rem; color:var(--text-sub); margin-bottom:0.75rem;">
                                ✉️ Email: <strong>${m.email || 'None'}</strong><br/>
                                🎂 Birth Date: <strong>${m.birth_date || 'Not specified'}</strong>
                            </div>
                        </div>
                    `).join('')}
                </div>

                <div class="card" style="margin-top:1.5rem;">
                    <div class="card-header">
                        <div class="card-title">🌳 Relationship Topology Edges</div>
                        <span class="pill pill-general">${relationships.length} Connections</span>
                    </div>
                    <div class="item-list">
                        ${relationships.length > 0 ? relationships.map(r => `
                            <div class="item-row">
                                <div>
                                    <div class="item-main">${r.source_person_name} ➔ ${r.target_person_name}</div>
                                    <div class="item-sub">Type: ${r.relationship_type.toUpperCase()} | Confidence: ${r.confidence}</div>
                                </div>
                                <span class="pill pill-anniversary">${r.relationship_type}</span>
                            </div>
                        `).join('') : '<div class="item-sub">No relationship edges defined yet.</div>'}
                    </div>
                </div>
            `;
        }

        async function renderCalendar(container) {
            const data = await fetchAPI('/api/events');
            const calendar = data.calendar || [];

            container.innerHTML = `
                <div class="page-header">
                    <div>
                        <h1 class="section-title">📅 Family Calendar & Agenda</h1>
                        <div class="section-subtitle">Authorized Family Events and Milestones</div>
                    </div>
                    <div>
                        <button class="btn" onclick="openCreateEventModal()">📅 Schedule Event</button>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Family Events Agenda</div>
                        <span class="pill pill-general">${calendar.length} Events</span>
                    </div>
                    <div class="item-list">
                        ${calendar.length > 0 ? calendar.map(c => `
                            <div class="item-row">
                                <div>
                                    <div class="item-main">${c.title}</div>
                                    <div class="item-sub">${c.date} • Visibility: ${c.visibility} ${c.description ? `• ${c.description}` : ''}</div>
                                </div>
                                <div style="display:flex; gap:0.5rem; align-items:center;">
                                    <span class="pill pill-${(c.category || 'general').toLowerCase()}">${c.category || 'EVENT'}</span>
                                    <button class="btn btn-sm btn-outline" onclick="openShareModal('EVENT', '${c.event_id}')">🔗 Share</button>
                                </div>
                            </div>
                        `).join('') : '<div class="item-sub">No calendar events scheduled.</div>'}
                    </div>
                </div>
            `;
        }

        async function renderMemories(container) {
            const timelineData = await fetchAPI('/api/timeline');
            const mediaData = await fetchAPI('/api/media');

            const timeline = timelineData.timeline || [];
            const mediaItems = mediaData.items || [];
            const mediaAlbums = mediaData.albums || [];

            let mediaGalleryHTML = mediaItems.map(m => {
                let playerHTML = '';
                if (m.media_type === 'video') {
                    playerHTML = `<video controls src="${m.uri}" style="width:100%; height:150px; object-fit:cover; display:block; background:#000;"></video>`;
                } else if (m.media_type === 'audio') {
                    playerHTML = `
                        <div class="audio-waveform-box">
                            <div style="font-size:0.8rem; font-weight:700; color:var(--pink); margin-bottom:0.4rem;">🎙️ Voice Memo</div>
                            <div class="audio-waveform-visual">
                                <div class="waveform-bar" style="animation-delay: 0.1s;"></div>
                                <div class="waveform-bar" style="animation-delay: 0.3s;"></div>
                                <div class="waveform-bar" style="animation-delay: 0.2s;"></div>
                                <div class="waveform-bar" style="animation-delay: 0.4s;"></div>
                                <div class="waveform-bar" style="animation-delay: 0.15s;"></div>
                                <div class="waveform-bar" style="animation-delay: 0.35s;"></div>
                                <div class="waveform-bar" style="animation-delay: 0.25s;"></div>
                            </div>
                            <audio controls src="${m.uri}" style="width:100%; max-width:200px; height:32px;"></audio>
                        </div>
                    `;
                } else {
                    playerHTML = `<img src="${m.uri}" alt="${m.caption || 'Photo'}" />`;
                }

                const fn = generate_media_download_filename(m.caption, m.media_type);

                return `
                    <div class="media-card">
                        ${playerHTML}
                        <div class="media-caption">${m.caption || 'Family Moment'}</div>
                        <div class="media-meta">Visibility: <strong>${m.visibility}</strong></div>
                        <div class="media-actions">
                            <a href="${m.uri}" download="${fn}" class="btn btn-sm btn-outline" style="text-decoration:none;" target="_blank">⬇ Download</a>
                            <button class="btn btn-sm btn-outline" onclick="openShareMediaModal('${m.id}', '${(m.caption || 'Family Media').replace(/'/g, "\'")}', '${m.uri}', '${m.media_type}', '${m.visibility}')">🔗 Share</button>
                            <button class="btn btn-sm btn-pink" onclick="openGenerateArtifactModal();">✨ Celebration</button>
                        </div>
                    </div>
                `;
            }).join('');

            container.innerHTML = `
                <div class="page-header">
                    <div>
                        <h1 class="section-title">📖 Memories & Media</h1>
                        <div class="section-subtitle">Capture the moments that matter. Photos, videos, and voice memos.</div>
                    </div>
                    <div style="display:flex; gap:0.4rem; flex-wrap:wrap;">
                        <button class="btn btn-pink" onclick="openMediaCaptureCenter()">📸 Capture Now</button>
                        <button class="btn btn-outline" onclick="openMediaCaptureCenter(); setTimeout(()=>switchCaptureTab('audio'), 200);">🎙️ Record Voice</button>
                        <button class="btn btn-outline" onclick="openMediaCaptureCenter(); setTimeout(()=>switchCaptureTab('video'), 200);">🎥 Record Video</button>
                        <button class="btn btn-outline" onclick="openMediaCaptureCenter(); setTimeout(()=>switchCaptureTab('file'), 200);">📁 Upload / Drop Files</button>
                        <button class="btn btn-outline" onclick="createMemoryPrompt()">✏️ Write Story</button>
                    </div>
                </div>

                <div class="card" style="margin-bottom:1.5rem;">
                    <div class="card-header">
                        <div class="card-title">📖 Memory Story Wall</div>
                        <span class="pill pill-milestone">${timeline.length} Story Entries</span>
                    </div>
                    <div class="item-list">
                        ${timeline.length > 0 ? timeline.map(t => `
                            <div class="item-row" style="align-items:flex-start;">
                                <div style="flex:1;">
                                    <div class="item-main" style="font-size:1rem; color:var(--text-main); margin-bottom:0.25rem;">
                                        ${t.title || 'Family Memory Story'}
                                    </div>
                                    <div style="font-size:0.88rem; color:var(--text-sub); line-height:1.5; margin-bottom:0.5rem;">
                                        "${t.narrative || t.description || 'A cherished moment captured in the family memory timeline.'}"
                                    </div>
                                    <div class="item-sub">
                                        Captured by <strong>${t.author_name || 'Family Member'}</strong> • Visibility: <span class="pill pill-general" style="font-size:0.65rem;">FAMILY VISIBLE</span>
                                    </div>
                                </div>
                                <div style="display:flex; gap:0.4rem; flex-wrap:wrap; align-items:center;">
                                    <button class="btn btn-sm btn-outline" onclick="openMediaCaptureCenter('${t.id || ''}')">📸 Add Media</button>
                                    <button class="btn btn-sm btn-outline" onclick="openShareModal('MEMORY', '${t.id || ''}')">🔗 Share Memory</button>
                                    <button class="btn btn-sm btn-pink" onclick="openGenerateArtifactModal('card')">✨ Create Celebration</button>
                                </div>
                            </div>
                        `).join('') : '<div class="item-sub">No memories recorded yet. Click Write Story or Capture Now!</div>'}
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <div class="card-title">🎥 Family Media Gallery (${mediaItems.length} Items, ${mediaAlbums.length} Albums)</div>
                        <button class="btn btn-sm btn-pink" onclick="openMediaCaptureCenter()">📸 Capture / Upload</button>
                    </div>
                    <div class="media-gallery">
                        ${mediaGalleryHTML || '<div class="item-sub" style="grid-column: 1/-1;">No media items captured yet. Click Capture Now to record a photo, video, or voice memo!</div>'}
                    </div>
                </div>
            `;
        }

        async function renderCelebrations(container) {
            const data = await fetchAPI('/api/celebrations');
            const artifacts = data.artifacts || [];

            container.innerHTML = `
                <div class="page-header">
                    <div>
                        <h1 class="section-title">🎉 Celebration Studio</h1>
                        <div class="section-subtitle">Turn meaningful moments into something worth remembering.</div>
                    </div>
                    <div style="display:flex; gap:0.4rem; flex-wrap:wrap;">
                        <button class="btn btn-pink" onclick="openGenerateArtifactModal('card')">✨ Generate Celebration Card</button>
                        <button class="btn btn-outline" onclick="openGenerateArtifactModal('album')">📚 Build Celebration Album</button>
                        <button class="btn btn-outline" onclick="openGenerateArtifactModal('person')">👤 Person Highlight</button>
                    </div>
                </div>

                <div class="grid">
                    ${artifacts.length > 0 ? artifacts.map(a => `
                        <div class="card" style="border-top: 4px solid var(--pink); display:flex; flex-direction:column; justify-content:space-between;">
                            <div>
                                <div class="card-header">
                                    <div class="card-title">${a.title}</div>
                                    <span class="pill pill-anniversary">${a.artifact_type}</span>
                                </div>
                                <div style="font-size:0.85rem; color:var(--text-sub); margin-bottom:1rem; line-height:1.5;">
                                    ${a.subtitle ? `<div style="font-weight:700; color:var(--text-main); margin-bottom:0.4rem;">${a.subtitle}</div>` : ''}
                                    <div style="background:#0f172a; padding:0.75rem; border-radius:6px; border:1px solid rgba(255,255,255,0.05); color:var(--text-main); font-style:italic;">
                                        "${a.rendered_text || 'Celebration Artifact Derived Content'}"
                                    </div>
                                </div>
                            </div>
                            <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid rgba(255,255,255,0.05); padding-top:0.75rem; margin-top:0.5rem; flex-wrap:wrap; gap:0.4rem;">
                                <span style="font-size:0.75rem; color:var(--text-sub);">Visibility: <strong>${a.visibility}</strong></span>
                                <div style="display:flex; gap:0.4rem;">
                                    <button class="btn btn-sm btn-outline" onclick="loadView('memories')">📖 View Source Memory</button>
                                    <button class="btn btn-sm btn-pink" onclick="openShareModal('MEDIA_ITEM', '${a.id}')">🔗 Share Artifact</button>
                                </div>
                            </div>
                        </div>
                    `).join('') : '<div class="card" style="grid-column: 1/-1;"><div class="item-sub">No celebration artifacts generated yet. Click Generate Celebration Card above!</div></div>'}
                </div>
            `;
        }

        async function renderReminders(container) {
            const data = await fetchAPI('/api/reminders');
            const notifications = data.notifications || [];
            const triggered = data.triggered || [];

            container.innerHTML = `
                <div class="page-header">
                    <div>
                        <h1 class="section-title">🔔 Reminders & Notifications</h1>
                        <div class="section-subtitle">Event Start Alerts and System Messages</div>
                    </div>
                </div>

                <div class="card" style="margin-bottom:1.5rem;">
                    <div class="card-header">
                        <div class="card-title">Active Notifications</div>
                        <span class="pill pill-birthday">${notifications.length} Notifications</span>
                    </div>
                    <div class="item-list">
                        ${notifications.length > 0 ? notifications.map(n => `
                            <div class="item-row">
                                <div>
                                    <div class="item-main">${n.title}</div>
                                    <div class="item-sub">${n.message}</div>
                                </div>
                                <div style="display:flex; gap:0.5rem; align-items:center;">
                                    ${n.status === 'read' ? '<span class="pill pill-health">READ</span>' : `<button class="btn btn-sm btn-pink" onclick="markNotificationRead('${n.id}')">Mark Read</button>`}
                                </div>
                            </div>
                        `).join('') : '<div class="item-sub">No active notifications.</div>'}
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Triggered Due Reminders</div>
                        <span class="pill pill-general">${triggered.length} Evaluated</span>
                    </div>
                    <div class="item-list">
                        ${triggered.length > 0 ? triggered.map(t => `
                            <div class="item-row">
                                <div>
                                    <div class="item-main">${t.title}</div>
                                    <div class="item-sub">${t.message}</div>
                                </div>
                                <span class="pill pill-amber">DUE</span>
                            </div>
                        `).join('') : '<div class="item-sub">No due reminders triggered at this time.</div>'}
                    </div>
                </div>
            `;
        }

        async function renderMayil(container) {
            const data = await fetchAPI('/api/mayil');
            const insight = data.insight || {};
            const proposals = data.proposals || [];

            container.innerHTML = `
                <div class="page-header">
                    <div>
                        <h1 class="section-title">🧠 Mayil AI Intelligence</h1>
                        <div class="section-subtitle">Context Insights and Action Proposals</div>
                    </div>
                    <div style="display:flex; gap:0.5rem;">
                        <button class="btn btn-pink" onclick="openAskMayilPanel()">🤖 Ask Mayil</button>
                        <button class="btn btn-outline" onclick="openAnimatedJourneyModal()">🎬 Mayil's Journey</button>
                    </div>
                </div>

                <div class="card" style="margin-bottom:1.5rem; border-left:4px solid var(--accent);">
                    <div class="card-header">
                        <div class="card-title" style="color:var(--accent);">💡 Mayil Noticed (Context Analysis)</div>
                        <span class="pill pill-general">ACTIVE INSIGHT</span>
                    </div>
                    <div style="font-size:0.9rem; color:var(--text-main); line-height:1.5;">
                        ${insight.summary || 'Mayil analyzed your family events, memories, and places to provide intelligent context awareness.'}
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Proposals & Recommendations</div>
                        <span class="pill pill-milestone">${proposals.length} Proposals</span>
                    </div>
                    <div class="item-list">
                        ${proposals.length > 0 ? proposals.map(p => `
                            <div class="item-row">
                                <div>
                                    <div class="item-main">${p.title}</div>
                                    <div class="item-sub">${p.description}</div>
                                </div>
                                ${p.status === 'approved' ? '<span class="pill pill-health">APPROVED</span>' : `<button class="btn btn-sm" onclick="approveProposal('${p.id}')">Approve Proposal</button>`}
                            </div>
                        `).join('') : '<div class="item-sub">No pending proposals from Mayil at this time.</div>'}
                    </div>
                </div>
            `;
        }

        async function renderGuardian(container) {
            const data = await fetchAPI('/api/guardian');
            const audit = data.audit || {};
            const proposals = data.repair_proposals || [];
            const isHealthy = audit.is_valid !== false;

            container.innerHTML = `
                <div class="page-header">
                    <div>
                        <h1 class="section-title">🛡️ VEL Guardian Governance</h1>
                        <div class="section-subtitle">Real-Time Data Integrity, Privacy Audits, and Controlled Repair</div>
                    </div>
                </div>

                <div class="card" style="margin-bottom:1.5rem; border-left:4px solid ${isHealthy ? 'var(--green)' : '#f87171'};">
                    <div class="card-header">
                        <div class="card-title">System Health & Data Integrity Audit</div>
                        <span class="pill ${isHealthy ? 'pill-health' : 'pill-private'}">${isHealthy ? 'HEALTHY' : 'ANOMALY DETECTED'}</span>
                    </div>
                    <div style="font-size:0.9rem; color:var(--text-sub);">
                        Guardian continuously verifies privacy rules, projection consistency, and reference integrity across canonical data and derived caches.
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Repair Proposals</div>
                        <span class="pill pill-general">${proposals.length} Proposals</span>
                    </div>
                    <div class="item-list">
                        ${proposals.length > 0 ? proposals.map(p => `
                            <div class="item-row">
                                <div>
                                    <div class="item-main">${p.description || p.anomaly_type || 'Data Repair Proposal'}</div>
                                    <div class="item-sub">Classification: ${p.repair_classification || 'DERIVED_REPAIR'}</div>
                                </div>
                                ${p.status === 'executed' ? '<span class="pill pill-health">REPAIRED</span>' : `<button class="btn btn-sm btn-pink" onclick="executeRepair('${p.id}')">Execute Repair</button>`}
                            </div>
                        `).join('') : '<div class="item-sub">No data integrity anomalies detected. Your family data is 100% healthy!</div>'}
                    </div>
                </div>
            `;
        }

        async function renderSharing(container) {
            const data = await fetchAPI('/api/sharing');
            const links = data.share_links || [];

            container.innerHTML = `
                <div class="page-header">
                    <div>
                        <h1 class="section-title">🔗 Secure Sharing Tokens</h1>
                        <div class="section-subtitle">Tokenized Links, Revocation, and Access Controls</div>
                    </div>
                    <div>
                        <button class="btn" onclick="openShareModal('EVENT', 'demo_event')">🔗 Create Share Link</button>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Active Share Tokens</div>
                        <span class="pill pill-general">${links.length} Links</span>
                    </div>
                    <div class="item-list">
                        ${links.length > 0 ? links.map(l => {
                            const url = `${window.location.origin}/share?token=${l.token}`;
                            const isRev = l.is_revoked;
                            return `
                                <div class="item-row">
                                    <div>
                                        <div class="item-main">Resource: ${l.resource_type} (${l.resource_id})</div>
                                        <div class="item-sub">Token: <code>${l.token}</code> | Expires: ${l.expires_at || 'Never'}</div>
                                    </div>
                                    <div style="display:flex; gap:0.5rem; align-items:center;">
                                        ${isRev ? '<span class="pill pill-private">REVOKED</span>' : `
                                            <button class="btn btn-sm btn-outline" onclick="copyShareUrl('${url}')">📋 Copy</button>
                                            <button class="btn btn-sm btn-pink" onclick="revokeShareLink('${l.token}')">Revoke</button>
                                        `}
                                    </div>
                                </div>
                            `;
                        }).join('') : '<div class="item-sub">No share links created yet.</div>'}
                    </div>
                </div>
            `;
        }

        async function renderSettings(container) {
            const data = await fetchAPI('/api/export');
            const exportData = data.export || {};
            const validation = data.validation || {};
            const jsonStr = JSON.stringify(exportData, null, 2);

            container.innerHTML = `
                <div class="page-header">
                    <div>
                        <h1 class="section-title">⚙️ Data Portability & Settings</h1>
                        <div class="section-subtitle">Complete Family Data Export & Schema Validation</div>
                    </div>
                </div>

                <div class="card" style="margin-bottom:1.5rem;">
                    <div class="card-header">
                        <div class="card-title">Schema Validation Status</div>
                        <span class="pill ${validation.is_valid ? 'pill-health' : 'pill-private'}">${validation.is_valid ? 'VALIDATED 1.0' : 'INVALID'}</span>
                    </div>
                    <div style="font-size:0.85rem; color:var(--text-sub);">
                        Export data structure validated against canonical schema version 1.0. 100% compatible for backup and offline storage.
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Family Data JSON Export</div>
                        <button class="btn btn-sm btn-outline" onclick="copyShareUrl('${encodeURIComponent(jsonStr)}')">📋 Copy JSON</button>
                    </div>
                    <pre style="max-height:300px; overflow-y:auto;">${jsonStr}</pre>
                </div>
            `;
        }


        // ==========================================
        // WORKSTREAM V2.3-C: MAYIL INTERACTIVE VISUAL ENGINE & MODALS
        // ==========================================
        let mayilAvatarState = 'idle'; // idle, speaking, listening, thinking, happy, helping
        let conversationHistory = [];
        let isAutoPlayJourney = false;
        let autoPlayTimer = null;
        let currentJourneyScene = 0;
        let tourLanguage = 'en';

        const FEMC_INTENTS = {
            OPEN_HOME: {
                keywords: ['home', 'dashboard', 'overview', 'முகப்பு', 'ஹோம்', 'होम', 'मुख्य'],
                view: 'home',
                response: { en: "Opening your Home Overview.", ta: "உங்கள் முகப்பு திரையகத்தைத் திறக்கிறேன்.", hi: "आपका होम डैशबोर्ड खोल रहे हैं।" }
            },
            OPEN_FAMILY: {
                keywords: ['family', 'members', 'people', 'குடும்பம்', 'உறுப்பினர்கள்', 'परिवार', 'सदस्य'],
                view: 'family',
                response: { en: "Opening your Family Members & Relationships.", ta: "உங்கள் குடும்ப உறுப்பினர்கள் மற்றும் உறவுகளைத் திறக்கிறேன்.", hi: "आपके परिवार के सदस्य खोल रहे हैं।" }
            },
            ADD_MEMBER: {
                keywords: ['add member', 'onboard', 'new person', 'சேர்', 'உறுப்பினர் சேர்', 'सदस्य जोड़ें', 'नया सदस्य'],
                view: 'family',
                actionFn: 'openOnboardModal()',
                requiresConfirmation: true,
                response: { en: "Let's onboard a new family member.", ta: "புதிய குடும்ப உறுப்பினரைச் சேர்ப்போம்.", hi: "नया परिवार सदस्य जोड़ते हैं।" }
            },
            OPEN_CALENDAR: {
                keywords: ['calendar', 'events', 'agenda', 'நாட்காட்டி', 'நிகழ்வுகள்', 'कैलेंडर', 'कार्यक्रम'],
                view: 'calendar',
                response: { en: "Opening your Family Calendar & Agenda.", ta: "உங்கள் குடும்ப நாட்காட்டியைத் திறக்கிறேன்.", hi: "आपका परिवार कैलेंडर खोल रहे हैं।" }
            },
            CREATE_EVENT: {
                keywords: ['create event', 'schedule event', 'new birthday', 'நிகழ்வு', 'நிகழ்வை உருவாக்கு', 'कार्यक्रम बनाएं', 'नया कार्यक्रम'],
                view: 'calendar',
                actionFn: 'openCreateEventModal()',
                requiresConfirmation: true,
                response: { en: "Let's schedule a new family event.", ta: "புதிய குடும்ப நிகழ்வைத் திட்டமிடுவோம்.", hi: "नया परिवार कार्यक्रम निर्धारित करते हैं।" }
            },
            OPEN_MEMORIES: {
                keywords: ['memories', 'stories', 'timeline', 'நினைவுகள்', 'கதைகள்', 'यादें', 'कहानियां'],
                view: 'memories',
                response: { en: "Opening your Family Memories & Timeline.", ta: "உங்கள் குடும்ப நினைவுகளைத் திறக்கிறேன்.", hi: "आपकी पारिवारिक यादें खोल रहे हैं।" }
            },
            RECORD_MEMORY: {
                keywords: ['record memory', 'add story', 'write memory', 'நினைவை பதிவு', 'பதிவு', 'याद दर्ज करें', 'कहानी दर्ज'],
                view: 'memories',
                actionFn: 'createMemoryPrompt()',
                requiresConfirmation: true,
                response: { en: "Let me open the memory recorder for you.", ta: "நினைவுப் பதிவியைத் திறக்கிறேன்.", hi: "याद दर्ज करने का विंडो खोल रहे हैं।" }
            },
            OPEN_MEDIA: {
                keywords: ['media', 'photos', 'videos', 'audio', 'ஊடகம்', 'படங்கள்', 'வீடியோ', 'मीडिया', 'फोटो'],
                view: 'memories',
                response: { en: "Opening your A/V Media Gallery.", ta: "உங்கள் ஊடகக் கேலரியைத் திறக்கிறேன்.", hi: "आपकी मीडिया गैलरी खोल रहे हैं।" }
            },
            CAPTURE_PHOTO: {
                keywords: ['take photo', 'camera', 'snap', 'புகைப்படம்', 'கேமரா', 'फोटो खींचें', 'कैमरा'],
                view: 'memories',
                actionFn: 'openMediaCaptureCenter()',
                requiresConfirmation: true,
                response: { en: "Opening the Camera Photo capture mode.", ta: "கேமரா புகைப்படப் பயன்முறையைத் திறக்கிறேன்.", hi: "कैमरा फोटो मोड खोल रहे हैं।" }
            },
            RECORD_AUDIO: {
                keywords: ['voice memo', 'record voice', 'audio song', 'குரல் பதிவு', 'பாட்டு', 'आवाज दर्ज', 'वॉइस रिकॉर्ड'],
                view: 'memories',
                actionFn: 'openMediaCaptureCenter()',
                requiresConfirmation: true,
                response: { en: "Opening the Voice Memo audio recorder.", ta: "குரல் பதிவுப் பயன்முறையைத் திறக்கிறேன்.", hi: "वॉइस रिकॉर्डर खोल रहे हैं।" }
            },
            RECORD_VIDEO: {
                keywords: ['record video', 'video clip', 'வீடியோ பதிவு', 'வீடியோ துண்டு', 'वीडियो रिकॉर्ड', 'वीडियो क्लिप'],
                view: 'memories',
                actionFn: 'openMediaCaptureCenter()',
                requiresConfirmation: true,
                response: { en: "Opening the Video Clip recorder.", ta: "வீடியோ பதிவுப் பயன்முறையைத் திறக்கிறேன்.", hi: "वीडियो रिकॉर्डर खोल रहे हैं।" }
            },
            OPEN_CELEBRATIONS: {
                keywords: ['celebrations', 'studio', 'cards', 'கொண்டாட்டம்', 'அட்டைகள்', 'उत्सव', 'कार्ड'],
                view: 'celebrations',
                response: { en: "Opening Celebration Studio.", ta: "கொண்டாட்ட அரங்கத்தைத் திறக்கிறேன்.", hi: "उत्सव स्टूडियो खोल रहे हैं।" }
            },
            CREATE_CELEBRATION: {
                keywords: ['create card', 'generate card', 'celebration artifact', 'அட்டை உருவாக்கு', 'कार्ड बनाएं', 'ग्रीटिंग कार्ड'],
                view: 'celebrations',
                actionFn: 'openGenerateArtifactModal()',
                requiresConfirmation: true,
                response: { en: "Let's generate a celebration card.", ta: "கொண்டாட்ட அட்டையை உருவாக்குவோம்.", hi: "उत्सव कार्ड बनाते हैं।" }
            },
            OPEN_REMINDERS: {
                keywords: ['reminders', 'notifications', 'alerts', 'நினைவூட்டல்கள்', 'அறிவிப்புகள்', 'रिमाइंडर्स', 'सूचनाएं'],
                view: 'reminders',
                response: { en: "Opening Reminders & Notifications.", ta: "நினைவூட்டல்களைத் திறக்கிறேன்.", hi: "रिमाइंडर्स और सूचनाएं खोल रहे हैं।" }
            },
            OPEN_SHARING: {
                keywords: ['sharing', 'share links', 'tokens', 'பகிர்வு', 'இணைப்புகள்', 'शेयरिंग', 'शेयर लिंक'],
                view: 'sharing',
                response: { en: "Opening Secure Sharing Tokens.", ta: "பாதுகாப்பான பகிர்வைத் திறக்கிறேன்.", hi: "सुरक्षित शेयरिंग खोल रहे हैं।" }
            },
            CREATE_SHARE_LINK: {
                keywords: ['create share', 'generate link', 'share token', 'இணைப்பு உருவாக்கு', 'लिंक बनाएं', 'शेयर लिंक बनाएं'],
                view: 'sharing',
                actionFn: "openShareModal('EVENT', 'demo_event')",
                requiresConfirmation: true,
                response: { en: "Let's create a secure share link.", ta: "பாதுகாப்பான பகிர்வு இணைப்பை உருவாக்குவோம்.", hi: "सुरक्षित शेयर लिंक बनाते हैं।" }
            },
            OPEN_MAYIL: {
                keywords: ['mayil', 'ai', 'insights', 'மயில்', 'ஆலோசனைகள்', 'मयिल', 'सुझाव'],
                view: 'mayil',
                response: { en: "Opening Mayil AI Insights.", ta: "மயில் AI ஆலோசனைகளைத் திறக்கிறேன்.", hi: "मयिल एआई सुझाव खोल रहे हैं।" }
            },
            OPEN_GUARDIAN: {
                keywords: ['guardian', 'audit', 'integrity', 'காவலர்', 'பாதுகாப்பு', 'गार्डियन', 'सुरक्षा जांच'],
                view: 'guardian',
                response: { en: "Opening VEL Guardian Integrity Audit.", ta: "காப்பாளர் தணிக்கையைத் திறக்கிறேன்.", hi: "गार्डियन सुरक्षा जांच खोल रहे हैं।" }
            },
            OPEN_SETTINGS: {
                keywords: ['settings', 'export', 'data portability', 'தரவு', 'ஏற்றுமதி', 'सेटिंग्स', 'डेटा एक्सपोर्ट'],
                view: 'settings',
                response: { en: "Opening Settings & Data Portability.", ta: "தரவு அமைப்புகளைத் திறக்கிறேன்.", hi: "डेटा एक्सपोर्ट खोल रहे हैं।" }
            },
            START_GUIDED_TOUR: {
                keywords: ['tour', 'guided', 'journey', 'help', 'பயணம்', 'வழிபாடு', 'सफर', 'गाइड'],
                actionFn: 'openAnimatedJourneyModal()',
                response: { en: "Starting Mayil's Animated FEMC Journey.", ta: "மயிலின் அனிமேஷன் பயணத்தைத் தொடங்குகிறேன்.", hi: "मयिल का एनिमेटेड सफर शुरू कर रहे हैं।" }
            }
        };

        const JOURNEY_SCENES = [
            { id: 1, title: "🌅 Welcome Home", nav: "home", narration: { en: "Welcome to the Smith Family space! Let's explore your family overview together.", ta: "ஸ்மித் குடும்ப இடத்திற்கு வரவேற்கிறோம்! உங்கள் குடும்ப மேலோட்டத்தை ஒன்றாக ஆராய்வோம்.", hi: "स्मिथ परिवार स्थान में आपका स्वागत है! आइए मिलकर आपका होम डैशबोर्ड देखें।" }, caption: "🌅 SCENE 1: Welcome to your family home overview.", actionFn: "loadView('home')" },
            { id: 2, title: "👨‍👩‍👧 Meet the Family", nav: "family", narration: { en: "Meet Alice, Bob, and Charlie Smith! Here you manage all family identities.", ta: "ஆலிஸ், பாப் மற்றும் சார்லியைச் சந்திக்கவும்! இங்கே குடும்ப நபர்களை நிர்வகிக்கலாம்.", hi: "एलिस, बॉब और चार्ली से मिलें! यहाँ सभी परिवार के सदस्यों को प्रबंधित किया जाता है।" }, caption: "👨‍👩‍👧 SCENE 2: Inspect family accounts and person identities.", actionFn: "openOnboardModal()" },
            { id: 3, title: "🌳 Family Relationships", nav: "family", narration: { en: "Discover relationship connections — partners, parents, and children.", ta: "குடும்ப உறவு இணைப்புகளைக் கண்டறியவும் — கணவன், மனைவி, பெற்றோர் மற்றும் குழந்தைகள்.", hi: "पारिवारिक संबंधों को समझें — जीवनसाथी, माता-पिता और बच्चे।" }, caption: "🌳 SCENE 3: Relationship graph edges connect family members.", actionFn: "loadView('family')" },
            { id: 4, title: "📅 Family Calendar", nav: "calendar", narration: { en: "Keep everyone on the same page with your family event agenda.", ta: "குடும்ப நிகழ்வுகள் அனைத்தும் ஒரே நாட்காட்டியில் காணப்படும்.", hi: "परिवार कैलेंडर में सभी कार्यक्रमों को एक साथ देखें।" }, caption: "📅 SCENE 4: Authorized family agenda and occurrences.", actionFn: "openCreateEventModal()" },
            { id: 5, title: "🎂 Birthday Event", nav: "calendar", narration: { en: "Celebrate Alice's birthday dinner with family visibility controls.", ta: "ஆலிஸின் பிறந்தநாள் விழாவை குடும்ப உறுப்பினர்களுடன் கொண்டாடுங்கள்.", hi: "एलिस का जन्मदिन समारोह आयोजित करें।" }, caption: "🎂 SCENE 5: Birthdays and milestones with privacy controls.", actionFn: "openCreateEventModal()" },
            { id: 6, title: "📖 Family Memory", nav: "memories", narration: { en: "Record the stories your family wants to remember forever.", ta: "உங்கள் குடும்பம் எப்போதும் நினைவில் வைத்திருக்க விரும்பும் கதைகளைப் பதிவு செய்யுங்கள்.", hi: "उन कहानियों को दर्ज करें जिन्हें परिवार याद रखना चाहता है।" }, caption: "📖 SCENE 6: Narrative memory stories attached to events.", actionFn: "createMemoryPrompt()" },
            { id: 7, title: "📷 Capture Photo", nav: "memories", narration: { en: "Snap a live family photo directly from your camera.", ta: "உங்கள் கேமரா மூலம் நேரடி புகைப்படங்களை எடுங்கள்.", hi: "कैमरे से सीधे पारिवारिक तस्वीर खींचें।" }, caption: "📷 SCENE 7: Browser-native camera snapshot capture.", actionFn: "openMediaCaptureCenter()" },
            { id: 8, title: "🎙️ Record Voice", nav: "memories", narration: { en: "Record Grandma's voice or a birthday song audio memo.", ta: "பாட்டியின் குரல் அல்லது பிறந்தநாள் பாடலைப் பதிவு செய்யுங்கள்.", hi: "दादी की आवाज या जन्मदिन का गाना रिकॉर्ड करें।" }, caption: "🎙️ SCENE 8: Voice memo recorder for audio memories.", actionFn: "openMediaCaptureCenter()" },
            { id: 9, title: "🎥 Record Video", nav: "memories", narration: { en: "Record live video clips of your family moments.", ta: "குடும்பத் தருணங்களை நேரடி வீடியோக்களாகப் பதிவு செய்யுங்கள்.", hi: "पारिवारिक पलों के वीडियो रिकॉर्ड करें।" }, caption: "🎥 SCENE 9: Browser video recorder for live video clips.", actionFn: "openMediaCaptureCenter()" },
            { id: 10, title: "📁 Add Existing Media", nav: "memories", narration: { en: "Upload existing photos and videos or drag & drop them anytime.", ta: "ஏற்கனவே உள்ள படங்களையும் வீடியோக்களையும் பதிவேற்றம் செய்யுங்கள்.", hi: "मौजूदा फोटो और वीडियो अपलोड या ड्रैग एंड ड्रॉप करें।" }, caption: "📁 SCENE 10: File upload and drag & drop dropzone.", actionFn: "openMediaCaptureCenter()" },
            { id: 11, title: "🎉 Celebration Studio", nav: "celebrations", narration: { en: "Turn family moments into celebration cards, digests, and photo albums.", ta: "குடும்பத் தருணங்களை அழகான கொண்டாட்ட அட்டைகளாக மாற்றுங்கள்.", hi: "पारिवारिक पलों को ग्रीटिंग कार्ड्स और एल्बम में बदलें।" }, caption: "🎉 SCENE 11: Celebration Studio artifact derivation.", actionFn: "openGenerateArtifactModal()" },
            { id: 12, title: "🔔 Reminders", nav: "reminders", narration: { en: "Receive timely reminders for upcoming birthdays and important events.", ta: "முக்கியமான பிறந்தநாட்களுக்கான நினைவூட்டல்களைப் பெறுங்கள்.", hi: "आगामी जन्मदिनों के रिमाइंडर्स प्राप्त करें।" }, caption: "🔔 SCENE 12: Event reminders and system notifications.", actionFn: "loadView('reminders')" },
            { id: 13, title: "🔗 Sharing", nav: "sharing", narration: { en: "Share family moments with secure tokenized share links, WhatsApp, or device share.", ta: "பாதுகாப்பான பகிர்வு இணைப்புகள் மூலம் நினைவுகளைப் பகிருங்கள்.", hi: "सुरक्षित शेयर लिंक्स द्वारा यादें साझा करें।" }, caption: "🔗 SCENE 13: Controlled share links with revocation support.", actionFn: "openShareModal('EVENT', 'demo_event')" },
            { id: 14, title: "🤖 Mayil AI", nav: "mayil", narration: { en: "Mayil observes authorized activity and offers helpful family suggestions.", ta: "மயில் உங்கள் குடும்பத்தைக் கவனித்து பயனுள்ள ஆலோசனைகளை வழங்குகிறது.", hi: "मयिल गतिविधियों को देखता है और उपयोगी सुझाव देता है।" }, caption: "🤖 SCENE 14: Read-only activity insights and proposals.", actionFn: "loadView('mayil')" },
            { id: 15, title: "🛡️ Guardian", nav: "guardian", narration: { en: "Guardian checks the integrity and privacy of your family data.", ta: "காப்பாளர் உங்கள் குடும்பத் தரவின் பாதுகாப்பை உறுதிசெய்கிறார்.", hi: "गार्डियन डेटा की सुरक्षा और गोपनीयता की जांच करता है।" }, caption: "🛡️ SCENE 15: Autonomous integrity auditing and repairs.", actionFn: "loadView('guardian')" },
            { id: 16, title: "💾 Data Ownership", nav: "settings", narration: { en: "Your family data belongs to you. Inspect and export your data anytime.", ta: "உங்கள் குடும்பத் தரவு உங்களுக்கே சொந்தமானது. எப்போதும் ஏற்றுமதி செய்யலாம்.", hi: "आपका डेटा आपका है। कभी भी एक्सपोर्ट कर सकते हैं।" }, caption: "💾 SCENE 16: Complete data portability with JSON exports.", actionFn: "loadView('settings')" },
            { id: 17, title: "❤️ Family Story Complete", nav: "home", narration: { en: "You have explored the complete FEMC ecosystem! Enjoy preserving your family memories.", ta: "FEMC-இன் முழுமையான அமைப்பை ஆராய்ந்து முடித்துவிட்டீர்கள்! உங்கள் குடும்ப நினைவுகளைப் பாதுகாத்து மகிழுங்கள்.", hi: "आपने FEMC के पूरे सफर को देख लिया है! अपनी यादों को सहेजने का आनंद लें।" }, caption: "❤️ SCENE 17: Complete Family Event & Memory Calendar ecosystem.", actionFn: "loadView('home')" }
        ];

        function renderMayilAvatarSVG(state = 'idle') {
            return `
                <div class="mayil-avatar ${state}">
                    <svg viewBox="0 0 100 100" class="mayil-svg">
                        <circle cx="50" cy="50" r="42" fill="url(#mayilGrad)" stroke="var(--accent)" stroke-width="3" />
                        <path d="M 30 40 Q 35 30 40 40" stroke="#fff" stroke-width="4" fill="none" />
                        <path d="M 60 40 Q 65 30 70 40" stroke="#fff" stroke-width="4" fill="none" />
                        <circle cx="35" cy="38" r="4" fill="#38bdf8" />
                        <circle cx="65" cy="38" r="4" fill="#38bdf8" />
                        <path d="${state === 'happy' ? 'M 32 60 Q 50 80 68 60' : 'M 38 62 Q 50 72 62 62'}" stroke="#fff" stroke-width="4" fill="none" />
                        <polygon points="50,12 44,24 56,24" fill="#fbbf24" />
                        <defs>
                            <linearGradient id="mayilGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="#0284c7" />
                                <stop offset="100%" stop-color="#38bdf8" />
                            </linearGradient>
                        </defs>
                    </svg>
                </div>
            `;
        }

        function resolveFEMCIntent(queryText) {
            const q = (queryText || '').toLowerCase().trim();
            if (!q) return null;

            for (const [intentKey, intentData] of Object.entries(FEMC_INTENTS)) {
                for (const kw of intentData.keywords) {
                    if (q.includes(kw.toLowerCase())) {
                        return { key: intentKey, ...intentData };
                    }
                }
            }
            return null;
        }

        function openAskMayilPanel() {
            const container = document.getElementById('modal-container');
            let historyHTML = conversationHistory.map(h => `
                <div style="margin-bottom:0.8rem;">
                    <div style="font-size:0.8rem; color:var(--text-sub); font-weight:700;">You: ${h.query}</div>
                    <div style="background:#0f172a; border-left:3px solid var(--accent); padding:0.6rem; border-radius:4px; font-size:0.85rem; color:var(--text-main); margin-top:0.25rem;">
                        <strong>🤖 Mayil:</strong> ${h.response}
                        ${h.actionFn ? `<div style="margin-top:0.4rem;"><button class="btn btn-sm" onclick="executeTourAction('${h.actionFn.replace(/'/g, "\\'")}')">👉 Open / Try Now</button></div>` : ''}
                    </div>
                </div>
            `).join('');

            container.innerHTML = `
                <div class="modal-overlay">
                    <div class="modal-card">
                        <div class="card-header">
                            <div class="card-title">🤖 Ask Mayil — Interactive Guide</div>
                            <button class="btn btn-outline" style="padding:0.2rem 0.5rem;" onclick="closeModal()">✕</button>
                        </div>

                        ${renderMayilAvatarSVG(mayilAvatarState)}

                        <div style="background:rgba(56,189,248,0.1); border:1px solid var(--accent); padding:0.6rem; border-radius:6px; font-size:0.8rem; color:var(--accent); margin-bottom:1rem; text-align:center;">
                            💡 Mayil understands your family space in <strong>English, தமிழ், and हिन्दी</strong>.
                        </div>

                        <div style="max-height:200px; overflow-y:auto; margin-bottom:1rem;" id="chat-history-area">
                            ${historyHTML || '<div style="font-size:0.8rem; color:var(--text-sub); text-align:center; padding:1rem;">Ask Mayil "Show my family", "Schedule event", "Record memory", or "Show calendar"...</div>'}
                        </div>

                        <form onsubmit="submitMayilQuery(event)">
                            <div class="form-group" style="display:flex; gap:0.5rem;">
                                <input type="text" id="mayil-text-input" class="form-input" placeholder="Type in English, தமிழ் or हिन्दी..." required />
                                <button type="submit" class="btn">Ask</button>
                            </div>
                        </form>

                        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:1rem; flex-wrap:wrap; gap:0.5rem;">
                            <button class="btn btn-outline btn-sm" onclick="startVoiceControl()">🎙️ Voice Command</button>
                            <button class="btn btn-pink btn-sm" onclick="openAnimatedJourneyModal()">🎬 Play Full Journey</button>
                        </div>
                    </div>
                </div>
            `;
            container.style.display = 'block';
        }

        function submitMayilQuery(evt) {
            evt.preventDefault();
            const input = document.getElementById('mayil-text-input');
            const text = input ? input.value : '';
            if (!text) return;

            mayilAvatarState = 'thinking';

            const resolved = resolveFEMCIntent(text);
            let respText = "I'm here to help with your family events, memories, and notifications. Try asking 'Show my family' or 'Schedule event'.";
            let actionFn = null;
            let targetView = null;

            if (resolved) {
                respText = resolved.response[tourLanguage] || resolved.response['en'];
                actionFn = resolved.actionFn || null;
                targetView = resolved.view || null;

                if (targetView) loadView(targetView);

                if (resolved.requiresConfirmation && actionFn) {
                    respText += " Would you like to proceed with this action?";
                }
            }

            conversationHistory.push({ query: text, response: respText, actionFn: actionFn });
            input.value = '';
            mayilAvatarState = 'speaking';
            speakNarration(respText);
            openAskMayilPanel();
        }

        function openAnimatedJourneyModal() {
            currentJourneyScene = 0;
            isAutoPlayJourney = false;
            renderAnimatedJourneyScene();
        }

        function renderAnimatedJourneyScene() {
            const scene = JOURNEY_SCENES[currentJourneyScene];
            if (!scene) return;

            // Highlight target nav link
            document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('highlight'));
            const navEl = document.getElementById(`nav-${scene.nav}`);
            if (navEl) navEl.classList.add('highlight');

            const narrationText = scene.narration[tourLanguage] || scene.narration['en'];
            const container = document.getElementById('modal-container');

            container.innerHTML = `
                <div class="modal-overlay">
                    <div class="modal-card">
                        <div class="card-header">
                            <div class="card-title">🎬 Mayil's Journey (${scene.id} of ${JOURNEY_SCENES.length})</div>
                            <button class="btn btn-outline" style="padding:0.2rem 0.5rem;" onclick="closeModal()">✕</button>
                        </div>

                        <!-- Language Selector -->
                        <div style="display:flex; gap:0.5rem; margin-bottom:1rem; background:#0f172a; padding:0.4rem; border-radius:6px;">
                            <button class="btn btn-sm ${tourLanguage === 'en' ? '' : 'btn-outline'}" onclick="setJourneyLanguage('en')">🇬🇧 English</button>
                            <button class="btn btn-sm ${tourLanguage === 'ta' ? '' : 'btn-outline'}" onclick="setJourneyLanguage('ta')">🇮🇳 தமிழ்</button>
                            <button class="btn btn-sm ${tourLanguage === 'hi' ? '' : 'btn-outline'}" onclick="setJourneyLanguage('hi')">🇮🇳 हिन्दी</button>
                        </div>

                        ${renderMayilAvatarSVG('speaking')}

                        <div style="background:#0f172a; padding:1rem; border-radius:8px; border:1px solid var(--card-border); margin-bottom:1rem;">
                            <div style="font-size:1.1rem; font-weight:700; color:var(--accent); margin-bottom:0.4rem;">${scene.title}</div>
                            <div style="font-size:0.9rem; color:var(--text-main); line-height:1.5;">${narrationText}</div>
                        </div>

                        <div class="subtitle-bar">
                            <span style="font-size:1.1rem;">💬</span>
                            <div style="font-size:0.85rem; color:var(--text-main); font-weight:500;">
                                ${scene.caption}
                            </div>
                        </div>

                        <!-- Controls -->
                        <div style="display:flex; gap:0.5rem; margin-top:1rem; flex-wrap:wrap;">
                            <button class="btn" style="background:var(--pink); color:#000;" onclick="toggleAutoPlayJourney()">${isAutoPlayJourney ? '⏸ Pause Auto-Play' : '▶ Play Full Journey'}</button>
                            <button class="btn btn-outline" onclick="executeTourAction('${scene.actionFn.replace(/'/g, "\\'")}')">👉 Try It Now</button>
                            <button class="btn btn-outline" onclick="startScreenRecording()">🎥 Record Demo</button>
                        </div>

                        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:1.5rem;">
                            <button class="btn btn-outline" onclick="prevJourneyScene()" ${currentJourneyScene === 0 ? 'disabled' : ''}>◀ Previous</button>
                            <span style="font-size:0.8rem; color:var(--text-sub); font-weight:600;">Scene ${currentJourneyScene + 1} / ${JOURNEY_SCENES.length}</span>
                            ${currentJourneyScene < JOURNEY_SCENES.length - 1 ?
                                `<button class="btn" onclick="nextJourneyScene()">Next ▶</button>` :
                                `<button class="btn" style="background:var(--green); color:#000;" onclick="showTourCompletion()">🎉 Finish</button>`
                            }
                        </div>
                    </div>
                </div>
            `;
            container.style.display = 'block';
            speakNarration(narrationText);
        }

        function setJourneyLanguage(lang) {
            tourLanguage = lang;
            renderAnimatedJourneyScene();
        }

        function toggleAutoPlayJourney() {
            isAutoPlayJourney = !isAutoPlayJourney;
            if (isAutoPlayJourney) {
                runAutoPlayTimer();
            } else {
                if (autoPlayTimer) clearTimeout(autoPlayTimer);
            }
            renderAnimatedJourneyScene();
        }

        function runAutoPlayTimer() {
            if (!isAutoPlayJourney) return;
            if (currentJourneyScene < JOURNEY_SCENES.length - 1) {
                autoPlayTimer = setTimeout(() => {
                    currentJourneyScene++;
                    renderAnimatedJourneyScene();
                    runAutoPlayTimer();
                }, 4500);
            } else {
                isAutoPlayJourney = false;
            }
        }

        function nextJourneyScene() {
            stopNarration();
            if (currentJourneyScene < JOURNEY_SCENES.length - 1) {
                currentJourneyScene++;
                renderAnimatedJourneyScene();
            }
        }

        function prevJourneyScene() {
            stopNarration();
            if (currentJourneyScene > 0) {
                currentJourneyScene--;
                renderAnimatedJourneyScene();
            }
        }

        function speakNarration(text) {
            stopNarration();
            if (!text || !window.speechSynthesis) return;
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = tourLanguage === 'ta' ? 'ta-IN' : tourLanguage === 'hi' ? 'hi-IN' : 'en-US';
            window.speechSynthesis.speak(utterance);
        }

        function stopNarration() {
            if (window.speechSynthesis) window.speechSynthesis.cancel();
        }

        function executeTourAction(actionFnStr) {
            closeModal();
            try {
                eval(actionFnStr);
            } catch (err) {
                console.error("Action execution error:", err);
            }
        }

        function startVoiceControl() {
            const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRec) {
                alert("🎙️ Speech Recognition API is not supported in this browser. Please use the button controls.");
                return;
            }

            const rec = new SpeechRec();
            rec.lang = tourLanguage === 'ta' ? 'ta-IN' : tourLanguage === 'hi' ? 'hi-IN' : 'en-US';
            rec.onstart = () => alert("🎙️ Listening... Speak a command like 'Open calendar', 'Show family', 'Record memory'");
            rec.onresult = (e) => {
                const cmd = (e.results[0][0].transcript || '').toLowerCase();
                alert(`Recognized Command: "${cmd}"`);
                const resolved = resolveFEMCIntent(cmd);
                if (resolved) {
                    if (resolved.view) loadView(resolved.view);
                    if (resolved.actionFn) executeTourAction(resolved.actionFn);
                }
            };
            rec.start();
        }

        async function startScreenRecording() {
            try {
                if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia) {
                    throw new Error("Display media capture not supported");
                }
                const stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
                alert("🎥 Demo Screen Capture active! Guided tour screen is being recorded.");
            } catch (err) {
                alert("ℹ️ Screen capture permission denied or unsupported. Guided experience remains fully operational.");
            }
        }

        function showTourCompletion() {
            stopNarration();
            const container = document.getElementById('modal-container');
            container.innerHTML = `
                <div class="modal-overlay">
                    <div class="modal-card" style="text-align:center;">
                        <div style="font-size:2.5rem; margin-bottom:0.5rem;">🎉</div>
                        <div class="card-title" style="font-size:1.3rem; margin-bottom:0.5rem;">You completed Mayil's Animated FEMC Journey!</div>
                        <div style="font-size:0.85rem; color:var(--text-sub); margin-bottom:1.5rem;">
                            You now know how to manage family members, schedule events, record memories, capture A/V media, generate celebration cards, manage reminders, share moments, and protect family data.
                        </div>

                        <div style="display:flex; justify-content:center; gap:0.5rem;">
                            <button class="btn" style="background:var(--pink); color:#000;" onclick="openAnimatedJourneyModal()">🔁 Replay Journey</button>
                            <button class="btn btn-outline" onclick="closeModal(); loadView('home');">🏠 Go to FEMC Home</button>
                        </div>
                    </div>
                </div>
            `;
            container.style.display = 'block';
        }

        function openOnboardModal() {
            const container = document.getElementById('modal-container');
            container.innerHTML = `
                <div class="modal-overlay">
                    <div class="modal-card">
                        <div class="card-header">
                            <div class="card-title">➕ Add Family Member</div>
                            <button class="btn btn-outline" style="padding:0.2rem 0.5rem;" onclick="closeModal()">✕</button>
                        </div>
                        <form onsubmit="submitOnboard(event)">
                            <div class="form-group">
                                <label class="form-label">Full Name</label>
                                <input type="text" id="onboard-name" class="form-input" placeholder="e.g. David Smith" required />
                            </div>
                            <div class="form-group">
                                <label class="form-label">Email Address</label>
                                <input type="email" id="onboard-email" class="form-input" placeholder="e.g. david@smithfamily.org" required />
                            </div>
                            <div class="form-group">
                                <label class="form-label">Relationship to Active Member</label>
                                <select id="onboard-rel" class="form-select">
                                    <option value="SPOUSE">Spouse / Partner</option>
                                    <option value="PARENT_CHILD">Parent / Child</option>
                                    <option value="MEMBER" selected>Family Member</option>
                                </select>
                            </div>
                            <div style="display:flex; justify-content:flex-end; gap:0.5rem; margin-top:1.5rem;">
                                <button type="button" class="btn btn-outline" onclick="closeModal()">Cancel</button>
                                <button type="submit" class="btn">Add Member</button>
                            </div>
                        </form>
                    </div>
                </div>
            `;
            container.style.display = 'block';
        }

        async function submitOnboard(evt) {
            evt.preventDefault();
            const name = document.getElementById('onboard-name').value;
            const email = document.getElementById('onboard-email').value;
            const rel = document.getElementById('onboard-rel').value;

            await fetchAPI('/api/family/onboard', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: name, email: email, relationship: rel })
            });

            closeModal();
            await initMembers();
            loadView('family');
        }

        function openCreateEventModal() {
            const container = document.getElementById('modal-container');

            let memberCheckboxes = membersData.map(m => `
                <label class="checkbox-item">
                    <input type="checkbox" name="target_persons" value="${m.person_id}" />
                    ${m.name} (${m.email})
                </label>
            `).join('');

            container.innerHTML = `
                <div class="modal-overlay">
                    <div class="modal-card">
                        <div class="card-header">
                            <div class="card-title">📅 Schedule Family Event</div>
                            <button class="btn btn-outline" style="padding:0.2rem 0.5rem;" onclick="closeModal()">✕</button>
                        </div>
                        <form onsubmit="submitCreateEvent(event)">
                            <div class="form-group">
                                <label class="form-label">Event Title</label>
                                <input type="text" id="evt-title" class="form-input" placeholder="e.g. Family Game Night" required />
                            </div>
                            <div class="form-group">
                                <label class="form-label">Category</label>
                                <select id="evt-cat" class="form-select">
                                    <option value="GENERAL" selected>General</option>
                                    <option value="BIRTHDAY">Birthday</option>
                                    <option value="ANNIVERSARY">Anniversary</option>
                                    <option value="MILESTONE">Milestone</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Target Family Member(s)</label>
                                <div class="checkbox-group">
                                    ${memberCheckboxes}
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Visibility</label>
                                <select id="evt-vis" class="form-select">
                                    <option value="FAMILY" selected>Family Visible (All Members)</option>
                                    <option value="PRIVATE">Private (Only You)</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Description</label>
                                <input type="text" id="evt-desc" class="form-input" placeholder="Event details..." />
                            </div>
                            <div style="display:flex; justify-content:flex-end; gap:0.5rem; margin-top:1.5rem;">
                                <button type="button" class="btn btn-outline" onclick="closeModal()">Cancel</button>
                                <button type="submit" class="btn">Create Event</button>
                            </div>
                        </form>
                    </div>
                </div>
            `;
            container.style.display = 'block';
        }

        async function submitCreateEvent(evt) {
            evt.preventDefault();
            const title = document.getElementById('evt-title').value;
            const category = document.getElementById('evt-cat').value;
            const visibility = document.getElementById('evt-vis').value;
            const description = document.getElementById('evt-desc').value;

            const selectedCheckboxes = document.querySelectorAll('input[name="target_persons"]:checked');
            const target_person_ids = Array.from(selectedCheckboxes).map(cb => cb.value);

            await fetchAPI('/api/events/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: title,
                    category: category,
                    visibility: visibility,
                    description: description,
                    target_person_ids: target_person_ids
                })
            });

            closeModal();
            loadView('calendar');
        }

        // ==========================================
        // UNIFIED MEDIA CAPTURE CENTER & SHARING (WORKSTREAM V2.3-B.1 & V2.3-B.2)
        // ==========================================
        let capturedDataURI = '';
        let capturedMediaType = 'photo';

        function openMediaCaptureCenter(preselectedMemoryId = '') {
            stopMediaStream();
            capturedDataURI = '';
            capturedMediaType = 'photo';

            const container = document.getElementById('modal-container');
            container.innerHTML = `
                <div class="modal-overlay">
                    <div class="modal-card">
                        <div class="card-header">
                            <div class="card-title">📸 Add Family Media</div>
                            <button class="btn btn-outline" style="padding:0.2rem 0.5rem;" onclick="closeModal()">✕</button>
                        </div>

                        <div class="capture-tabs">
                            <button class="capture-tab active" onclick="switchCaptureTab('camera', event)">📷 Camera Photo</button>
                            <button class="capture-tab" onclick="switchCaptureTab('video', event)">🎥 Record Video</button>
                            <button class="capture-tab" onclick="switchCaptureTab('audio', event)">🎙️ Voice Memo</button>
                            <button class="capture-tab" onclick="switchCaptureTab('file', event)">📁 Upload File</button>
                            <button class="capture-tab" onclick="switchCaptureTab('drop', event)">🖱️ Drag & Drop</button>
                        </div>

                        <div id="capture-body-area">
                            <!-- Dynamically loaded capture mode body -->
                        </div>
                    </div>
                </div>
            `;
            container.style.display = 'block';
            switchCaptureTab('camera');
        }

        function switchCaptureTab(mode, evt) {
            stopMediaStream();
            if (evt) {
                document.querySelectorAll('.capture-tab').forEach(t => t.classList.remove('active'));
                evt.currentTarget.classList.add('active');
            }

            const body = document.getElementById('capture-body-area');
            if (mode === 'camera') {
                body.innerHTML = `
                    <div style="text-align:center;">
                        <video id="live-cam" autoplay playsinline style="width:100%; max-height:240px; background:#000; border-radius:8px; display:block; margin-bottom:1rem;"></video>
                        <div style="display:flex; justify-content:center; gap:0.5rem;">
                            <button class="btn" onclick="takeCameraSnapshot()">📸 Take Photo</button>
                        </div>
                        <div id="camera-status-msg" style="font-size:0.8rem; color:var(--text-sub); margin-top:0.5rem;">Starting camera stream...</div>
                    </div>
                `;
                initCameraStream();
            } else if (mode === 'video') {
                body.innerHTML = `
                    <div style="text-align:center;">
                        <video id="live-cam" autoplay playsinline muted style="width:100%; max-height:240px; background:#000; border-radius:8px; display:block; margin-bottom:1rem;"></video>
                        <div style="display:flex; justify-content:center; gap:0.5rem;">
                            <button id="rec-video-btn" class="btn" onclick="toggleVideoRecording()">🎥 Start Recording</button>
                        </div>
                        <div id="camera-status-msg" style="font-size:0.8rem; color:var(--text-sub); margin-top:0.5rem;">Ready to record video clip.</div>
                    </div>
                `;
                initCameraStream();
            } else if (mode === 'audio') {
                body.innerHTML = `
                    <div style="text-align:center; padding:1.5rem 1rem; background:#0f172a; border-radius:8px; border:1px solid var(--card-border); margin-bottom:1rem;">
                        <div style="font-size:2rem; margin-bottom:0.5rem;">🎙️</div>
                        <div style="font-size:0.9rem; font-weight:600; color:var(--text-main); margin-bottom:1rem;">Family Voice Memo Recorder</div>
                        <button id="rec-audio-btn" class="btn" onclick="toggleAudioRecording()">🎙️ Start Recording</button>
                        <div id="audio-status-msg" style="font-size:0.8rem; color:var(--text-sub); margin-top:0.8rem;">Click to record audio snippet.</div>
                    </div>
                `;
            } else if (mode === 'file') {
                body.innerHTML = `
                    <div class="form-group">
                        <label class="form-label">Select Photo, Video or Audio File</label>
                        <input type="file" id="media-file-input" class="form-input" accept="image/*,video/*,audio/*" onchange="handleFileSelect(event)" />
                    </div>
                    <div class="form-group" style="margin-top:1rem;">
                        <label class="form-label">Or Enter Image/Video URL</label>
                        <input type="url" id="media-url-input" class="form-input" placeholder="https://images.unsplash.com/photo-..." />
                        <button class="btn btn-outline" style="margin-top:0.5rem; width:100%;" onclick="useSampleURL()">Use Sample URL</button>
                    </div>
                `;
            } else if (mode === 'drop') {
                body.innerHTML = `
                    <div class="dropzone" id="drop-zone" ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)" ondrop="handleDrop(event)">
                        <div style="font-size:2rem; margin-bottom:0.4rem;">🖱️</div>
                        <div class="dropzone-title">Drop Family Media Here</div>
                        <div class="dropzone-sub">Supports photos, video clips, and audio files</div>
                    </div>
                `;
            }
        }

        async function initCameraStream() {
            try {
                if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                    throw new Error("getUserMedia not supported");
                }
                activeMediaStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
                const videoEl = document.getElementById('live-cam');
                if (videoEl) {
                    videoEl.srcObject = activeMediaStream;
                }
                const msg = document.getElementById('camera-status-msg');
                if (msg) msg.innerText = "Camera active. Ready to capture.";
            } catch (err) {
                console.warn("Camera access warning:", err);
                const msg = document.getElementById('camera-status-msg');
                if (msg) msg.innerText = "⚠️ Camera permission denied or unsupported. Falling back to File Upload mode.";
                setTimeout(() => switchCaptureTab('file'), 1500);
            }
        }

        function takeCameraSnapshot() {
            const videoEl = document.getElementById('live-cam');
            if (!videoEl) return;
            const canvas = document.createElement('canvas');
            canvas.width = videoEl.videoWidth || 640;
            canvas.height = videoEl.videoHeight || 480;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(videoEl, 0, 0, canvas.width, canvas.height);
            capturedDataURI = canvas.toDataURL('image/jpeg');
            capturedMediaType = 'photo';
            stopMediaStream();
            showCapturePreview();
        }

        function toggleVideoRecording() {
            const btn = document.getElementById('rec-video-btn');
            if (!mediaRecorder || mediaRecorder.state === 'inactive') {
                if (!activeMediaStream) return;
                recordedChunks = [];
                mediaRecorder = new MediaRecorder(activeMediaStream);
                mediaRecorder.ondataavailable = e => { if (e.data.size > 0) recordedChunks.push(e.data); };
                mediaRecorder.onstop = () => {
                    const blob = new Blob(recordedChunks, { type: 'video/webm' });
                    capturedDataURI = URL.createObjectURL(blob);
                    capturedMediaType = 'video';
                    stopMediaStream();
                    showCapturePreview();
                };
                mediaRecorder.start();
                btn.innerText = "⏹️ Stop Recording";
                btn.style.background = "#f87171";
            } else {
                mediaRecorder.stop();
            }
        }

        async function toggleAudioRecording() {
            const btn = document.getElementById('rec-audio-btn');
            const msg = document.getElementById('audio-status-msg');
            if (!mediaRecorder || mediaRecorder.state === 'inactive') {
                try {
                    activeMediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    recordedChunks = [];
                    mediaRecorder = new MediaRecorder(activeMediaStream);
                    mediaRecorder.ondataavailable = e => { if (e.data.size > 0) recordedChunks.push(e.data); };
                    mediaRecorder.onstop = () => {
                        const blob = new Blob(recordedChunks, { type: 'audio/webm' });
                        capturedDataURI = URL.createObjectURL(blob);
                        capturedMediaType = 'audio';
                        stopMediaStream();
                        showCapturePreview();
                    };
                    mediaRecorder.start();
                    btn.innerText = "⏹️ Stop Recording";
                    btn.style.background = "#f87171";
                    if (msg) msg.innerText = "Recording voice memo...";
                } catch (err) {
                    console.warn("Microphone access warning:", err);
                    if (msg) msg.innerText = "⚠️ Microphone permission denied. Falling back to File Upload mode.";
                    setTimeout(() => switchCaptureTab('file'), 1500);
                }
            } else {
                mediaRecorder.stop();
            }
        }

        function handleFileSelect(evt) {
            const file = evt.target.files[0];
            if (!file) return;
            processFileForPreview(file);
        }

        function handleDragOver(evt) {
            evt.preventDefault();
            evt.currentTarget.classList.add('hover');
        }

        function handleDragLeave(evt) {
            evt.currentTarget.classList.remove('hover');
        }

        function handleDrop(evt) {
            evt.preventDefault();
            evt.currentTarget.classList.remove('hover');
            const file = evt.dataTransfer.files[0];
            if (file) processFileForPreview(file);
        }

        function processFileForPreview(file) {
            const reader = new FileReader();
            if (file.type.startsWith('video/')) capturedMediaType = 'video';
            else if (file.type.startsWith('audio/')) capturedMediaType = 'audio';
            else capturedMediaType = 'photo';

            reader.onload = e => {
                capturedDataURI = e.target.result;
                showCapturePreview(file.name);
            };
            reader.readAsDataURL(file);
        }

        function useSampleURL() {
            const input = document.getElementById('media-url-input');
            const url = input ? input.value : '';
            capturedDataURI = url || 'https://images.unsplash.com/photo-1513151233558-d860c5398176';
            capturedMediaType = 'photo';
            showCapturePreview('Sample Photo');
        }

        function showCapturePreview(fileName = 'Captured Media') {
            const body = document.getElementById('capture-body-area');
            let previewHTML = '';
            if (capturedMediaType === 'video') {
                previewHTML = `<video controls src="${capturedDataURI}" style="width:100%; max-height:240px; background:#000; border-radius:8px; display:block; margin-bottom:1rem;"></video>`;
            } else if (capturedMediaType === 'audio') {
                previewHTML = `<div style="background:#0f172a; padding:1rem; border-radius:8px; border:1px solid var(--card-border); margin-bottom:1rem;"><audio controls src="${capturedDataURI}" style="width:100%;"></audio></div>`;
            } else {
                previewHTML = `<img src="${capturedDataURI}" style="width:100%; max-height:240px; object-fit:cover; border-radius:8px; display:block; margin-bottom:1rem;" />`;
            }

            let eventOptions = '<option value="">-- Select Linked Event (Optional) --</option>';
            fetchAPI('/api/events').then(data => {
                const cal = data.calendar || [];
                const select = document.getElementById('context-event-select');
                if (select) {
                    select.innerHTML = eventOptions + cal.map(c => `<option value="${c.event_id}">${c.title} (${c.date})</option>`).join('');
                }
            });

            body.innerHTML = `
                <div style="margin-bottom:1rem;">
                    <div style="font-size:0.85rem; font-weight:700; color:var(--accent); margin-bottom:0.5rem;">MEDIA PREVIEW (${capturedMediaType.toUpperCase()})</div>
                    ${previewHTML}
                </div>

                <form onsubmit="submitSavedMedia(event)">
                    <div class="form-group">
                        <label class="form-label">Caption / Description</label>
                        <input type="text" id="context-caption" class="form-input" value="${fileName}" required />
                    </div>
                    <div class="form-group">
                        <label class="form-label">What is this memory about? (Optional Narrative)</label>
                        <input type="text" id="context-narrative" class="form-input" placeholder="e.g. Birthday cake & song celebration" />
                    </div>
                    <div class="form-group">
                        <label class="form-label">Associate with Event</label>
                        <select id="context-event-select" class="form-select">
                            <option value="">-- Loading events... --</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Visibility</label>
                        <select id="context-vis" class="form-select">
                            <option value="FAMILY" selected>Family Visible</option>
                            <option value="PRIVATE">Private (Only You)</option>
                        </select>
                    </div>
                    <div style="display:flex; justify-content:space-between; gap:0.5rem; margin-top:1.5rem;">
                        <button type="button" class="btn btn-outline" onclick="openMediaCaptureCenter()">🔄 Retake / Discard</button>
                        <button type="submit" class="btn">💾 Save Family Media</button>
                    </div>
                </form>
            `;
        }

        async function submitSavedMedia(evt) {
            evt.preventDefault();
            const caption = document.getElementById('context-caption').value;
            const narrative = document.getElementById('context-narrative').value;
            const event_id = document.getElementById('context-event-select').value;
            const vis = document.getElementById('context-vis').value;

            let memory_id = null;
            if (narrative && event_id) {
                const memRes = await fetchAPI('/api/memories/create', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ narrative: narrative, event_id: event_id, visibility: vis })
                });
                if (memRes.memory) memory_id = memRes.memory.id;
            }

            await fetchAPI('/api/media/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    uri: capturedDataURI,
                    caption: caption,
                    media_type: capturedMediaType,
                    event_id: event_id || null,
                    memory_id: memory_id || null,
                    visibility: vis
                })
            });

            closeModal();
            loadView('memories');
        }

        // ==========================================
        // MEDIA SHARING & SOCIAL EXPORT (WORKSTREAM V2.3-B.2)
        // ==========================================
        async function openShareMediaModal(mediaId, caption, uri, mediaType, visibility) {
            const shareRes = await fetchAPI('/api/sharing/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    resource_type: 'MEDIA_ITEM',
                    resource_id: mediaId,
                    expires_in_minutes: 1440
                })
            });

            const shareToken = shareRes.share_link ? shareRes.share_link.token : 'demo_token';
            const shareUrl = `${window.location.origin}/share?token=${shareToken}`;

            let icon = '📸';
            if (mediaType === 'video') icon = '🎥';
            else if (mediaType === 'audio') icon = '🎙️';

            const shareTitle = `${icon} ${caption || 'Family Memory'}`;

            const container = document.getElementById('modal-container');
            container.innerHTML = `
                <div class="modal-overlay">
                    <div class="modal-card">
                        <div class="card-header">
                            <div class="card-title">Share this family moment</div>
                            <button class="btn btn-outline" style="padding:0.2rem 0.5rem;" onclick="closeModal()">✕</button>
                        </div>

                        <div style="background:#0f172a; padding:0.8rem; border-radius:8px; border:1px solid var(--card-border); margin-bottom:1rem;">
                            <div style="font-size:0.95rem; font-weight:700; color:var(--text-main); margin-bottom:0.3rem;">${shareTitle}</div>
                            <div style="font-size:0.8rem; color:var(--text-sub);">Media Type: ${mediaType.toUpperCase()} | Visibility: ${visibility}</div>
                        </div>

                        <div style="background:rgba(56,189,248,0.1); border:1px solid var(--accent); padding:0.6rem; border-radius:6px; font-size:0.8rem; color:var(--accent); margin-bottom:1rem;">
                            ℹ️ <strong>Demo / Local Host Notice:</strong> Share link created. Available within this device/local host (<code>http://127.0.0.1:8000</code>). Configure FEMC public origin for deployed external sharing.
                        </div>

                        <div class="form-group">
                            <label class="form-label">Authorized Share Token URL</label>
                            <input type="text" id="share-url-input" class="form-input" value="${shareUrl}" readonly />
                        </div>

                        <div style="display:flex; flex-direction:column; gap:0.5rem; margin-top:1rem;">
                            <button class="btn" style="background:var(--pink); color:#000;" onclick="triggerDeviceShare('${shareTitle.replace(/'/g, "\\'")}', '${shareUrl}')">📱 Device Share (navigator.share)</button>
                            <button class="btn" style="background:#25D366; color:#fff;" onclick="triggerWhatsAppShare('${shareTitle.replace(/'/g, "\\'")}', '${shareUrl}', '${mediaType}')">💬 Share to WhatsApp</button>
                            <button class="btn btn-outline" onclick="copyShareUrl('${shareUrl}')">📋 Copy Share Link</button>
                        </div>
                    </div>
                </div>
            `;
            container.style.display = 'block';
        }

        async function triggerDeviceShare(title, shareUrl) {
            if (navigator.share) {
                try {
                    await navigator.share({
                        title: title,
                        text: `${title} - A special family moment from Smith Family`,
                        url: shareUrl
                    });
                } catch (err) {
                    console.log("Device share cancelled or dismissed:", err);
                }
            } else {
                alert("Native device sharing (navigator.share) is not supported in this browser. Use Copy Link or WhatsApp.");
            }
        }

        function triggerWhatsAppShare(title, shareUrl, mediaType) {
            const text = encodeURIComponent(`${title}\nA special family moment from Smith Family.\n${shareUrl}`);
            window.open(`https://api.whatsapp.com/send?text=${text}`, '_blank');
        }

        function copyShareUrl(url) {
            navigator.clipboard.writeText(url);
            alert("🔗 Secure Share Link copied to clipboard!");
        }

        function openGenerateArtifactModal() {
            const container = document.getElementById('modal-container');
            container.innerHTML = `
                <div class="modal-overlay">
                    <div class="modal-card">
                        <div class="card-header">
                            <div class="card-title">✨ Generate Celebration Artifact</div>
                            <button class="btn btn-outline" style="padding:0.2rem 0.5rem;" onclick="closeModal()">✕</button>
                        </div>
                        <form onsubmit="submitGenerateArtifact(event)">
                            <div class="form-group">
                                <label class="form-label">Artifact Target Type</label>
                                <select id="art-target-type" class="form-select">
                                    <option value="event" selected>Event Celebration Card</option>
                                    <option value="person">Person Highlight Digest</option>
                                </select>
                            </div>
                            <div style="display:flex; justify-content:flex-end; gap:0.5rem; margin-top:1.5rem;">
                                <button type="button" class="btn btn-outline" onclick="closeModal()">Cancel</button>
                                <button type="submit" class="btn">Generate Artifact</button>
                            </div>
                        </form>
                    </div>
                </div>
            `;
            container.style.display = 'block';
        }

        async function submitGenerateArtifact(evt) {
            evt.preventDefault();
            const targetType = document.getElementById('art-target-type').value;

            const eventsData = await fetchAPI('/api/events');
            const cal = eventsData.calendar || [];
            const targetId = cal.length > 0 ? cal[0].event_id : '';

            if (targetId) {
                await fetchAPI('/api/celebrations/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        target_type: targetType,
                        target_id: targetId
                    })
                });
            }

            closeModal();
            loadView('celebrations');
        }

        function openShareModal(resourceType, resourceId) {
            const container = document.getElementById('modal-container');
            container.innerHTML = `
                <div class="modal-overlay">
                    <div class="modal-card">
                        <div class="card-header">
                            <div class="card-title">🔗 Create Share Link</div>
                            <button class="btn btn-outline" style="padding:0.2rem 0.5rem;" onclick="closeModal()">✕</button>
                        </div>
                        <form onsubmit="submitCreateShare(event, '${resourceType}', '${resourceId}')">
                            <div class="form-group">
                                <label class="form-label">Resource Type</label>
                                <input type="text" class="form-input" value="${resourceType}" readonly />
                            </div>
                            <div class="form-group">
                                <label class="form-label">Expiration (Minutes)</label>
                                <input type="number" id="share-expires" class="form-input" value="1440" />
                            </div>
                            <div style="display:flex; justify-content:flex-end; gap:0.5rem; margin-top:1.5rem;">
                                <button type="button" class="btn btn-outline" onclick="closeModal()">Cancel</button>
                                <button type="submit" class="btn">Generate Share Token</button>
                            </div>
                        </form>
                    </div>
                </div>
            `;
            container.style.display = 'block';
        }

        async function submitCreateShare(evt, resourceType, resourceId) {
            evt.preventDefault();
            const expires = parseInt(document.getElementById('share-expires').value) || 1440;

            await fetchAPI('/api/sharing/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    resource_type: resourceType,
                    resource_id: resourceId,
                    expires_in_minutes: expires
                })
            });

            closeModal();
            loadView('sharing');
        }

        async function revokeShareLink(token) {
            await fetchAPI('/api/sharing/revoke', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token: token })
            });
            loadView('sharing');
        }

        async function createMemoryPrompt() {
            const narrative = prompt("Enter memory narrative:", "Alice made delicious dessert!");
            if (narrative) {
                await fetchAPI('/api/memories/create', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ narrative: narrative })
                });
                loadView('memories');
            }
        }

        async function markNotificationRead(notifId) {
            await fetchAPI('/api/notifications/read', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ notification_id: notifId })
            });
            loadView('reminders');
        }

        async function approveProposal(propId) {
            await fetchAPI('/api/mayil/approve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ proposal_id: propId })
"""


class DemoHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/" or path == "/share":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
            return

        api = demo_state.api
        session_id = demo_state.session_id
        fc_id = demo_state.family_context.id

        if path == "/api/status":
            res = {
                "session_id": session_id,
                "active_account_id": demo_state.active_account_id,
                "family_context_id": fc_id,
            }
            self._send_json(res)
        elif path == "/api/members":
            members_list = []
            for acc_id, sess_id in demo_state.account_sessions.items():
                acc = api.canonical.get_account(acc_id)
                per = api.canonical.get_person(acc.person_id) if acc and acc.person_id else None
                if acc and per:
                    members_list.append({
                        "account_id": acc.id,
                        "person_id": per.id,
                        "name": per.name,
                        "email": acc.email,
                        "username": acc.username,
                        "session_id": sess_id,
                        "is_active": acc.id == demo_state.active_account_id,
                    })
            self._send_json({"members": members_list, "active_account_id": demo_state.active_account_id})
        elif path == "/api/dashboard":
            summary = api.get_dashboard_summary_for_session(session_id, fc_id)
            entries = api.get_dashboard_projection_for_session(session_id, fc_id)
            self._send_json({"summary": to_dict(summary), "entries": to_dict(entries)})
        elif path == "/api/family":
            topology = api.get_family_topology_for_session(session_id, fc_id)
            active_account = api.canonical.get_account(demo_state.active_account_id)
            active_person_id = active_account.person_id if active_account else demo_state.p_alice.id
            active_detail = api.build_rich_person_detail_for_session(session_id, active_person_id)
            self._send_json({"topology": to_dict(topology), "active_person_detail": to_dict(active_detail)})
        elif path == "/api/events":
            calendar = api.get_calendar_for_session(session_id, fc_id)
            detail = api.build_rich_event_detail_for_session(session_id, demo_state.event1.id)
            self._send_json({"calendar": to_dict(calendar), "event_detail": to_dict(detail)})
        elif path == "/api/timeline":
            timeline = api.get_timeline_for_session(session_id, fc_id)
            event_memories = api.get_event_with_memories_for_session(session_id, demo_state.event1.id)
            self._send_json({"timeline": to_dict(timeline), "event_memories": to_dict(event_memories)})
        elif path == "/api/media":
            items = [m for m in api.canonical.list_media_items() if m.family_context_id == fc_id and api.authorization.can_view_media_item(demo_state.acc_alice.id, m, demo_state.family_context)]
            albums = [a for a in api.canonical.list_media_albums() if a.family_context_id == fc_id and api.authorization.can_view_media_album(demo_state.acc_alice.id, a, demo_state.family_context)]
            self._send_json({"items": to_dict(items), "albums": to_dict(albums)})
        elif path == "/api/celebrations":
            artifacts = api.list_celebration_artifacts_for_session(session_id, fc_id)
            self._send_json({"artifacts": to_dict(artifacts)})
        elif path == "/api/reminders":
            notifs = api.list_notifications_for_session(session_id)
            triggered = api.trigger_due_reminders_for_session(session_id, fc_id)
            self._send_json({"notifications": to_dict(notifs), "triggered": to_dict(triggered)})
        elif path == "/api/sharing":
            links = [l for l in api.canonical.list_share_links() if l.family_context_id == fc_id]
            self._send_json({"share_links": to_dict(links)})
        elif path == "/api/sharing/resolve":
            token = query.get("token", [""])[0]
            if token:
                try:
                    resource = api.resolve_share_token(token)
                    self._send_json({"status": "success", "resource": to_dict(resource)})
                except PermissionError as e:
                    self._send_json({"status": "error", "message": str(e)})
            else:
                self._send_json({"status": "error", "message": "Missing token"})
        elif path == "/api/mayil":
            insight = api.analyze_family_insights_for_session(session_id, fc_id)
            proposals = api.get_action_proposals_for_session(session_id, fc_id)
            self._send_json({"insight": to_dict(insight), "proposals": to_dict(proposals)})
        elif path == "/api/guardian":
            audit = api.run_integrity_audit_for_session(session_id, fc_id)
            proposals = api.get_repair_proposals_for_session(session_id, fc_id)
            self._send_json({"audit": to_dict(audit), "repair_proposals": to_dict(proposals)})
        elif path == "/api/guide/practice/status":
            session = demo_state.api._validate_session(demo_state.session_id)
            pw = demo_state.api.get_practice_world_state_for_session(session.session_id)
            if not pw:
                pw = demo_state.api.start_practice_world_for_session(session.session_id, demo_state.family_context.id)
            self._send_json({"practice_world": to_dict(pw)})
            return
        elif path == "/api/guide/status":
            session = demo_state.api._validate_session(demo_state.session_id)
            st = demo_state.api.get_guided_experience_state_for_session(session.session_id)
            if not st:
                st = demo_state.api.initialize_guided_experience_for_session(session.session_id, demo_state.family_context.id)
            scenes = demo_state.api.get_shared_journey_scenes_for_session(session.session_id)
            self._send_json({"session_state": to_dict(st), "scenes": to_dict(scenes)})
            return
        elif path == "/api/export":
            export_data = api.export_family_context_for_session(session_id, fc_id)
            validation = api.validate_data_export(to_dict(export_data))
            self._send_json({"export": to_dict(export_data), "validation": to_dict(validation)})
        elif path == "/api/history":
            session = demo_state.api._validate_session(demo_state.session_id)
            history = demo_state.api.get_transaction_history_for_session(
                session.session_id, demo_state.family_context.id, limit=50
            )
            res = [r.__dict__ for r in history]
            for r in res:
                r['timestamp'] = r['timestamp'].isoformat()
                r['action_type'] = str(r['action_type'])
                r['resource_type'] = str(r['resource_type'])
                r['visibility'] = str(r['visibility'])
            self._send_json({"transactions": res})
        elif path.startswith("/api/resource_history"):
            session = demo_state.api._validate_session(demo_state.session_id)
            res_type = query.get('type', ['event'])[0]
            res_id = query.get('id', [''])[0]
            from ENGINEERING.source.femc.models import ResourceType
            try:
                rt = ResourceType(res_type.lower())
            except Exception:
                rt = ResourceType.EVENT
            explanation = demo_state.api.explain_resource_history_for_session(
                session.session_id, demo_state.family_context.id, rt, res_id
            )
            self._send_json(explanation)
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/reset":
            demo_state.reset()
            self._send_json({"status": "reset_success"})
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        api = demo_state.api
        session_id = demo_state.session_id
        fc_id = demo_state.family_context.id

        if path == "/api/guide/practice/start":
            session = demo_state.api._validate_session(demo_state.session_id)
            from ENGINEERING.source.femc.models import ContextType, AgeGroup, Language
            ctx_str = payload.get("context_type", "family").lower()
            age_str = payload.get("age_group", "mixed").lower()
            lang_str = payload.get("language", "en").lower()
            inc_fam = payload.get("include_family", True)

            try: ctx = ContextType(ctx_str)
            except Exception: ctx = ContextType.FAMILY

            try: age = AgeGroup(age_str)
            except Exception: age = AgeGroup.MIXED

            try: lang = Language(lang_str)
            except Exception: lang = Language.ENGLISH

            pw = demo_state.api.start_practice_world_for_session(
                session.session_id, demo_state.family_context.id, ctx, age, inc_fam, lang
            )
            self._send_json({"status": "success", "practice_world": to_dict(pw)})
            return
        elif path == "/api/guide/practice/action":
            session = demo_state.api._validate_session(demo_state.session_id)
            from ENGINEERING.source.femc.models import ActionType, ResourceType
            act_str = payload.get("action_type", "PERSPECTIVE_SWITCH").upper()
            res_type_str = payload.get("resource_type", "EVENT").upper()
            ctrl_id = payload.get("control_id", "nav-home")
            action_payload = payload.get("payload", {})

            try: act = ActionType(act_str.lower())
            except Exception: act = ActionType.PERSPECTIVE_SWITCH

            try: rt = ResourceType(res_type_str.lower())
            except Exception: rt = ResourceType.EVENT

            res = demo_state.api.execute_simulated_action_for_session(
                session.session_id, act, ctrl_id, rt, action_payload
            )
            self._send_json(to_dict(res))
            return
        elif path == "/api/guide/practice/reset":
            session = demo_state.api._validate_session(demo_state.session_id)
            pw = demo_state.api.reset_practice_world_for_session(session.session_id)
            self._send_json({"status": "success", "message": "Practice World reset successfully.", "practice_world": to_dict(pw)})
            return
        elif path == "/api/guide/practice/exit":
            session = demo_state.api._validate_session(demo_state.session_id)
            res = demo_state.api.exit_practice_world_for_session(session.session_id)
            self._send_json(to_dict(res))
            return
        elif path == "/api/guide/init":
            session = demo_state.api._validate_session(demo_state.session_id)
            from ENGINEERING.source.femc.models import GuideMode, ContextType, AgeGroup, Language
            mode_str = payload.get("mode", "learn_by_doing").lower()
            ctx_str = payload.get("context_type", "family").lower()
            age_str = payload.get("age_group", "mixed").lower()
            lang_str = payload.get("language", "en").lower()
            inc_fam = payload.get("include_family", True)

            try: mode = GuideMode(mode_str)
            except Exception: mode = GuideMode.LEARN_BY_DOING

            try: ctx = ContextType(ctx_str)
            except Exception: ctx = ContextType.FAMILY

            try: age = AgeGroup(age_str)
            except Exception: age = AgeGroup.MIXED

            try: lang = Language(lang_str)
            except Exception: lang = Language.ENGLISH

            st = demo_state.api.initialize_guided_experience_for_session(
                session.session_id, demo_state.family_context.id, mode, ctx, age, inc_fam, lang
            )
            scenes = demo_state.api.get_shared_journey_scenes_for_session(session.session_id)
            self._send_json({"status": "success", "session_state": to_dict(st), "scenes": to_dict(scenes)})
            return
        elif path == "/api/guide/validate":
            session = demo_state.api._validate_session(demo_state.session_id)
            from ENGINEERING.source.femc.models import ActionType
            act_str = payload.get("action_type", "PERSPECTIVE_SWITCH").upper()
            ctrl_id = payload.get("control_id", "nav-home")
            res_id = payload.get("resource_id", "")
            res_label = payload.get("resource_label", "")
            op = payload.get("operation", "")

            try: act = ActionType(act_str.lower())
            except Exception: act = ActionType.PERSPECTIVE_SWITCH

            res = demo_state.api.validate_guided_action_for_session(
                session.session_id, act, ctrl_id, res_id, res_label, op
            )
            self._send_json(to_dict(res))
            return
        elif path == "/api/guide/switch_mode":
            session = demo_state.api._validate_session(demo_state.session_id)
            from ENGINEERING.source.femc.models import GuideMode
            mode_str = payload.get("mode", "learn_by_doing").lower()
            try: mode = GuideMode(mode_str)
            except Exception: mode = GuideMode.LEARN_BY_DOING

            st = demo_state.api.switch_guided_experience_mode_for_session(session.session_id, mode)
            self._send_json({"status": "success", "session_state": to_dict(st)})
            return
        elif path == "/api/guide/reset":
            session = demo_state.api._validate_session(demo_state.session_id)
            st = demo_state.api.reset_guided_experience_for_session(session.session_id)
            self._send_json({"status": "success", "session_state": to_dict(st)})
            return
        elif path == "/api/session/switch":
            acc_id = payload.get("account_id")
            if acc_id:
                new_session_id = demo_state.switch_session(acc_id)
                self._send_json({"status": "success", "active_account_id": acc_id, "session_id": new_session_id})
            else:
                self._send_json({"status": "error", "message": "Missing account_id"})
        elif path == "/api/family/onboard":
            name = payload.get("name", "New Member")
            email = payload.get("email", "member@example.com")
            rel = payload.get("relationship", "MEMBER")
            acc, per, sess = demo_state.onboard_member(name=name, email=email, relationship_type_str=rel)
            self._send_json({
                "status": "success",
                "account_id": acc.id,
                "person_id": per.id,
                "session_id": sess.session_id,
            })
        elif path == "/api/events/create":
            title = payload.get("title", "New Event")
            desc = payload.get("description", "")
            cat_str = payload.get("category", "GENERAL").upper()
            vis_str = payload.get("visibility", "FAMILY").upper()
            target_ids = payload.get("target_person_ids", [])

            try:
                cat = EventCategory(cat_str.lower())
            except ValueError:
                cat = EventCategory.GENERAL

            try:
                vis = VisibilityLevel(vis_str.lower())
            except ValueError:
                vis = VisibilityLevel.FAMILY

            now = _utc_now()
            event = api.create_event_for_session(
                session_id=session_id,
                title=title,
                description=desc,
                family_context_id=fc_id,
                start_time=now + datetime.timedelta(days=1),
                end_time=now + datetime.timedelta(days=1, hours=2),
                visibility=vis,
                category=cat,
                target_person_ids=target_ids,
            )
            self._send_json({"status": "success", "event": to_dict(event)})
        elif path == "/api/memories/create":
            narrative = payload.get("narrative", "Shared memory")
            evt_id = payload.get("event_id", demo_state.event1.id)
            vis_str = payload.get("visibility", "FAMILY").upper()
            try:
                vis = VisibilityLevel(vis_str.lower())
            except ValueError:
                vis = VisibilityLevel.FAMILY

            memory = api.create_memory_for_session(
                session_id=session_id,
                event_id=evt_id,
                narrative=narrative,
                visibility=vis,
            )
            self._send_json({"status": "success", "memory": to_dict(memory)})
        elif path == "/api/media/create":
            uri = payload.get("uri", "https://images.unsplash.com/photo-1513151233558-d860c5398176")
            caption = payload.get("caption", "Family media")
            media_type_str = payload.get("media_type", "photo").lower()
            mem_id = payload.get("memory_id")
            evt_id = payload.get("event_id")
            vis_str = payload.get("visibility", "FAMILY").upper()

            try:
                m_type = MediaType(media_type_str)
            except ValueError:
                m_type = MediaType.PHOTO

            try:
                vis = VisibilityLevel(vis_str.lower())
            except ValueError:
                vis = VisibilityLevel.FAMILY

            item = api.create_media_item_for_session(
                session_id=session_id,
                uri=uri,
                media_type=m_type,
                caption=caption,
                family_context_id=fc_id,
                event_id=evt_id,
                memory_id=mem_id,
                visibility=vis,
            )
            self._send_json({"status": "success", "media_item": to_dict(item)})
        elif path == "/api/media/album/create":
            title = payload.get("title", "New Album")
            desc = payload.get("description", "")
            media_ids = payload.get("media_ids", [])
            album = api.create_media_album_for_session(
                session_id=session_id,
                title=title,
                description=desc,
                family_context_id=fc_id,
                media_ids=media_ids,
                visibility=VisibilityLevel.FAMILY,
            )
            self._send_json({"status": "success", "media_album": to_dict(album)})
        elif path == "/api/celebrations/generate":
            target_type = payload.get("target_type", "event")
            target_id = payload.get("target_id", demo_state.event1.id)

            if target_type == "event":
                artifact = api.build_celebration_artifact_for_event_for_session(session_id, target_id)
            elif target_type == "person":
                artifact = api.build_celebration_artifact_for_person_for_session(session_id, demo_state.p_alice.id, fc_id)
            elif target_type == "memory":
                artifact = api.build_celebration_artifact_for_memory_for_session(session_id, demo_state.memory1.id)
            elif target_type == "album":
                artifact = api.build_celebration_album_artifact_for_session(session_id, demo_state.album1.id)
            else:
                artifact = api.build_celebration_artifact_for_event_for_session(session_id, demo_state.event1.id)

            self._send_json({"status": "success", "artifact": to_dict(artifact)})
        elif path == "/api/sharing/create":
            res_type_str = payload.get("resource_type", "EVENT").upper()
            res_id = payload.get("resource_id", demo_state.event1.id)
            expires = payload.get("expires_in_minutes", 1440)

            try:
                res_type = ShareResourceType(res_type_str.lower())
            except ValueError:
                res_type = ShareResourceType.EVENT

            link = api.create_share_link_for_session(
                session_id=session_id,
                resource_type=res_type,
                resource_id=res_id,
                family_context_id=fc_id,
                expires_in_minutes=expires,
            )
            self._send_json({"status": "success", "share_link": to_dict(link)})
        elif path == "/api/sharing/revoke":
            token = payload.get("token")
            if token:
                link = api.revoke_share_link_for_session(session_id, token)
                self._send_json({"status": "success", "share_link": to_dict(link)})
            else:
                self._send_json({"status": "error", "message": "Missing token"})
        elif path == "/api/notifications/read":
            notif_id = payload.get("notification_id")
            if notif_id:
                notif = api.mark_notification_read_for_session(session_id, notif_id)
                self._send_json({"status": "success", "notification": to_dict(notif)})
            else:
                self._send_json({"status": "error", "message": "Missing notification_id"})
        elif path == "/api/mayil/approve":
            prop_id = payload.get("proposal_id")
            if prop_id:
                prop = api.approve_action_proposal_for_session(session_id, prop_id)
                self._send_json({"status": "success", "proposal": to_dict(prop)})
            else:
                self._send_json({"status": "error", "message": "Missing proposal_id"})
        elif path == "/api/guardian/repair":
            prop_id = payload.get("proposal_id")
            if prop_id:
                prop = api.execute_repair_proposal_for_session(session_id, prop_id)
                self._send_json({"status": "success", "proposal": to_dict(prop)})
            else:
                self._send_json({"status": "error", "message": "Missing proposal_id"})
        else:
            self.send_error(404, "Not Found")

    def _send_json(self, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


def run_server(host="127.0.0.1", port=8000):
    server_address = (host, port)
    httpd = HTTPServer(server_address, DemoHTTPRequestHandler)
    print(f"FEMC First User Experience Demo Host running at http://{host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()


if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run_server(port=port)
