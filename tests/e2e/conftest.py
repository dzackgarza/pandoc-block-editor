# pylint: disable=import-error,redefined-outer-name
# (psutil, pytest are dev dependencies; pytest fixtures)
import subprocess
import time
import os  # Added for path operations
import psutil
import pytest

STREAMLIT_APP_PATH = "src/app.py"  # Changed from main.py
STREAMLIT_PORT = "8501"
BASE_URL = f"http://localhost:{STREAMLIT_PORT}"


@pytest.fixture(scope="session", autouse=True)
def streamlit_server():
    """
    pytest fixture to start and stop the Streamlit server for E2E tests.
    """
    # Construct an absolute path to the streamlit executable
    # within the virtual environment.
    # conftest.py is in tests/e2e/, so project_root is three levels up.
    current_dir = os.path.dirname(os.path.abspath(__file__))  # .../tests/e2e
    tests_dir = os.path.dirname(current_dir)  # .../tests
    project_root = os.path.dirname(tests_dir)  # .../ (project root)

    streamlit_executable = os.path.join(project_root, ".venv", "bin", "streamlit")

    command = [
        streamlit_executable,
        "run",
        STREAMLIT_APP_PATH,
        "--server.port",
        STREAMLIT_PORT,
        "--server.headless",
        "true",
    ]

    print(f"\nStarting Streamlit server: {' '.join(command)}")
    # R1732: Using 'with' for subprocess.Popen
    with subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ) as process:
        print(f"Streamlit server starting with PID: {process.pid}...")
        # Wait for the server to start
        print("Waiting 10 seconds for Streamlit server to initialize fully...")
        time.sleep(10)  # Increased delay

        if process.poll() is not None:
            # Process terminated prematurely
            stdout, stderr = process.communicate()
            print(f"Streamlit stdout: {stdout.decode(errors='ignore')}")
            print(f"Streamlit stderr: {stderr.decode(errors='ignore')}")
            raise RuntimeError(
                f"Streamlit server failed to start. Exit code: {process.returncode}"
            )
        print(f"Streamlit server assumed started with PID: {process.pid}")

        yield  # Test execution happens here

        # Teardown: Stop the Streamlit server
        print(f"\nStopping Streamlit server (PID: {process.pid})...")
        try:
            parent = psutil.Process(process.pid)
            # Kill child processes first, then the parent
            for child in parent.children(recursive=True):
                print(f"Killing child process {child.pid}")
                try:
                    child.kill()
                except psutil.NoSuchProcess:
                    print(f"Child process {child.pid} already terminated.")
            print(f"Killing parent process {parent.pid}")
            parent.kill()
            print("Streamlit server process killed.")
        except psutil.NoSuchProcess:
            print(f"Streamlit process {process.pid} already terminated.")
        except psutil.Error as e:
            print(f"psutil error stopping Streamlit server: {e}")
        except OSError as e:
            print(f"OS error stopping Streamlit server: {e}")
        # The broad 'except Exception' for final cleanup is acceptable here.
        # pylint: disable=broad-exception-caught
        except Exception as e:
            print(f"Unexpected error stopping Streamlit server: {e}")
        finally:
            # Ensure process Popen object is handled if still alive
            if process.poll() is None:
                try:
                    print(f"Final termination attempt for process {process.pid}")
                    process.terminate()
                    process.wait(timeout=5)
                    if process.poll() is None:
                        process.kill()
                        process.wait(timeout=5)
                # pylint: disable=broad-exception-caught
                except Exception as e_final:
                    print(
                        f"Error during final Popen cleanup for {process.pid}: {e_final}"
                    )
            print("Streamlit server cleanup sequence complete.")


@pytest.fixture(scope="session")
def base_url_session():
    """Provides the base URL for the Streamlit application."""
    return BASE_URL
