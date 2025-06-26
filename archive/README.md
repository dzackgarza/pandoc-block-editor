# Archive - Previous Versions

This archive contains the previous versions of the Pandoc Block Editor before focusing on the specialized amsthm environment editor.

## Archived Components

### Original Streamlit Application
- `src/app.py` - Original Streamlit-based block editor
- `src/ui_elements.py` - Streamlit UI components  
- `main.py` - Streamlit main launcher
- `run_dev.py` - Development launcher
- `functional_test.py` - Functional testing script

### General PyQt6 Application  
- `src/qt_app.py` - General-purpose PyQt6 block editor
- `run_qt.py` - PyQt6 launcher
- `test_qt_app.py` - PyQt6 app tests
- `docs/README_QT.md` - PyQt6 documentation

### Development Files
- `dev/` - Development utilities and guides
- `dev-docs/` - Development documentation
- `tests/` - Old test suite
- `test_fixtures/` - Test markdown files
- `docs/README_OLD.md` - Original project README

## Why Archived

These components were replaced by the focused **amsthm environment editor** which:
- Eliminates complexity by focusing only on fenced div blocks
- Provides perfect alignment between editor and preview
- Specializes in mathematical environment rendering
- Removes all height restrictions and web-based limitations

## Current Application

The current application (in the parent directory) is the **specialized amsthm environment editor** built with PyQt6, focused exclusively on mathematical fenced div environments with perfect alignment.

To use the current version:
```bash
cd ..
python test.py              # Run all tests
python tests/test_editor.py # Test editor functionality only  
python run.py               # Launch the editor
```

## Historical Context

The evolution was:
1. **Streamlit version** - Web-based but with 68px height restrictions
2. **General PyQt6 version** - Native desktop but still general-purpose  
3. **Specialized amsthm version** - Focused, minimal, perfect alignment ✅

The final specialized version achieves exactly what was requested: fenced div blocks only, with perfect top-alignment between editor and preview. 