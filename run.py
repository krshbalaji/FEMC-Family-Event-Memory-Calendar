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
    NotificationType,
    RelationshipType,
    ReminderType,
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


class DemoState:
    def __init__(self):
        self.api = None
        self.reset()

    def reset(self):
        self.api = FEMCApi()

        # 1. Create People
        self.p_alice = self.api.identity.create_person("Alice Smith", birth_date=datetime.date(1990, 5, 15))
        self.p_bob = self.api.identity.create_person("Bob Smith", birth_date=datetime.date(1988, 10, 20))

        # 2. Create Accounts
        self.acc_alice = self.api.identity.create_account("alice_smith", "alice@example.com", person_id=self.p_alice.id)
        self.acc_bob = self.api.identity.create_account("bob_smith", "bob@example.com", person_id=self.p_bob.id)

        # 3. Relationship
        self.api.identity.create_relationship(self.p_alice.id, self.p_bob.id, RelationshipType.PARTNER, confidence=Confidence.HIGH)

        # 4. Family Context
        self.family_context = self.api.identity.create_family_context("Smith Family", member_ids=[self.acc_alice.id, self.acc_bob.id], created_by_id=self.acc_alice.id)

        # 5. Session for Alice
        self.session = self.api.create_session(self.acc_alice.id)
        self.session_id = self.session.session_id

        # 6. Events (Deterministic Seed State with Correct Categories)
        now = _utc_now()
        start_bday = now + datetime.timedelta(days=7)
        start_gen = now + datetime.timedelta(days=2)

        # Event 1: Birthday
        self.event1 = self.api.create_event_for_session(
            session_id=self.session_id,
            title="Alice's Birthday Celebration",
            description="Gathering at home for Alice's birthday dinner.",
            family_context_id=self.family_context.id,
            start_time=start_bday,
            end_time=start_bday + datetime.timedelta(hours=3),
            category=EventCategory.BIRTHDAY,
            target_person_ids=[self.p_alice.id],
            visibility=VisibilityLevel.FAMILY,
        )

        # Event 2: General Family Gathering
        self.event2 = self.api.create_event_for_session(
            session_id=self.session_id,
            title="Smith Family Weekend Dinner",
            description="Casual Sunday family dinner.",
            family_context_id=self.family_context.id,
            start_time=start_gen,
            end_time=start_gen + datetime.timedelta(hours=2),
            category=EventCategory.GENERAL,
            target_person_ids=[self.p_alice.id, self.p_bob.id],
            visibility=VisibilityLevel.FAMILY,
        )

        # 7. Memory
        self.memory1 = self.api.create_memory_for_session(
            session_id=self.session_id,
            event_id=self.event1.id,
            narrative="We blew out candles and shared old photo albums.",
            visibility=VisibilityLevel.FAMILY,
        )

        # 8. Reminder
        self.reminder1 = self.api.configure_reminder_for_session(
            session_id=self.session_id,
            event_id=self.event1.id,
            offset_minutes=60,
            reminder_type=ReminderType.EVENT_START,
        )

        # 9. Notification
        self.notif1 = self.api.create_notification_for_session(
            session_id=self.session_id,
            recipient_id=self.acc_alice.id,
            notification_type=NotificationType.SYSTEM_ALERT,
            title="Welcome to FEMC",
            message="Your family event and memory space has been initialized.",
            family_context_id=self.family_context.id,
        )

        # 10. Celebration Artifact
        self.celebration1 = self.api.build_celebration_artifact_for_event_for_session(
            session_id=self.session_id,
            event_id=self.event1.id,
            attach_as_media=False,
        )

        # 11. Mayil AI Insight
        self.insight = self.api.analyze_family_insights_for_session(self.session_id, self.family_context.id)


demo_state = DemoState()


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FEMC — Family Event & Memory Calendar</title>
    <style>
        :root {
            --bg: #0f172a;
            --panel: #1e293b;
            --panel-border: #334155;
            --accent: #38bdf8;
            --accent-hover: #0284c7;
            --text: #f8fafc;
            --text-sub: #94a3b8;
            --success: #22c55e;
            --warning: #f59e0b;
            --danger: #ef4444;
            --card-bg: #162032;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        body { background: var(--bg); color: var(--text); display: flex; height: 100vh; overflow: hidden; }

        #sidebar { width: 260px; background: var(--panel); border-right: 1px solid var(--panel-border); display: flex; flex-direction: column; }
        .brand { padding: 20px; border-bottom: 1px solid var(--panel-border); }
        .brand h1 { font-size: 20px; color: var(--accent); letter-spacing: -0.5px; display: flex; align-items: center; gap: 8px; }
        .brand h2 { font-size: 12px; color: var(--text-sub); font-weight: normal; margin-top: 4px; }
        .brand .badge { display: inline-block; background: rgba(56, 189, 248, 0.15); color: var(--accent); padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-top: 8px; font-weight: 600; }

        .nav-list { list-style: none; padding: 12px; flex: 1; overflow-y: auto; }
        .nav-item { margin-bottom: 4px; }
        .nav-link { display: flex; align-items: center; gap: 10px; padding: 10px 14px; border-radius: 6px; color: var(--text-sub); text-decoration: none; font-size: 14px; cursor: pointer; transition: all 0.2s; }
        .nav-link:hover, .nav-link.active { background: rgba(255,255,255,0.05); color: var(--text); }
        .nav-link.active { color: var(--accent); font-weight: 600; background: rgba(56, 189, 248, 0.1); }

        .reset-box { padding: 16px; border-top: 1px solid var(--panel-border); }
        .btn { display: inline-flex; align-items: center; justify-content: center; gap: 6px; padding: 8px 14px; border-radius: 6px; border: none; font-weight: 600; cursor: pointer; font-size: 13px; transition: all 0.2s; text-align: center; }
        .btn-primary { background: var(--accent); color: #000; }
        .btn-primary:hover { background: var(--accent-hover); }
        .btn-outline { background: transparent; border: 1px solid var(--panel-border); color: var(--text-sub); }
        .btn-outline:hover { background: rgba(255,255,255,0.05); color: var(--text); }
        .btn-sm { padding: 4px 10px; font-size: 12px; }

        #main { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
        .topbar { height: 60px; border-bottom: 1px solid var(--panel-border); display: flex; align-items: center; justify-content: space-between; padding: 0 24px; background: var(--panel); }
        .user-info { font-size: 13px; color: var(--text-sub); display: flex; align-items: center; gap: 16px; }
        .user-info span { color: var(--text); font-weight: 600; }

        .content { flex: 1; padding: 24px; overflow-y: auto; }
        .page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
        .section-title { font-size: 22px; font-weight: 600; color: var(--text); }
        .section-subtitle { font-size: 13px; color: var(--text-sub); margin-top: 4px; }

        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px; margin-bottom: 24px; }
        .card { background: var(--card-bg); border: 1px solid var(--panel-border); border-radius: 10px; padding: 20px; }
        .card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
        .card-title { font-size: 15px; font-weight: 600; color: var(--accent); display: flex; align-items: center; gap: 8px; }

        .pill { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; text-transform: uppercase; }
        .pill-birthday { background: rgba(236, 72, 153, 0.2); color: #f472b6; border: 1px solid rgba(236, 72, 153, 0.4); }
        .pill-anniversary { background: rgba(168, 85, 247, 0.2); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.4); }
        .pill-milestone { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }
        .pill-general { background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); }
        .pill-health { background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.4); }
        .pill-unread { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); }
        .pill-read { background: rgba(148, 163, 184, 0.2); color: #94a3b8; border: 1px solid rgba(148, 163, 184, 0.4); }

        .item-list { list-style: none; }
        .item-row { padding: 12px; border-bottom: 1px solid var(--panel-border); display: flex; justify-content: space-between; align-items: center; }
        .item-row:last-child { border-bottom: none; }
        .item-main { font-weight: 500; font-size: 14px; color: var(--text); }
        .item-sub { font-size: 12px; color: var(--text-sub); margin-top: 2px; }

        .timeline { border-left: 2px solid var(--panel-border); padding-left: 20px; margin-left: 10px; }
        .timeline-item { position: relative; margin-bottom: 24px; }
        .timeline-item::before { content: ''; position: absolute; left: -27px; top: 4px; width: 12px; height: 12px; border-radius: 50%; background: var(--accent); }

        .celebration-card { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border: 1px solid var(--accent); border-radius: 12px; padding: 24px; position: relative; overflow: hidden; }
        .celebration-banner { font-size: 20px; font-weight: 700; color: var(--accent); margin-bottom: 8px; }

        details { margin-top: 20px; background: #090d16; border: 1px solid var(--panel-border); border-radius: 6px; padding: 12px; }
        summary { font-size: 12px; color: var(--text-sub); font-weight: 600; cursor: pointer; outline: none; }
        pre { font-family: monospace; font-size: 11px; color: #94a3b8; margin-top: 10px; overflow-x: auto; max-height: 300px; }
    </style>
</head>
<body>
    <div id="sidebar">
        <div class="brand">
            <h1>🏠 FEMC</h1>
            <h2>Family Event & Memory Calendar</h2>
            <div class="badge">v1.0 First User Experience Demo</div>
        </div>
        <ul class="nav-list">
            <li class="nav-item"><a class="nav-link active" onclick="loadView('home', event)">🏠 HOME</a></li>
            <li class="nav-item"><a class="nav-link" onclick="loadView('family', event)">👨‍👩‍👧‍👦 FAMILY</a></li>
            <li class="nav-item"><a class="nav-link" onclick="loadView('calendar', event)">📅 CALENDAR</a></li>
            <li class="nav-item"><a class="nav-link" onclick="loadView('memories', event)">📖 MEMORIES</a></li>
            <li class="nav-item"><a class="nav-link" onclick="loadView('celebrations', event)">🎉 CELEBRATIONS</a></li>
            <li class="nav-item"><a class="nav-link" onclick="loadView('reminders', event)">🔔 REMINDERS</a></li>
            <li class="nav-item"><a class="nav-link" onclick="loadView('mayil', event)">🧠 MAYIL AI</a></li>
            <li class="nav-item"><a class="nav-link" onclick="loadView('settings', event)">⚙️ SETTINGS / DATA</a></li>
        </ul>
        <div class="reset-box">
            <button class="btn btn-outline" onclick="resetDemoState()">🔄 Recreate Demo State</button>
        </div>
    </div>
    <div id="main">
        <div class="topbar">
            <div class="user-info">
                <div>Active Family: <span id="sess-ctx">Smith Family</span></div>
                <div>User: <span id="sess-user">Alice Smith</span></div>
            </div>
            <div style="font-size:12px; color:var(--text-sub); display:flex; align-items:center; gap:8px;">
                <span class="pill pill-health">🛡️ VEL Guardian Healthy</span>
            </div>
        </div>
        <div class="content" id="content-area">
            <!-- Dynamic View Content -->
        </div>
    </div>

    <script>
        let currentView = 'home';

        async function fetchAPI(endpoint, options={}) {
            try {
                const res = await fetch(endpoint, options);
                return await res.json();
            } catch (e) {
                return { error: e.message };
            }
        }

        async function resetDemoState() {
            if (confirm("Reset demo data to deterministic initial state?")) {
                await fetchAPI('/api/reset', { method: 'POST' });
                loadView(currentView);
            }
        }

        function setActiveNav(evt) {
            if (!evt) return;
            document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));
            evt.currentTarget.classList.add('active');
        }

        function getCategoryBadge(category) {
            const cat = (category || '').toLowerCase();
            if (cat === 'birthday') return '<span class="pill pill-birthday">🎂 BIRTHDAY</span>';
            if (cat === 'anniversary') return '<span class="pill pill-anniversary">💍 ANNIVERSARY</span>';
            if (cat === 'milestone') return '<span class="pill pill-milestone">⭐ MILESTONE</span>';
            return '<span class="pill pill-general">📅 GENERAL</span>';
        }

        async function loadView(view, evt) {
            currentView = view;
            if (evt) setActiveNav(evt);
            const area = document.getElementById('content-area');
            area.innerHTML = '<div style="color:var(--text-sub)">Loading...</div>';

            if (view === 'home') {
                const dash = await fetchAPI('/api/dashboard');
                const entries = dash.entries || [];

                // Filter dashboard entries into distinct semantic categories to prevent semantic mixing
                const getItemType = e => e.item_type || e.entry_type || '';
                const getDateOrTime = e => e.date_or_time || e.date || '';

                const eventsList = entries.filter(e => getItemType(e) === 'upcoming_event' || getItemType(e) === 'recurring_event');
                const remindersList = entries.filter(e => getItemType(e) === 'due_reminder');
                const memoriesList = entries.filter(e => getItemType(e) === 'recent_memory');
                const celebrationsList = entries.filter(e => getItemType(e) === 'celebration_highlight');

                let eventsHTML = eventsList.map(e => `
                    <div class="item-row">
                        <div>
                            <div class="item-main">${e.title}</div>
                            <div class="item-sub">${getDateOrTime(e)}</div>
                        </div>
                        <span class="pill pill-general">${e.visibility || 'family'}</span>
                    </div>
                `).join('');

                let remindersHTML = remindersList.map(e => `
                    <div class="item-row">
                        <div>
                            <div class="item-main">${e.title}</div>
                            <div class="item-sub">${e.subtitle || 'Offset 60 mins'}</div>
                        </div>
                        <span class="pill pill-birthday">DUE SOON</span>
                    </div>
                `).join('');

                let memoriesHTML = memoriesList.map(e => `
                    <div class="item-row">
                        <div>
                            <div class="item-main">" ${e.title} "</div>
                            <div class="item-sub">Shared Family Memory</div>
                        </div>
                    </div>
                `).join('');

                let celebrationsHTML = celebrationsList.map(e => `
                    <div class="item-row">
                        <div>
                            <div class="item-main">🎂 ${e.title}</div>
                            <div class="item-sub">Celebration Highlight</div>
                        </div>
                        <span class="pill pill-milestone">CELEBRATION</span>
                    </div>
                `).join('');

                area.innerHTML = `
                    <div class="page-header">
                        <div>
                            <div class="section-title">Welcome Home, Alice</div>
                            <div class="section-subtitle">Smith Family Memory & Event Overview</div>
                        </div>
                    </div>
                    <div class="grid">
                        <div class="card">
                            <div class="card-header"><div class="card-title">📅 Upcoming Family Events</div></div>
                            <div class="item-list">
                                ${eventsHTML || '<div class="item-sub">No upcoming events scheduled.</div>'}
                            </div>
                        </div>
                        <div class="card">
                            <div class="card-header"><div class="card-title">🔔 Reminders / Needs Attention</div></div>
                            <div class="item-list">
                                ${remindersHTML || '<div class="item-sub">No active reminders due.</div>'}
                            </div>
                        </div>
                    </div>
                    <div class="grid">
                        <div class="card">
                            <div class="card-header"><div class="card-title">📖 Recent Family Memories</div></div>
                            <div class="item-list">
                                ${memoriesHTML || '<div class="item-sub">No recent memories.</div>'}
                            </div>
                        </div>
                        <div class="card">
                            <div class="card-header"><div class="card-title">🎉 Celebration Highlights</div></div>
                            <div class="item-list">
                                ${celebrationsHTML || '<div class="item-sub">No celebration highlights.</div>'}
                            </div>
                        </div>
                    </div>
                    <div class="card" style="margin-bottom:20px;">
                        <div class="card-header"><div class="card-title">💡 Mayil AI Spotlight</div></div>
                        <div style="font-size:14px; line-height:1.5; color:var(--text-sub);">
                            "Mayil noticed 2 upcoming events and 1 shared memory for the Smith Family context."
                        </div>
                    </div>
                    <details>
                        <summary>Technical Details (Raw JSON Payload)</summary>
                        <pre>${JSON.stringify(dash, null, 2)}</pre>
                    </details>
                `;
            } else if (view === 'family') {
                const data = await fetchAPI('/api/family');

                area.innerHTML = `
                    <div class="page-header">
                        <div>
                            <div class="section-title">Smith Family Members</div>
                            <div class="section-subtitle">Authorized Family Context & Relationships</div>
                        </div>
                    </div>
                    <div class="grid">
                        <div class="card">
                            <div class="card-header"><div class="card-title">👤 Alice Smith</div><span class="pill pill-general">Account Owner</span></div>
                            <div class="item-sub">Born: 15 May 1990</div>
                            <div class="item-sub">Email: alice@example.com</div>
                            <div class="item-sub" style="margin-top:8px;">Associated Events: Alice's Birthday Celebration, Smith Family Weekend Dinner</div>
                        </div>
                        <div class="card">
                            <div class="card-header"><div class="card-title">👤 Bob Smith</div><span class="pill pill-milestone">Partner</span></div>
                            <div class="item-sub">Born: 20 Oct 1988</div>
                            <div class="item-sub">Email: bob@example.com</div>
                            <div class="item-sub" style="margin-top:8px;">Associated Events: Smith Family Weekend Dinner</div>
                        </div>
                    </div>
                    <details>
                        <summary>Technical Details (Family Topology & Rich Person Detail)</summary>
                        <pre>${JSON.stringify(data, null, 2)}</pre>
                    </details>
                `;
            } else if (view === 'calendar') {
                const data = await fetchAPI('/api/events');
                const cal = data.calendar || [];

                let calHTML = cal.map(item => `
                    <div class="item-row">
                        <div>
                            <div class="item-main">${item.title}</div>
                            <div class="item-sub">${item.date || item.start_time || ''}</div>
                        </div>
                        ${getCategoryBadge(item.category || (item.title.includes('Birthday') ? 'birthday' : 'general'))}
                    </div>
                `).join('');

                area.innerHTML = `
                    <div class="page-header">
                        <div>
                            <div class="section-title">Family Calendar</div>
                            <div class="section-subtitle">Scheduled Family Events & Milestones</div>
                        </div>
                        <button class="btn btn-primary" onclick="createEventPrompt()">+ Schedule Event</button>
                    </div>
                    <div class="card" style="margin-bottom:20px;">
                        <div class="card-header"><div class="card-title">📅 Event Agenda</div></div>
                        <div class="item-list">${calHTML}</div>
                    </div>
                    <details>
                        <summary>Technical Details (Calendar Projections & Rich Details)</summary>
                        <pre>${JSON.stringify(data, null, 2)}</pre>
                    </details>
                `;
            } else if (view === 'memories') {
                const data = await fetchAPI('/api/timeline');
                const evMem = data.event_memories || {};

                let memHTML = (evMem.memories || []).map(m => `
                    <div class="timeline-item">
                        <div class="item-main">" ${m.narrative} "</div>
                        <div class="item-sub">Linked Event: ${evMem.event ? evMem.event.title : 'Family Event'} • Author: Alice Smith</div>
                    </div>
                `).join('');

                area.innerHTML = `
                    <div class="page-header">
                        <div>
                            <div class="section-title">Family Memories & Timeline</div>
                            <div class="section-subtitle">Chronological Family Stories & Narratives</div>
                        </div>
                        <button class="btn btn-primary" onclick="createMemoryPrompt()">+ Add Memory</button>
                    </div>
                    <div class="card">
                        <div class="card-header"><div class="card-title">📖 Memory Narrative Stories</div></div>
                        <div class="timeline" style="margin-top:16px;">${memHTML || '<div class="item-sub">No memories recorded yet.</div>'}</div>
                    </div>
                    <details>
                        <summary>Technical Details (Timeline Entries & Memory Models)</summary>
                        <pre>${JSON.stringify(data, null, 2)}</pre>
                    </details>
                `;
            } else if (view === 'celebrations') {
                const data = await fetchAPI('/api/celebrations');
                const arts = data.artifacts || [];

                let artHTML = arts.map(art => `
                    <div class="celebration-card">
                        <div class="celebration-banner">🎂 ${art.title || 'Family Celebration'}</div>
                        <div style="font-size:14px; color:var(--text-sub); margin-bottom:12px;">${art.rendered_content || ''}</div>
                        <div class="item-sub">Artifact Type: ${art.artifact_type} • Visibility: ${art.visibility || 'family'}</div>
                    </div>
                `).join('');

                area.innerHTML = `
                    <div class="page-header">
                        <div>
                            <div class="section-title">Celebration Studio</div>
                            <div class="section-subtitle">Derived Family Celebration Cards & Artifacts</div>
                        </div>
                    </div>
                    <div class="grid">${artHTML}</div>
                    <details>
                        <summary>Technical Details (Celebration Artifact Objects)</summary>
                        <pre>${JSON.stringify(data, null, 2)}</pre>
                    </details>
                `;
            } else if (view === 'reminders') {
                const data = await fetchAPI('/api/reminders');
                const notifs = data.notifications || [];

                let notifHTML = notifs.map(n => `
                    <div class="item-row">
                        <div>
                            <div class="item-main">${n.title}</div>
                            <div class="item-sub">${n.message}</div>
                        </div>
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span class="pill ${n.status === 'unread' ? 'pill-unread' : 'pill-read'}">${n.status}</span>
                            ${n.status === 'unread' ? `<button class="btn btn-sm btn-outline" onclick="markNotificationRead('${n.id}')">Mark Read</button>` : ''}
                        </div>
                    </div>
                `).join('');

                area.innerHTML = `
                    <div class="page-header">
                        <div>
                            <div class="section-title">Reminders & Notifications</div>
                            <div class="section-subtitle">Active Family Alerts & Triggered Event Reminders</div>
                        </div>
                    </div>
                    <div class="card">
                        <div class="card-header"><div class="card-title">🔔 Active Notifications & Event Reminders</div></div>
                        <div class="item-list">${notifHTML}</div>
                    </div>
                    <details>
                        <summary>Technical Details (Notifications & Reminder Configurations)</summary>
                        <pre>${JSON.stringify(data, null, 2)}</pre>
                    </details>
                `;
            } else if (view === 'mayil') {
                const data = await fetchAPI('/api/mayil');
                const insight = data.insight || {};
                const props = data.proposals || [];

                let propHTML = props.length > 0 ? props.map(p => `
                    <div class="item-row">
                        <div>
                            <div class="item-main">${p.title}</div>
                            <div class="item-sub">${p.reasoning}</div>
                        </div>
                        <button class="btn btn-sm btn-primary" onclick="approveProposal('${p.id}')">Approve</button>
                    </div>
                `).join('') : '<div class="item-sub">No action proposals currently recommended.</div>';

                area.innerHTML = `
                    <div class="page-header">
                        <div>
                            <div class="section-title">Mayil AI Engine</div>
                            <div class="section-subtitle">Read-Only Family Activity Insights & Action Proposals</div>
                        </div>
                    </div>
                    <div class="grid">
                        <div class="card">
                            <div class="card-header"><div class="card-title">💡 Mayil Noticed...</div></div>
                            <div style="font-size:14px; color:var(--text-sub); line-height:1.6;">
                                ${insight.analysis_summary || 'Mayil noticed family event activity in the Smith Family context.'}
                            </div>
                        </div>
                        <div class="card">
                            <div class="card-header"><div class="card-title">✨ Mayil Suggests...</div></div>
                            <div class="item-list">${propHTML}</div>
                        </div>
                    </div>
                    <details>
                        <summary>Technical Details (Insight Analysis & Proposals)</summary>
                        <pre>${JSON.stringify(data, null, 2)}</pre>
                    </details>
                `;
            } else if (view === 'settings') {
                const data = await fetchAPI('/api/export');
                const val = data.validation || {};
                const exp = data.export || {};

                area.innerHTML = `
                    <div class="page-header">
                        <div>
                            <div class="section-title">Settings & Data Portability</div>
                            <div class="section-subtitle">Constitutional Data Ownership & Schema Validation</div>
                        </div>
                    </div>
                    <div class="grid">
                        <div class="card">
                            <div class="card-header"><div class="card-title">🛡️ Data Integrity Status</div><span class="pill pill-health">VALID</span></div>
                            <div class="item-sub">Family Context Export Schema: Version 1.0</div>
                            <div class="item-sub">Validation Errors: ${val.errors ? val.errors.length : 0}</div>
                        </div>
                        <div class="card">
                            <div class="card-header"><div class="card-title">📦 Export Summary</div></div>
                            <div class="item-sub">Family Context ID: ${exp.family_context_id || ''}</div>
                            <div class="item-sub">Records Exported: ${exp.records ? Object.keys(exp.records).length : 0} categories</div>
                        </div>
                    </div>
                    <details>
                        <summary>Technical Details (Export Payload & Schema Audit)</summary>
                        <pre>${JSON.stringify(data, null, 2)}</pre>
                    </details>
                `;
            }
        }

        async function createEventPrompt() {
            const title = prompt("Enter event title:", "Family Game Night");
            if (title) {
                await fetchAPI('/api/events/create', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title: title, description: "Scheduled family gathering" })
                });
                loadView('calendar');
            }
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
            });
            loadView('mayil');
        }

        loadView('home');
    </script>
</body>
</html>
"""


class DemoHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":
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
                "account_id": demo_state.acc_alice.id,
                "person_id": demo_state.p_alice.id,
                "family_context_id": fc_id,
            }
            self._send_json(res)
        elif path == "/api/dashboard":
            summary = api.get_dashboard_summary_for_session(session_id, fc_id)
            entries = api.get_dashboard_projection_for_session(session_id, fc_id)
            self._send_json({"summary": to_dict(summary), "entries": to_dict(entries)})
        elif path == "/api/family":
            topology = api.get_family_topology_for_session(session_id, fc_id)
            alice_detail = api.build_rich_person_detail_for_session(session_id, demo_state.p_alice.id)
            self._send_json({"topology": to_dict(topology), "alice_detail": to_dict(alice_detail)})
        elif path == "/api/events":
            calendar = api.get_calendar_for_session(session_id, fc_id)
            detail = api.build_rich_event_detail_for_session(session_id, demo_state.event1.id)
            self._send_json({"calendar": to_dict(calendar), "event_detail": to_dict(detail)})
        elif path == "/api/timeline":
            timeline = api.get_timeline_for_session(session_id, fc_id)
            event_memories = api.get_event_with_memories_for_session(session_id, demo_state.event1.id)
            self._send_json({"timeline": to_dict(timeline), "event_memories": to_dict(event_memories)})
        elif path == "/api/celebrations":
            artifacts = api.list_celebration_artifacts_for_session(session_id, fc_id)
            self._send_json({"artifacts": to_dict(artifacts)})
        elif path == "/api/reminders":
            notifs = api.list_notifications_for_session(session_id)
            triggered = api.trigger_due_reminders_for_session(session_id, fc_id)
            self._send_json({"notifications": to_dict(notifs), "triggered": to_dict(triggered)})
        elif path == "/api/mayil":
            insight = api.analyze_family_insights_for_session(session_id, fc_id)
            proposals = api.get_action_proposals_for_session(session_id, fc_id)
            self._send_json({"insight": to_dict(insight), "proposals": to_dict(proposals)})
        elif path == "/api/guardian":
            audit = api.run_integrity_audit_for_session(session_id, fc_id)
            proposals = api.get_repair_proposals_for_session(session_id, fc_id)
            self._send_json({"audit": to_dict(audit), "repair_proposals": to_dict(proposals)})
        elif path == "/api/export":
            export_data = api.export_family_context_for_session(session_id, fc_id)
            validation = api.validate_data_export(to_dict(export_data))
            self._send_json({"export": to_dict(export_data), "validation": to_dict(validation)})
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

        if path == "/api/events/create":
            title = payload.get("title", "New Event")
            desc = payload.get("description", "")
            now = _utc_now()
            event = api.create_event_for_session(
                session_id=session_id,
                title=title,
                description=desc,
                family_context_id=fc_id,
                start_time=now + datetime.timedelta(days=1),
                end_time=now + datetime.timedelta(days=1, hours=2),
                visibility=VisibilityLevel.FAMILY,
            )
            self._send_json({"status": "success", "event": to_dict(event)})
        elif path == "/api/memories/create":
            narrative = payload.get("narrative", "Shared memory")
            memory = api.create_memory_for_session(
                session_id=session_id,
                event_id=demo_state.event1.id,
                narrative=narrative,
                visibility=VisibilityLevel.FAMILY,
            )
            self._send_json({"status": "success", "memory": to_dict(memory)})
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
