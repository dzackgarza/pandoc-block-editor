# Development Guide - Pandoc Block Editor

This guide explains how to develop the Pandoc Block Editor with hot reload functionality.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Development Server (with Hot Reload)
```bash
python dev.py
```

This will start the Streamlit development server with:
- ✅ **Hot reload** - automatically refreshes when you save files
- ✅ **Fast file watching** - uses the best available file watcher for your system
- ✅ **Optimized settings** - disabled telemetry for faster startup
- ✅ **Development-friendly configuration** - via `.streamlit/config.toml`

The app will be available at: **http://localhost:8501**

### 3. Alternative: Standard Streamlit
If you prefer the standard Streamlit command:
```bash
python main.py
# or
streamlit run src/app.py
```

## Development Workflow

### Making Changes
1. Edit any Python file in the `src/` directory
2. Save the file
3. The browser will automatically refresh with your changes
4. No need to restart the server!

### Testing Changes
Before committing, run the compilation test:
```bash
python test_compilation.py
```

This ensures:
- All modules can be imported correctly
- Basic functionality works
- No obvious syntax errors

## File Structure

### Development Files
- `dev.py` - Enhanced development server with hot reload
- `test_compilation.py` - Quick compilation and functionality test
- `.streamlit/config.toml` - Streamlit configuration optimized for development

### Application Files
- `src/app.py` - Main Streamlit application
- `src/pandoc_utils.py` - Pandoc integration utilities  
- `src/ui_elements.py` - UI components and helpers
- `main.py` - Standard application launcher

## Hot Reload Features

### What Gets Hot Reloaded
- ✅ Python code changes (`*.py` files)
- ✅ Function modifications
- ✅ UI changes
- ✅ Logic updates

### What Requires Manual Refresh
- Configuration file changes (`.streamlit/config.toml`)
- Static assets
- External dependencies

### Performance Tips
- The file watcher uses minimal resources
- Changes are detected instantly
- Page state is preserved when possible
- Streamlit automatically handles most session state

## Development Configuration

The `.streamlit/config.toml` file includes development-optimized settings:

```toml
[server]
runOnSave = true              # Enable hot reload
fileWatcherType = "auto"      # Best file watcher for your OS
enableCORS = false            # Faster local development
enableXsrfProtection = false  # Faster local development
headless = false              # Open browser automatically

[browser]
gatherUsageStats = false      # Faster startup (no telemetry)

[theme]
base = "light"                # Easier on eyes during development

[logger]
level = "info"                # Show helpful development logs
```

## Troubleshooting

### Server Won't Start
1. Check if port 8501 is already in use:
   ```bash
   lsof -i :8501
   ```
2. Kill any existing Streamlit processes:
   ```bash
   pkill -f streamlit
   ```
3. Try running the test first:
   ```bash
   python test_compilation.py
   ```

### Hot Reload Not Working
1. Ensure you're using `dev.py` (not `main.py`)
2. Check that `runOnSave = true` in `.streamlit/config.toml`
3. Try refreshing the browser manually
4. Restart the development server

### Import Errors
1. Make sure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the compilation test:
   ```bash
   python test_compilation.py
   ```

## Development Commands Summary

| Command | Purpose |
|---------|---------|
| `python dev.py` | Start development server with hot reload |
| `python test_compilation.py` | Test imports and basic functionality |
| `python main.py` | Start standard Streamlit server |
| `pkill -f streamlit` | Stop all Streamlit processes |

## Next Steps

Once the hot reload is working:
1. Edit `src/app.py` to see changes instantly
2. Try modifying the UI components in `ui_elements.py`
3. Test Pandoc integration via `pandoc_utils.py`
4. Use the browser developer tools for frontend debugging

Happy coding! 🚀 