import os, sys

# 1. Update api.py to use self._validate_session(session_id)
api_code = open('ENGINEERING/source/femc/api.py', encoding='utf-8').read()

api_code = api_code.replace(
    'session = self.authorization.get_session(self.canonical, session_id)',
    'session = self._validate_session(session_id)'
)

with open('ENGINEERING/source/femc/api.py', 'w', encoding='utf-8') as f:
    f.write(api_code)

print("Updated api.py to use self._validate_session(session_id)!")

# 2. Update DataPortabilityService in services.py to include transaction history in export
services_code = open('ENGINEERING/source/femc/services.py', encoding='utf-8').read()

if '"transactions": []' not in services_code:
    services_code = services_code.replace(
        '"insight_analyses": [],',
        '"insight_analyses": [],\n            "transactions": [],'
    )
    
    # Append export of transactions
    export_tx_code = """
        if hasattr(self, "transaction_service") and self.transaction_service:
            tx_history = self.transaction_service.get_transaction_history_for_session(account_id, family_context_id, limit=200)
            for tx in tx_history:
                records["transactions"].append({
                    "transaction_id": tx.transaction_id,
                    "timestamp": tx.timestamp.isoformat(),
                    "actor_account_id": tx.actor_account_id,
                    "action_type": tx.action_type.value if hasattr(tx.action_type, "value") else str(tx.action_type),
                    "resource_type": tx.resource_type.value if hasattr(tx.resource_type, "value") else str(tx.resource_type),
                    "resource_id": tx.resource_id,
                    "resource_label_snapshot": tx.resource_label_snapshot,
                    "operation": tx.operation,
                    "visibility": tx.visibility.value if hasattr(tx.visibility, "value") else str(tx.visibility),
                })
"""
    # Insert before return DataExportResult
    services_code = services_code.replace(
        'return DataExportResult(',
        export_tx_code + '\n        return DataExportResult('
    )

with open('ENGINEERING/source/femc/services.py', 'w', encoding='utf-8') as f:
    f.write(services_code)

print("Updated DataPortabilityService in services.py to export transactions!")
