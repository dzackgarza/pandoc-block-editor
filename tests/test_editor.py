#!/usr/bin/env python3
"""
Test script for the Pandoc Block Editor (Amsthm Environment Editor).
Verifies all components work correctly.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_amsthm_editor():
    """Test that the amsthm editor classes work correctly."""
    print("Testing Amsthm Environment Editor...")
    print("=" * 50)
    
    try:
        from PyQt6.QtWidgets import QApplication
        from amsthm_editor import (
            FencedDivBlock, 
            FencedDivEditor, 
            AmsthmEditor,
            FencedDivSyntaxHighlighter
        )
        print("✅ All amsthm classes imported successfully")
        
        # Test FencedDivBlock
        block = FencedDivBlock("test_id", "theorem", "Test Theorem", "Content here")
        print("✅ FencedDivBlock created")
        
        # Test markdown generation
        markdown = block.to_markdown()
        expected = ":::{.theorem title=\"Test Theorem\"}\nContent here\n:::"
        assert markdown == expected, f"Expected {expected}, got {markdown}"
        print("✅ Markdown generation works correctly")
        
        # Test parsing
        parsed = FencedDivBlock.from_markdown(markdown, "parsed_id")
        assert parsed.env_type == "theorem"
        assert parsed.title == "Test Theorem"
        assert parsed.content == "Content here"
        print("✅ Markdown parsing works correctly")
        
        # Test Qt components (without showing GUI)
        app = QApplication([])
        
        from PyQt6.QtGui import QTextDocument
        doc = QTextDocument()
        highlighter = FencedDivSyntaxHighlighter(doc)
        print("✅ Syntax highlighter created")
        
        editor = FencedDivEditor(block)
        print("✅ FencedDivEditor created")
        
        # Test main window (don't show it)
        main_window = AmsthmEditor()
        print("✅ AmsthmEditor main window created")
        
        print("=" * 50)
        print("✅ All amsthm editor components working!")
        
        app.quit()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sample_environments():
    """Test various amsthm environments."""
    print("\nTesting Environment Types...")
    print("=" * 30)
    
    try:
        from amsthm_editor import FencedDivBlock
        
        environments = [
            ("theorem", "Pythagorean Theorem", "$$a^2 + b^2 = c^2$$"),
            ("definition", "Vector Space", "A set with addition and scalar multiplication"),
            ("proof", "", "By contradiction, assume..."),
            ("lemma", "Helper Result", "This follows from the theorem"),
            ("example", "Unit Circle", "The circle $x^2 + y^2 = 1$"),
            ("remark", "", "Note that this also applies to...")
        ]
        
        for env_type, title, content in environments:
            block = FencedDivBlock(f"test_{env_type}", env_type, title, content)
            markdown = block.to_markdown()
            print(f"✅ {env_type.title()}: Generated markdown correctly")
            
            # Verify parsing round-trip
            parsed = FencedDivBlock.from_markdown(markdown, f"parsed_{env_type}")
            assert parsed.env_type == env_type
            assert parsed.title == title
            assert parsed.content == content
            print(f"   ↳ Round-trip parsing works")
        
        print("=" * 30)
        print("✅ All environment types work correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing environments: {e}")
        return False

if __name__ == '__main__':
    print("🧮 Amsthm Environment Editor Tests")
    print("=" * 60)
    
    success1 = test_amsthm_editor()
    success2 = test_sample_environments()
    
    if success1 and success2:
        print("\n🎉 All tests passed! Your editor is ready!")
        print("Run with: python run.py")
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1) 