import os, sys

code = open('run.py', encoding='utf-8').read()

# 1. Add API endpoints for guided experience
if '/api/guide/init' not in code:
    old_endpoints = "elif path == \"/api/export\":"
    new_endpoints = """elif path == "/api/guide/status":
            session = demo_state.api._validate_session(demo_state.session_id)
            st = demo_state.api.get_guided_experience_state_for_session(session.session_id)
            if not st:
                st = demo_state.api.initialize_guided_experience_for_session(session.session_id, demo_state.family_context.id)
            scenes = demo_state.api.get_shared_journey_scenes_for_session(session.session_id)
            scenes_dict = [s.__dict__ for s in scenes]
            self._send_json({"session_state": st.__dict__, "scenes": scenes_dict})
            return
        elif path == "/api/export":"""
    code = code.replace(old_endpoints, new_endpoints)

if 'elif path == "/api/guide/init":' not in code:
    old_post = "if path == \"/api/session/switch\":"
    new_post = """if path == "/api/guide/init":
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
            self._send_json({"status": "success", "session_state": st.__dict__, "scenes": [s.__dict__ for s in scenes]})
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
            self._send_json(res)
            return
        elif path == "/api/guide/switch_mode":
            session = demo_state.api._validate_session(demo_state.session_id)
            from ENGINEERING.source.femc.models import GuideMode
            mode_str = payload.get("mode", "learn_by_doing").lower()
            try: mode = GuideMode(mode_str)
            except Exception: mode = GuideMode.LEARN_BY_DOING

            st = demo_state.api.switch_guided_experience_mode_for_session(session.session_id, mode)
            self._send_json({"status": "success", "session_state": st.__dict__})
            return
        elif path == "/api/guide/reset":
            session = demo_state.api._validate_session(demo_state.session_id)
            st = demo_state.api.reset_guided_experience_for_session(session.session_id)
            self._send_json({"status": "success", "session_state": st.__dict__})
            return
        elif path == "/api/session/switch":"""
    code = code.replace(old_post, new_post)

# 2. Add Target Highlight & Guidance Banner CSS
if '.target-glow' not in code:
    old_css = "</style>"
    new_css = """
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
    </style>"""
    code = code.replace(old_css, new_css)

# 3. Add Onboarding Welcome Modal HTML & Guided Experience JS
if 'id="guide-onboarding-modal"' not in code:
    onboarding_html = """
    <!-- V2.3-D MAYIL LEARN-BY-DOING + LIVING DEMO ONBOARDING MODAL -->
    <div id="guide-onboarding-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); z-index:10000; justify-content:center; align-items:center; backdrop-filter:blur(6px);">
        <div class="modal-card" style="max-width:540px; width:90%; background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); border: 2px solid var(--purple); box-shadow: 0 0 30px rgba(192, 132, 252, 0.3);">
            <div style="text-align:center; margin-bottom:1.25rem;">
                <div style="font-size:2.8rem; margin-bottom:0.4rem;">🦚</div>
                <h2 style="font-size:1.4rem; color:var(--text-main); font-weight:800;">Welcome to FEMC with Mayil</h2>
                <div style="font-size:0.85rem; color:var(--accent); font-weight:600; margin-top:0.2rem;">Don't just watch FEMC. Let's build something together.</div>
            </div>

            <div style="margin-bottom:1rem;">
                <label style="font-size:0.8rem; font-weight:700; color:var(--text-sub); display:block; margin-bottom:0.3rem;">1. What is FEMC for you?</label>
                <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:0.5rem;">
                    <button class="btn btn-outline" id="ctx-family" onclick="selectContext('family')">👨‍👩‍👧‍👦 Family</button>
                    <button class="btn btn-outline" id="ctx-friends" onclick="selectContext('friends')">👫 Friends</button>
                    <button class="btn btn-outline" id="ctx-community" onclick="selectContext('community')">🌍 Community</button>
                </div>
            </div>

            <div style="margin-bottom:1rem;">
                <label style="font-size:0.8rem; font-weight:700; color:var(--text-sub); display:block; margin-bottom:0.3rem;">2. Preferred Language</label>
                <select id="guide-lang-select" class="btn btn-outline" style="width:100%; text-align:left;">
                    <option value="en">🌐 English (Original)</option>
                    <option value="ta">🇮🇳 தமிழ் (Tamil)</option>
                    <option value="hi">🇮🇳 हिंदी (Hindi)</option>
                </select>
            </div>

            <div style="margin-bottom:1.25rem;">
                <label style="font-size:0.8rem; font-weight:700; color:var(--text-sub); display:block; margin-bottom:0.3rem;">3. Choose Experience Mode</label>
                <div style="display:flex; flex-direction:column; gap:0.6rem;">
                    <div style="background:rgba(192, 132, 252, 0.15); border:1px solid var(--purple); padding:0.8rem; border-radius:8px; cursor:pointer;" onclick="startGuidedExperience('learn_by_doing')">
                        <div style="font-weight:700; color:var(--pink); font-size:0.95rem;">🎓 LEARN BY DOING (Recommended)</div>
                        <div style="font-size:0.78rem; color:var(--text-sub); margin-top:0.2rem;">Mayil guides you step-by-step to operate real FEMC calendar, memories, media and celebrations.</div>
                    </div>
                    <div style="background:rgba(56, 189, 248, 0.1); border:1px solid var(--accent); padding:0.8rem; border-radius:8px; cursor:pointer;" onclick="startGuidedExperience('watch_journey')">
                        <div style="font-weight:700; color:var(--accent); font-size:0.95rem;">🎬 WATCH MAYIL'S JOURNEY</div>
                        <div style="font-size:0.78rem; color:var(--text-sub); margin-top:0.2rem;">Cinematic animated journey demonstrating FEMC capabilities with 'Try It Yourself' interactive transitions.</div>
                    </div>
                </div>
            </div>

            <div style="text-align:right;">
                <button class="btn btn-pink" style="width:100%; font-size:1rem; padding:0.6rem;" onclick="startGuidedExperience('learn_by_doing')">🚀 Start Guided Journey</button>
            </div>
        </div>
    </div>
    """
    code = code.replace("</body>", onboarding_html + "\n</body>")

with open('run.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Applied V2.3-D UI HTML & API endpoints to run.py!")
