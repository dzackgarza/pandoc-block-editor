#!/usr/bin/env python3
"""
Test script to verify the Qt app structure without launching the GUI.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_qt_app_structure():
    """Test that the Qt app classes can be imported and instantiated."""
    print("Testing Qt App Structure...")
    print("=" * 40)
    
    try:
        from PyQt6.QtWidgets import QApplication
        from qt_app import (
            MarkdownSyntaxHighlighter, 
            BlockEditor, 
            BlockContainer, 
            PreviewPane, 
            PandocBlockEditor
        )
        print("✅ All Qt app classes imported successfully")
        
        # Test basic instantiation (without showing GUI)
        app = QApplication([])
        
        # Test syntax highlighter
        from PyQt6.QtGui import QTextDocument
        doc = QTextDocument()
        highlighter = MarkdownSyntaxHighlighter(doc)
        print("✅ MarkdownSyntaxHighlighter created")
        
        # Test block editor
        editor = BlockEditor("test_block", "# Test Content")
        print("✅ BlockEditor created")
        
        # Test preview pane
        preview = PreviewPane()
        print("✅ PreviewPane created")
        
        # Test main window (don't show it)
        main_window = PandocBlockEditor()
        print("✅ PandocBlockEditor created")
        
        print("=" * 40)
        print("✅ All Qt app components working correctly!")
        
        # Clean up
        app.quit()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    success = test_qt_app_structure()
    if success:
        print("\n🎉 Your PyQt6 Pandoc Block Editor is ready!")
        print("Run with: python run_qt.py")
    else:
        print("\n❌ There were issues with the Qt app structure.")
        sys.exit(1) 