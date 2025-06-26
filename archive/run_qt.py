#!/usr/bin/env python3
"""
Launcher script for the PyQt6 Pandoc Block Editor.
"""

import sys
import os

# Add src directory to path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the Qt app
from qt_app import main

if __name__ == '__main__':
    main() 