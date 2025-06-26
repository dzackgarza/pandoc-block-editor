#!/usr/bin/env python3
import os
import subprocess
import sys


def main():
    """
    Runs the Streamlit application.
    """
    # Get the directory where main.py is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(script_dir, "app.py")

    if not os.path.exists(app_path):
        print(f"Error: app.py not found at {app_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Launching Streamlit app: {app_path}")

    try:
        # Using subprocess.run to have a bit more control and capture output if needed.
        # Streamlit typically runs until manually stopped.
        # The `streamlit run` command will take over the terminal.
        process = subprocess.run(["streamlit", "run", app_path], check=True)
    except FileNotFoundError:
        print(
            "Error: 'streamlit' command not found. Please ensure Streamlit is installed and in your PATH.",
            file=sys.stderr,
        )
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit app: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nStreamlit app stopped by user.")
        sys.exit(0)


if __name__ == "__main__":
    main()
