import runtime
from launch_projection_patch import install
from event_edit_patch import install as install_event_edit
from event_create_sync_patch import install as install_event_create_sync
from event_celebration_integration_patch import install as install_event_celebration_integration

install(runtime)
install_event_edit(runtime)
install_event_create_sync(runtime)
install_event_celebration_integration(runtime)


if __name__ == "__main__":
    import sys
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    runtime.run_server(port=port)
