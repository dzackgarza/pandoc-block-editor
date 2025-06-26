#!/usr/bin/env python3
"""
Main test runner for the Pandoc Block Editor.
Runs all tests from the tests/ directory.
"""

import subprocess
import sys
import os

def run_test(test_file, description):
    """Run a single test file and return success status."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=False, 
                              cwd=os.path.dirname(__file__))
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {test_file}: {e}")
        return False

def main():
    """Run all tests."""
    print("🧮 Pandoc Block Editor - Test Suite")
    print("=" * 60)
    
    test_files = [
        ("tests/test_dependencies.py", "Dependencies Test"),
        ("tests/test_editor.py", "Editor Functionality Test")
    ]
    
    all_passed = True
    results = []
    
    for test_file, description in test_files:
        if os.path.exists(test_file):
            success = run_test(test_file, description)
            results.append((description, success))
            if not success:
                all_passed = False
        else:
            print(f"❌ Test file not found: {test_file}")
            all_passed = False
            results.append((description, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    for description, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {description}")
    
    print(f"{'='*60}")
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\nYour Pandoc Block Editor is ready to use!")
        print("Launch with: python run.py")
        return 0
    else:
        print("❌ SOME TESTS FAILED!")
        print("\nPlease check the errors above and fix them.")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code) 