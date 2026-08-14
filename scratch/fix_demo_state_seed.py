import os, sys

code = open('run.py', encoding='utf-8').read()

# Fix seed_demo_transactions method in run.py
old_seed = """    def seed_demo_transactions(self):
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
        )"""

new_seed = """    def seed_demo_transactions(self):
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
        )"""

code = code.replace(old_seed, new_seed)

# Move self.seed_demo_transactions() to end of reset()
code = code.replace(
    "self.seed_demo_transactions()\n        self.event1 = self.api.create_event_for_session(",
    "self.event1 = self.api.create_event_for_session("
)

if 'self.seed_demo_transactions()' not in code.split('def reset(self):')[1].split('def ')[0]:
    old_reset_end = "self.api.dashboard.rebuild_dashboard_projections(self.family_context.id)"
    new_reset_end = "self.api.dashboard.rebuild_dashboard_projections(self.family_context.id)\n        self.seed_demo_transactions()"
    code = code.replace(old_reset_end, new_reset_end)

with open('run.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Fixed seed_demo_transactions in run.py!")
