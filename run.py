#!/usr/bin/env python3
"""
Pandoc Block Editor - Amsthm Environment Editor
A specialized editor for mathematical fenced div environments.
"""

import sys
import os

# Add src directory to path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the amsthm editor
from amsthm_editor import main

if __name__ == '__main__':
    main() 