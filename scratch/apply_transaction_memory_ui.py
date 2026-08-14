import os, sys

code = open('run.py', encoding='utf-8').read()

# 1. Update DemoState.__init__ to seed realistic transaction records
if 'def seed_demo_transactions' not in code:
    old_ds_init = "self.event1 = self.api.create_event_for_session("
    new_ds_init = """self.seed_demo_transactions()
        self.event1 = self.api.create_event_for_session("""

    seed_method = """
    def seed_demo_transactions(self):
        sess_id = self.session_alice.session_id
        fc_id = self.family_context.id
        cid = "demo-journey-chain-1"

        from ENGINEERING.source.femc.models import ActionType, ResourceType, VisibilityLevel

        # 1. Add Person
        self.api.record_transaction_for_session(
            session_id=sess_id, family_context_id=fc_id, action_type=ActionType.CREATE,
            resource_type=ResourceType.PERSON, resource_id=self.person_alice.id,
            resource_label_snapshot="Alice Smith", operation="Added Alice Smith to family group",
            correlation_id=cid
        )
        # 2. Schedule Event
        self.api.record_transaction_for_session(
            session_id=sess_id, family_context_id=fc_id, action_type=ActionType.CREATE,
            resource_type=ResourceType.EVENT, resource_id=self.event1.id,
            resource_label_snapshot="Grandma's 80th Birthday", operation="Scheduled family birthday dinner for Aug 20",
            correlation_id=cid
        )
        # 3. Attach Photos
        self.api.record_transaction_for_session(
            session_id=sess_id, family_context_id=fc_id, action_type=ActionType.ATTACH,
            resource_type=ResourceType.MEDIA, resource_id=self.media1.id,
            resource_label_snapshot="Birthday Cake & Candles Photo", operation="Attached photo to Grandma's 80th Birthday",
            correlation_id=cid
        )
        # 4. Create Memory Story
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
"""
    code = code.replace("class DemoState:", "class DemoState:\n" + seed_method)
    code = code.replace(old_ds_init, new_ds_init)

# 2. Add nav-history item to nav ribbon
if 'id="nav-history"' not in code:
    old_nav_settings = '<a id="nav-settings"'
    new_nav_item = """<a id="nav-history" class="nav-link" tabindex="0" onclick="loadView('history', event)" onkeydown="if(event.key==='Enter'||event.key===' ')loadView('history', event)">
            <span class="nav-icon">🕘</span>
            <div class="nav-text">
                <span class="nav-title">ACTIVITY</span>
                <span class="nav-subtitle">Audit & History</span>
            </div>
        </a>\n        <a id="nav-settings" """
    code = code.replace(old_nav_settings, new_nav_item)

# 3. Add API endpoints in DemoHTTPRequestHandler
if '/api/history' not in code:
    old_endpoint_handle = "elif self.path == '/api/export':"
    new_endpoints = """elif self.path == '/api/history':
            session = self.demo_state.api._validate_session(self.demo_state.session_id)
            history = self.demo_state.api.get_transaction_history_for_session(
                session.session_id, self.demo_state.family_context.id, limit=50
            )
            res = [r.__dict__ for r in history]
            # Convert datetime & enums for JSON serialization
            for r in res:
                r['timestamp'] = r['timestamp'].isoformat()
                r['action_type'] = str(r['action_type'])
                r['resource_type'] = str(r['resource_type'])
                r['visibility'] = str(r['visibility'])
            self._send_json({"transactions": res})
            return
        elif self.path.startswith('/api/resource_history'):
            session = self.demo_state.api._validate_session(self.demo_state.session_id)
            from urllib.parse import parse_qs, urlparse
            query = parse_qs(urlparse(self.path).query)
            res_type = query.get('type', ['event'])[0]
            res_id = query.get('id', [''])[0]
            
            from ENGINEERING.source.femc.models import ResourceType
            try:
                rt = ResourceType(res_type.lower())
            except Exception:
                rt = ResourceType.EVENT

            explanation = self.demo_state.api.explain_resource_history_for_session(
                session.session_id, self.demo_state.family_context.id, rt, res_id
            )
            self._send_json(explanation)
            return
        elif self.path == '/api/export':"""
    code = code.replace(old_endpoint_handle, new_endpoints)

# 4. Add renderHistory function & update loadView routing
if 'async function renderHistory(' not in code:
    old_load_view_route = "else if (viewName === 'settings') await renderSettings(content);"
    new_load_view_route = """else if (viewName === 'history') await renderHistory(content);
            else if (viewName === 'settings') await renderSettings(content);"""
    code = code.replace(old_load_view_route, new_load_view_route)

    render_history_js = """
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
"""
    code = code.replace("async function renderHome(container) {", render_history_js + "\n\n        async function renderHome(container) {")

with open('run.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Applied transaction memory UI upgrades to run.py!")
