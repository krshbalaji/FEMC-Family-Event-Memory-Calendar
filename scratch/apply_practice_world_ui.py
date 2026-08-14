import os, sys

code = open('run.py', encoding='utf-8').read()

# 1. Add GET endpoint for practice world status
if '/api/guide/practice/status' not in code:
    old_get = 'elif path == "/api/guide/status":'
    new_get = """elif path == "/api/guide/practice/status":
            session = demo_state.api._validate_session(demo_state.session_id)
            pw = demo_state.api.get_practice_world_state_for_session(session.session_id)
            if not pw:
                pw = demo_state.api.start_practice_world_for_session(session.session_id, demo_state.family_context.id)
            self._send_json({"practice_world": to_dict(pw)})
            return
        elif path == "/api/guide/status":"""
    code = code.replace(old_get, new_get)

# 2. Add POST endpoints for practice world actions
if 'elif path == "/api/guide/practice/start":' not in code:
    old_post = 'if path == "/api/guide/init":'
    new_post = """if path == "/api/guide/practice/start":
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
        elif path == "/api/guide/init":"""
    code = code.replace(old_post, new_post)

# 3. Add Practice World Header Banner CSS & HTML Banner Container
if 'id="practice-world-header-banner"' not in code:
    banner_css = """
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
    """
    code = code.replace(".target-glow {", banner_css + "\n        .target-glow {")

    banner_html = """
    <!-- MAYIL PRACTICE WORLD HEADER BANNER -->
    <div id="practice-world-header-banner" class="practice-world-banner" style="display:none;">
        <div style="display:flex; align-items:center; gap:0.75rem;">
            <span style="font-size:1.5rem;">🎮</span>
            <div>
                <strong style="font-size:1rem; color:var(--pink);">MAYIL'S PRACTICE WORLD (SAFE TRAINING SIMULATION)</strong>
                <div style="font-size:0.8rem; color:var(--text-sub);">Zero mutation on real data • Practice creating events, memories, media & celebrations safely</div>
            </div>
        </div>
        <div style="display:flex; gap:0.6rem;">
            <button class="btn btn-outline" style="font-size:0.8rem; border-color:var(--pink); color:var(--pink);" onclick="resetPracticeWorldUI()">🔄 Reset Practice</button>
            <button class="btn btn-pink" style="font-size:0.8rem;" onclick="exitPracticeWorldUI()">← Exit to Real FEMC</button>
        </div>
    </div>
    """
    code = code.replace('<main class="femc-main">', '<main class="femc-main">\n' + banner_html)

with open('run.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Applied Practice World UI & API endpoints to run.py!")
