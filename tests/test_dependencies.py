#!/usr/bin/env python3
"""
Test script to check PyQt6 dependencies and provide helpful error messages.
"""

def test_dependencies():
    """Test all required dependencies."""
    print("Testing PyQt6 Block Editor Dependencies...")
    print("=" * 50)
    
    # Test PyQt6
    try:
        from PyQt6.QtWidgets import QApplication
        print("✅ PyQt6.QtWidgets - Available")
    except ImportError as e:
        print(f"❌ PyQt6.QtWidgets - Missing: {e}")
        print("   Install with: pip install PyQt6")
        return False
    
    # Test PyQt6 WebEngine
    try:
        from PyQt6.QtWebEngineWidgets import QWebEngineView
        print("✅ PyQt6.QtWebEngineWidgets - Available")
    except ImportError as e:
        print(f"❌ PyQt6.QtWebEngineWidgets - Missing: {e}")
        print("   Install with: pip install PyQt6-WebEngine")
        return False
    
    # Test our pandoc utilities
    try:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        import pandoc_utils
        print("✅ pandoc_utils - Available")
    except ImportError as e:
        print(f"❌ pandoc_utils - Missing: {e}")
        return False
    
    # Test Pandoc itself
    try:
        import pypandoc
        test_result = pypandoc.convert_text("# Test", to="html", format="markdown")
        print("✅ Pandoc - Available and working")
    except Exception as e:
        print(f"❌ Pandoc - Error: {e}")
        print("   Make sure pandoc is installed: https://pandoc.org/installing.html")
        return False
    
    # Test markdown library
    try:
        import markdown
        print("✅ markdown - Available")
    except ImportError as e:
        print(f"❌ markdown - Missing: {e}")
        print("   Install with: pip install markdown")
        return False
    
    print("=" * 50)
    print("✅ All dependencies available! You can run the PyQt editor.")
    return True

if __name__ == '__main__':
    import sys
    success = test_dependencies()
    if not success:
        print("\nSome dependencies are missing. Please install them and try again.")
        print("You can install all at once with:")
        print("pip install PyQt6 PyQt6-WebEngine markdown")
        sys.exit(1)
    else:
        print("\nReady to run! Use: python run_qt.py") 