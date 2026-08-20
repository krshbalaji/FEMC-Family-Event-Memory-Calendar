import runtime
from launch_projection_patch import install

install(runtime)


if __name__ == "__main__":
    import sys
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    runtime.run_server(port=port)
