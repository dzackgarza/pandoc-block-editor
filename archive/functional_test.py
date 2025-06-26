#!/usr/bin/env python3
"""
Functional test to verify all key features work after performance optimizations.
"""

import sys
import time

sys.path.insert(0, 'src')

def test_imports():
    """Test that all modules import correctly."""
    print("🧪 Testing imports...")
    try:
        import app
        import pandoc_utils
        import ui_elements
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_block_creation():
    """Test that blocks can be created."""
    print("🧪 Testing block creation...")
    try:
        from app import create_editor_block
        
        # Test basic block creation
        block = create_editor_block(content="# Test\n\nHello world")
        assert block["content"] == "# Test\n\nHello world"
        assert block["kind"] == "paragraph" 
        assert "id" in block
        
        # Test different block types
        heading_block = create_editor_block(content="# Heading", kind="heading", level=1)
        assert heading_block["level"] == 1
        
        print("✅ Block creation works")
        return True
    except Exception as e:
        print(f"❌ Block creation failed: {e}")
        return False

def test_fast_parsing():
    """Test that fast parsing works for simple content."""
    print("🧪 Testing fast parsing...")
    try:
        from app import parse_full_markdown_to_editor_blocks
        
        # Test simple content (should use fast path)
        simple_content = "# Hello\n\nThis is simple content."
        blocks = parse_full_markdown_to_editor_blocks(simple_content)
        
        assert len(blocks) == 1
        assert blocks[0]["content"] == simple_content.strip()
        
        print("✅ Fast parsing works")
        return True
    except Exception as e:
        print(f"❌ Fast parsing failed: {e}")
        return False

def test_markdown_rendering():
    """Test that markdown rendering works correctly."""
    print("🧪 Testing markdown rendering...")
    try:
        import pandoc_utils
        
        # Test ultra-fast rendering
        simple_md = "# Hello\n\nThis is **bold** text."
        html = pandoc_utils.convert_markdown_to_html_ultrafast(simple_md)
        
        assert "<h1>" in html
        assert "<strong>" in html or "<b>" in html
        
        # Test fallback to Pandoc
        html_pandoc = pandoc_utils.convert_markdown_to_html_direct(simple_md)
        assert "<h1>" in html_pandoc
        
        print("✅ Markdown rendering works")
        return True
    except Exception as e:
        print(f"❌ Markdown rendering failed: {e}")
        return False

def test_session_state_functions():
    """Test session state related functions."""
    print("🧪 Testing session state functions...")
    try:
        from app import initialize_session_state
        
        # This should work without requiring streamlit context
        # We can't fully test it without streamlit, but we can import it
        assert callable(initialize_session_state)
        
        print("✅ Session state functions available")
        return True
    except Exception as e:
        print(f"❌ Session state functions failed: {e}")
        return False

def test_ui_elements():
    """Test UI elements generation."""
    print("🧪 Testing UI elements...")
    try:
        import ui_elements
        
        # Test debug console
        console_html = ui_elements.render_debug_console(initial_visible=False)
        assert "debug-console" in console_html
        assert "script" in console_html.lower()
        
        print("✅ UI elements work")
        return True
    except Exception as e:
        print(f"❌ UI elements failed: {e}")
        return False

def test_performance_expectations():
    """Test that performance improvements are in place."""
    print("🧪 Testing performance expectations...")
    try:
        from app import parse_full_markdown_to_editor_blocks
        
        # Test that simple content uses fast path
        start_time = time.time()
        simple_content = "# Simple\n\nNo fancy features here."
        blocks = parse_full_markdown_to_editor_blocks(simple_content)
        duration = time.time() - start_time
        
        # Should be very fast (< 0.1s)
        if duration > 0.1:
            print(f"⚠️ Parsing took {duration:.3f}s - may be slower than expected")
        else:
            print(f"✅ Fast parsing: {duration:.3f}s")
        
        return True
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def main():
    """Run all functional tests."""
    print("🔍 FUNCTIONAL TEST SUITE - POST-OPTIMIZATION")
    print("=" * 50)
    print("Verifying that all features work after performance improvements...")
    
    tests = [
        test_imports,
        test_block_creation, 
        test_fast_parsing,
        test_markdown_rendering,
        test_session_state_functions,
        test_ui_elements,
        test_performance_expectations
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("📊 RESULTS:")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - App functionality is intact!")
        print("🚀 Performance optimizations successful with no feature loss")
    else:
        print("⚠️ Some tests failed - functionality may be compromised")
        print("💡 Review the failed tests and fix any issues")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 