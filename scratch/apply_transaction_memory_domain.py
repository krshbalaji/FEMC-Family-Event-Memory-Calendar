import os, sys

# 1. Update services.py
services_code = open('ENGINEERING/source/femc/services.py', encoding='utf-8').read()

# Add imports for ActionType, ResourceType, TransactionRecord, TransactionMemoryRepository
if 'TransactionRecord' not in services_code:
    services_code = services_code.replace(
        'from .models import (',
        'from .models import (\n    ActionType,\n    ResourceType,\n    TransactionRecord,'
    )
    services_code = services_code.replace(
        'from .repositories import CanonicalRepository, DerivedRepository',
        'from .repositories import CanonicalRepository, DerivedRepository, TransactionMemoryRepository'
    )

# Append TransactionMemoryService at end of services.py
tx_service_class = """

class TransactionMemoryService:
    def __init__(
        self,
        repository: TransactionMemoryRepository,
        canonical: CanonicalRepository,
        authorization: AuthorizationService,
    ) -> None:
        self.repository = repository
        self.canonical = canonical
        self.authorization = authorization

    def record_transaction(
        self,
        actor_account_id: str,
        family_context_id: str,
        action_type: ActionType,
        resource_type: ResourceType,
        resource_id: str,
        resource_label_snapshot: str,
        operation: str,
        actor_person_id: Optional[str] = None,
        visibility: VisibilityLevel = VisibilityLevel.FAMILY,
        result_status: str = "SUCCESS",
        source: str = "user_action",
        correlation_id: Optional[str] = None,
        parent_transaction_id: Optional[str] = None,
        changed_fields: Optional[dict] = None,
        before_snapshot: Optional[dict] = None,
        after_snapshot: Optional[dict] = None,
        reason: Optional[str] = None,
        related_resource_ids: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
    ) -> TransactionRecord:
        record = TransactionRecord(
            actor_account_id=actor_account_id,
            actor_person_id=actor_person_id,
            family_context_id=family_context_id,
            action_type=action_type,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_label_snapshot=resource_label_snapshot,
            operation=operation,
            result_status=result_status,
            visibility=visibility,
            source=source,
            correlation_id=correlation_id,
            parent_transaction_id=parent_transaction_id,
            changed_fields=changed_fields,
            before_snapshot=before_snapshot,
            after_snapshot=after_snapshot,
            reason=reason,
            related_resource_ids=related_resource_ids or [],
            metadata=metadata or {},
        )
        return self.repository.record_transaction(record)

    def can_view_transaction(self, account_id: str, record: TransactionRecord, context: Optional[FamilyContext]) -> bool:
        if record.visibility == VisibilityLevel.PUBLIC:
            return True
        if record.visibility == VisibilityLevel.PRIVATE:
            return account_id == record.actor_account_id
        if record.visibility == VisibilityLevel.FAMILY:
            if context is None:
                return False
            return account_id in context.member_ids or account_id == record.actor_account_id
        return False

    def get_transaction_history_for_session(
        self,
        account_id: str,
        family_context_id: str,
        resource_type: Optional[ResourceType] = None,
        resource_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[TransactionRecord]:
        context = self.canonical.get_family_context(family_context_id)
        all_records = self.repository.list_transactions(
            family_context_id=family_context_id,
            resource_type=resource_type,
            resource_id=resource_id,
            limit=None,
        )

        authorized_records = [
            r for r in all_records
            if self.can_view_transaction(account_id, r, context)
        ]

        return authorized_records[:limit]

    def get_resource_history_for_session(
        self,
        account_id: str,
        family_context_id: str,
        resource_type: ResourceType,
        resource_id: str,
    ) -> List[TransactionRecord]:
        return self.get_transaction_history_for_session(
            account_id=account_id,
            family_context_id=family_context_id,
            resource_type=resource_type,
            resource_id=resource_id,
            limit=100,
        )

    def get_correlation_chain(
        self,
        account_id: str,
        family_context_id: str,
        correlation_id: str,
    ) -> List[TransactionRecord]:
        context = self.canonical.get_family_context(family_context_id)
        all_records = self.repository.list_transactions(
            family_context_id=family_context_id,
            correlation_id=correlation_id,
            limit=None,
        )
        return [r for r in all_records if self.can_view_transaction(account_id, r, context)]

    def explain_resource_history(
        self,
        account_id: str,
        family_context_id: str,
        resource_type: ResourceType,
        resource_id: str,
    ) -> dict:
        history = self.get_resource_history_for_session(account_id, family_context_id, resource_type, resource_id)

        current_state_desc = "Resource exists in canonical state."
        if resource_type == ResourceType.EVENT:
            ev = self.canonical.get_event(resource_id)
            if not ev: current_state_desc = "Event has been deleted."
            else: current_state_desc = f"Event '{ev.title}' scheduled on {ev.date} ({ev.visibility.value})."
        elif resource_type == ResourceType.MEMORY:
            mem = self.canonical.get_memory(resource_id)
            if not mem: current_state_desc = "Memory story has been deleted."
            else: current_state_desc = f"Memory '{mem.title}' ({mem.visibility.value})."

        facts = []
        for r in reversed(history):
            actor_name = r.actor_account_id
            acct = self.canonical.get_account(r.actor_account_id)
            if acct and acct.person_id:
                p = self.canonical.get_person(acct.person_id)
                if p: actor_name = p.name

            t_str = r.timestamp.strftime("%b %d, %H:%M UTC")
            facts.append(f"RECORDED FACT [{t_str}]: {actor_name} executed {r.action_type.value.upper()} ({r.operation}) on {r.resource_label_snapshot}")

        interpretation = f"Traced {len(history)} authorized historical activities leading to current state."

        return {
            "resource_id": resource_id,
            "resource_type": resource_type.value,
            "recorded_facts": facts,
            "current_state": current_state_desc,
            "mayil_interpretation": interpretation,
            "history_count": len(history),
        }
"""

if 'class TransactionMemoryService:' not in services_code:
    services_code += tx_service_class

with open('ENGINEERING/source/femc/services.py', 'w', encoding='utf-8') as f:
    f.write(services_code)

print("Added TransactionMemoryService to services.py!")

# 2. Update api.py to expose transaction memory on FEMCApi
api_code = open('ENGINEERING/source/femc/api.py', encoding='utf-8').read()

if 'TransactionMemoryService' not in api_code:
    api_code = api_code.replace(
        'from .models import (',
        'from .models import (\n    ActionType,\n    ResourceType,\n    TransactionRecord,'
    )
    api_code = api_code.replace(
        'from .repositories import CanonicalRepository, DerivedRepository',
        'from .repositories import CanonicalRepository, DerivedRepository, TransactionMemoryRepository'
    )
    api_code = api_code.replace(
        'from .services import (',
        'from .services import (\n    TransactionMemoryService,'
    )

    # In FEMCApi.__init__:
    old_init_end = "self.guardian = VelGuardianService(self.canonical, self.derived, self.authorization)"
    new_init_end = """self.transaction_repository = TransactionMemoryRepository()
        self.transaction_memory = TransactionMemoryService(self.transaction_repository, self.canonical, self.authorization)
        self.guardian = VelGuardianService(self.canonical, self.derived, self.authorization)"""
    api_code = api_code.replace(old_init_end, new_init_end)

    # Add API methods to FEMCApi
    api_methods = """
    def record_transaction_for_session(
        self,
        session_id: str,
        family_context_id: str,
        action_type: ActionType,
        resource_type: ResourceType,
        resource_id: str,
        resource_label_snapshot: str,
        operation: str,
        visibility: VisibilityLevel = VisibilityLevel.FAMILY,
        correlation_id: Optional[str] = None,
        parent_transaction_id: Optional[str] = None,
        changed_fields: Optional[dict] = None,
        reason: Optional[str] = None,
        related_resource_ids: Optional[List[str]] = None,
    ) -> TransactionRecord:
        session = self.authorization.get_session(self.canonical, session_id)
        if not session:
            raise PermissionError("Invalid session")
        account = self.canonical.get_account(session.account_id)
        actor_person_id = account.person_id if account else None

        return self.transaction_memory.record_transaction(
            actor_account_id=session.account_id,
            actor_person_id=actor_person_id,
            family_context_id=family_context_id,
            action_type=action_type,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_label_snapshot=resource_label_snapshot,
            operation=operation,
            visibility=visibility,
            correlation_id=correlation_id,
            parent_transaction_id=parent_transaction_id,
            changed_fields=changed_fields,
            reason=reason,
            related_resource_ids=related_resource_ids,
        )

    def get_transaction_history_for_session(
        self,
        session_id: str,
        family_context_id: str,
        resource_type: Optional[ResourceType] = None,
        resource_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[TransactionRecord]:
        session = self.authorization.get_session(self.canonical, session_id)
        if not session:
            raise PermissionError("Invalid session")
        return self.transaction_memory.get_transaction_history_for_session(
            account_id=session.account_id,
            family_context_id=family_context_id,
            resource_type=resource_type,
            resource_id=resource_id,
            limit=limit,
        )

    def get_resource_history_for_session(
        self,
        session_id: str,
        family_context_id: str,
        resource_type: ResourceType,
        resource_id: str,
    ) -> List[TransactionRecord]:
        session = self.authorization.get_session(self.canonical, session_id)
        if not session:
            raise PermissionError("Invalid session")
        return self.transaction_memory.get_resource_history_for_session(
            account_id=session.account_id,
            family_context_id=family_context_id,
            resource_type=resource_type,
            resource_id=resource_id,
        )

    def explain_resource_history_for_session(
        self,
        session_id: str,
        family_context_id: str,
        resource_type: ResourceType,
        resource_id: str,
    ) -> dict:
        session = self.authorization.get_session(self.canonical, session_id)
        if not session:
            raise PermissionError("Invalid session")
        return self.transaction_memory.explain_resource_history(
            account_id=session.account_id,
            family_context_id=family_context_id,
            resource_type=resource_type,
            resource_id=resource_id,
        )
"""
    api_code += api_methods

with open('ENGINEERING/source/femc/api.py', 'w', encoding='utf-8') as f:
    f.write(api_code)

print("Updated api.py with TransactionMemoryService integration!")
