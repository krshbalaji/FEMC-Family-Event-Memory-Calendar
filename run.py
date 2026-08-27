import runtime
from launch_projection_patch import install
from event_edit_patch import install as install_event_edit
from event_create_sync_patch import install as install_event_create_sync
from event_celebration_integration_patch import install as install_event_celebration_integration
from sharing_label_patch import install as install_sharing_label_patch
from practice_sharing_celebration_projection_patch import install as install_practice_sharing_celebration_projection
from practice_shared_celebration_context_patch import install as install_practice_shared_celebration_context
from event_intelligence_patch import install as install_event_intelligence
from practice_runtime_fix_patch import install as install_practice_runtime_fix
from practice_event_store_repair_patch import install as install_practice_event_store_repair
from api_events_contract_repair_patch import install as install_api_events_contract_repair
from atomic_event_save_repair_patch import install as install_atomic_event_save_repair

install(runtime)
install_event_edit(runtime)
install_event_create_sync(runtime)
install_event_celebration_integration(runtime)
install_sharing_label_patch(runtime)
install_practice_sharing_celebration_projection(runtime)
install_practice_shared_celebration_context(runtime)
install_event_intelligence(runtime)
install_practice_runtime_fix(runtime)
install_practice_event_store_repair(runtime)
install_api_events_contract_repair(runtime)
install_atomic_event_save_repair(runtime)


if __name__ == "__main__":
    import sys
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    runtime.run_server(port=port)
