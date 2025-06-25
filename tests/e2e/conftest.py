import subprocess
import time

import psutil  # For reliably killing the streamlit process and its children
import pytest

STREAMLIT_APP_PATH = "main.py"
STREAMLIT_PORT = "8501"  # Default streamlit port
BASE_URL = f"http://localhost:{STREAMLIT_PORT}"


@pytest.fixture(scope="session", autouse=True)
def streamlit_server():
    """
    pytest fixture to start and stop the Streamlit server for E2E tests.
    Autouse=True means it will run for all tests in the session (within its scope).
    """
    # Command to run Streamlit
    # Using exec to ensure Streamlit becomes the process group leader,
    # which can make cleanup easier.
    command = [
        "streamlit",
        "run",
        STREAMLIT_APP_PATH,
        "--server.port",
        STREAMLIT_PORT,
        "--server.headless",
        "true",
    ]

    # Start Streamlit as a subprocess
    print(f"\nStarting Streamlit server: {' '.join(command)}")
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Wait for the server to start
    # This is a simple way; a more robust way might check for network port availability
    # or poll the app's health endpoint if it had one.
    time.sleep(5)  # Give Streamlit a few seconds to start

    # Check if process started successfully (optional, but good for debugging)
    if process.poll() is not None:  # Process terminated
        stdout, stderr = process.communicate()
        print(f"Streamlit stdout: {stdout.decode()}")
        print(f"Streamlit stderr: {stderr.decode()}")
        raise RuntimeError(
            f"Streamlit server failed to start. Exit code: {process.returncode}"
        )
    # R1720: Removed unnecessary "else"
    print(f"Streamlit server started with PID: {process.pid}")

    yield  # This is where the testing happens

    # Teardown: Stop the Streamlit server
    print(f"\nStopping Streamlit server (PID: {process.pid})...")
    try:
        parent = psutil.Process(process.pid)
        for child in parent.children(recursive=True):  # kill children first
            print(f"Killing child process {child.pid}")
            child.kill()
        parent.kill()
        print("Streamlit server stopped.")
    except psutil.NoSuchProcess:
        print(f"Streamlit process {process.pid} already terminated.")
    except psutil.Error as e:  # Catch specific psutil errors
        print(f"psutil error stopping Streamlit server: {e}")
    except OSError as e:  # Catch OS errors during process management
        print(f"OS error stopping Streamlit server: {e}")
    # W0718: Catching other potential errors during cleanup, log them.
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Unexpected error stopping Streamlit server: {e}")
    finally:
        # Ensure process is cleaned up if Popen object still exists
        if process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=5)  # Wait a bit for termination
                if process.poll() is None:  # If still running, force kill
                    process.kill()
                    process.wait(timeout=5)
            except OSError as e:  # Catch errors during final termination attempts
                print(f"Error during final termination of process {process.pid}: {e}")
            except Exception as e:  # pylint: disable=broad-exception-caught
                err_msg = "Unexpected err in final cleanup for PID"
                print(f"{err_msg} {process.pid}: {e}")
        print("Streamlit server cleanup complete.")


# Note: The `page` fixture used in test_main_app.py is provided by pytest-playwright.
# We don't need to define it here.
# The BASE_URL can also be defined here or passed via pytest-base-url if configured.
# For simplicity, test_main_app.py can import BASE_URL from here or define it itself.
# Let's make it accessible from here.
@pytest.fixture(scope="session")
def base_url_session():
    return BASE_URL
