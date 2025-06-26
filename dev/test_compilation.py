#!/usr/bin/env python3
"""
Simple compilation test to ensure all modules can be imported and basic functionality works.
This test should be run after any changes to check for import errors or syntax issues.
"""
import sys
import os

def test_imports():
    """Test that all main modules can be imported successfully."""
    print("Testing imports...")
    
    try:
        # Add src directory to path
        project_root = os.path.dirname(os.path.dirname(__file__))  # Go up from dev/ to project root
        sys.path.insert(0, os.path.join(project_root, 'src'))
        
        # Test importing all main modules
        import app
        print("✅ app.py imported successfully")
        
        import pandoc_utils
        print("✅ pandoc_utils.py imported successfully")
        
        import ui_elements
        print("✅ ui_elements.py imported successfully")
        
        # Test basic function existence
        assert hasattr(app, 'main'), "app.main function not found"
        assert hasattr(app, 'create_editor_block'), "app.create_editor_block function not found"
        assert hasattr(app, 'parse_full_markdown_to_editor_blocks'), "app.parse_full_markdown_to_editor_blocks function not found"
        
        print("✅ All required functions exist")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except AssertionError as e:
        print(f"❌ Function missing: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without running Streamlit."""
    print("\nTesting basic functionality...")
    
    try:
        project_root = os.path.dirname(os.path.dirname(__file__))  # Go up from dev/ to project root
        sys.path.insert(0, os.path.join(project_root, 'src'))
        import app
        
        # Test creating an editor block
        block = app.create_editor_block(content="# Test Heading")
        assert block['content'] == "# Test Heading"
        assert block['kind'] == "paragraph"
        assert 'id' in block
        print("✅ create_editor_block works correctly")
        
        # Test parsing simple markdown
        test_markdown = "# Hello World\n\nThis is a test."
        blocks = app.parse_full_markdown_to_editor_blocks(test_markdown)
        assert len(blocks) >= 1
        assert any("Hello World" in block['content'] for block in blocks)
        print("✅ parse_full_markdown_to_editor_blocks works correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Running compilation and basic functionality tests...")
    print("=" * 50)
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test basic functionality
    if not test_basic_functionality():
        success = False
    
    print("=" * 50)
    if success:
        print("✅ All tests passed! The app should compile and run correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues before running the app.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 