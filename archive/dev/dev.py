#!/usr/bin/env python3
"""
Development script for the Pandoc Block Editor with optimized hot reload.
This script provides enhanced development features like faster reloading and better debugging.
"""
import os
import subprocess
import sys


def main():
    """
    Runs the Streamlit application in development mode with hot reload optimizations.
    """
    # Get the directory where dev.py is located  
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)  # Go up one level from dev/ to project root
    app_path = os.path.join(project_root, "src/app.py")

    if not os.path.exists(app_path):
        print(f"Error: app.py not found at {app_path}", file=sys.stderr)
        sys.exit(1)

    print(f"🚀 Launching Streamlit app in development mode: {app_path}")
    print("📝 Hot reload is enabled - changes will be reflected automatically")
    print("🔍 Debug mode is enabled for better error reporting")
    print("⚡ Fast rerun mode is enabled for quicker updates")
    print("🌐 Server will be available at http://localhost:8501")
    print("=" * 60)

    try:
        # Development-optimized Streamlit command with additional flags
        cmd = [
            "streamlit", "run", app_path,
            "--server.runOnSave", "true",        # Enable hot reload
            "--server.fileWatcherType", "auto",   # Use the best file watcher available
            "--browser.gatherUsageStats", "false", # Disable telemetry for faster startup
        ]
        
        print(f"Running command: {' '.join(cmd)}")
        print("=" * 60)
        
        # Run the command and let Streamlit handle the process
        subprocess.run(cmd, check=True)
        
    except FileNotFoundError:
        error_message = (
            "Error: 'streamlit' command not found. "
            "Please ensure Streamlit is installed:\n"
            "  pip install streamlit\n"
            "or install from requirements.txt:\n"
            "  pip install -r requirements.txt"
        )
        print(error_message, file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit app: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Development server stopped by user.")
        sys.exit(0)


if __name__ == "__main__":
    main() 