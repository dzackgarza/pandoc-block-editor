#!/usr/bin/env python3
"""
Simple launcher for the development environment.
"""
import subprocess
import sys
import os

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dev_script = os.path.join(script_dir, "dev", "dev.py")
    subprocess.run([sys.executable, dev_script]) 