# pylint: disable=import-error
# (streamlit is a core dep for the app, pylint might not find it in all CI envs)
import json
import os
import time
from io import StringIO
import uuid

import streamlit as st

# First-party imports
import pandoc_utils
import ui_elements

# import tempfile # Unused import W0611 - Removed


# --- Global Helper Functions & Data Structures ---


def create_editor_block(
    block_id=None, kind="paragraph", content="", attributes=None, level=0
):  # Renamed id to block_id (W0622)
    """Creates an EditorBlock dictionary."""
    return {
        "id": block_id if block_id else str(uuid.uuid4()),
        "kind": kind,
        "content": content,
        "attributes": attributes if attributes else {},
        "level": level,
    }


def _extract_ast_block_attributes(ast_block):
    """Helper to extract id from AST block attributes if available."""
    attrs_container = ast_block.get("c", [])
    if isinstance(attrs_container, list) and attrs_container:
        attrs_tuple = None
        if (
            ast_block["t"] == "Header"
            and len(attrs_container) > 1
            and isinstance(attrs_container[1], list)
        ):
            attrs_tuple = attrs_container[1]
        elif ast_block["t"] == "Div" and isinstance(attrs_container[0], list):
            attrs_tuple = attrs_container[0]

        if attrs_tuple and len(attrs_tuple) > 0 and isinstance(attrs_tuple[0], str):
            return attrs_tuple[0] if attrs_tuple[0] else None
    return None


def _split_markdown_on_headings(markdown_string):
    """
    Fast markdown splitting: headings and content as separate blocks.
    - Each heading becomes its own block
    - Content between headings becomes separate blocks
    - Perfect for block-based editing where each logical unit is editable
    """
    if not markdown_string:
        return [create_editor_block(content="")]
    
    lines = markdown_string.split('\n')
    blocks = []
    current_content_lines = []
    
    for line in lines:
        # Check if line is a heading (starts with #)
        if line.strip().startswith('#'):
            # Save any accumulated content as a block
            if current_content_lines:
                content = '\n'.join(current_content_lines).strip()
                if content:
                    blocks.append(create_editor_block(content=content, kind="paragraph"))
                current_content_lines = []
            
            # Add heading as its own block
            heading_content = line.strip()
            if heading_content:
                # Determine heading level for kind
                level = len(heading_content) - len(heading_content.lstrip('#'))
                blocks.append(create_editor_block(
                    content=heading_content, 
                    kind="heading", 
                    level=level
                ))
        else:
            # Accumulate content lines
            current_content_lines.append(line)
    
    # Add final content block if any
    if current_content_lines:
        content = '\n'.join(current_content_lines).strip()
        if content:
            blocks.append(create_editor_block(content=content, kind="paragraph"))
    
    return blocks if blocks else [create_editor_block(content="")]


def parse_full_markdown_to_editor_blocks(full_markdown_string):
    """
    OPTIMIZED: Parses a full Markdown string into editor blocks.
    Only uses expensive AST parsing for document structure (fenced divs).
    Individual blocks store raw markdown for fast editing.
    """
    if not full_markdown_string:
        return [create_editor_block(content="")]
    
    # PERFORMANCE OPTIMIZATION: Check if content needs AST processing
    # Only use expensive AST parsing if document has structural elements
    lines = full_markdown_string.split('\n')
    heading_lines = [line for line in lines if line.strip().startswith('#')]
    
    needs_ast_parsing = (
        ":::" in full_markdown_string or  # Fenced divs
        len(heading_lines) > 5  # Many headings - worth structuring
    )
    
    if not needs_ast_parsing:
        # FAST PATH: Split on headings without expensive AST operations
        print(f"DEBUG: Using fast path - simple heading-based splitting")
        return _split_markdown_on_headings(full_markdown_string)
    
    # STRUCTURAL PATH: Use AST only for document structure
    print(f"DEBUG: Using AST parsing for structural content")
    try:
        ast = pandoc_utils.parse_markdown_to_ast_json(full_markdown_string)
    except RuntimeError as e:
        st.error(f"Failed to parse Markdown AST: {e}")
        return [create_editor_block(content=full_markdown_string, kind="paragraph")]

    editor_blocks = []
    pandoc_api_version = ast.get("pandoc-api-version", [1, 22])

    for ast_block in ast.get("blocks", []):
        block_data = _process_ast_block(ast_block, pandoc_api_version)
        editor_blocks.append(create_editor_block(**block_data))

    return editor_blocks if editor_blocks else [create_editor_block(content="")]


def _process_ast_block(ast_block, pandoc_api_version):
    """Helper function to process a single AST block for parsing."""
    block_id_str = _extract_ast_block_attributes(ast_block)
    content_ast_blocks = []
    block_kind = "paragraph"  # Default kind
    block_level = 0
    block_attrs = {}
    actual_block_id = block_id_str

    if ast_block["t"] == "Header":
        level, header_attrs_tuple, inlines = (
            ast_block["c"][0],
            ast_block["c"][1],
            ast_block["c"][2],
        )
        actual_block_id = (
            header_attrs_tuple[0] if header_attrs_tuple[0] else str(uuid.uuid4())
        )
        content_ast_blocks = [{"t": "Plain", "c": inlines}]
        block_kind = "heading"
        block_level = level
        block_attrs = dict(header_attrs_tuple[2])

    elif ast_block["t"] == "Div":
        div_attrs_tuple, inner_blocks_ast = ast_block["c"][0], ast_block["c"][1]
        actual_block_id = (
            div_attrs_tuple[0] if div_attrs_tuple[0] else str(uuid.uuid4())
        )
        content_ast_blocks = inner_blocks_ast
        block_kind = "semantic"
        block_attrs = {
            "id": actual_block_id,
            "classes": div_attrs_tuple[1],
            "keyvals": dict(div_attrs_tuple[2]),
        }
    else:  # Default for Para, CodeBlock, etc.
        actual_block_id = block_id_str if block_id_str else str(uuid.uuid4())
        content_ast_blocks = [ast_block]

    current_block_ast_for_content = {
        "pandoc-api-version": pandoc_api_version,
        "meta": {},
        "blocks": content_ast_blocks,
    }
    content = pandoc_utils.convert_ast_json_to_markdown(
        current_block_ast_for_content, is_full_ast=True
    ).strip()

    return {
        "block_id": actual_block_id,
        "kind": block_kind,
        "level": block_level,
        "content": content,
        "attributes": block_attrs,
    }


def handle_block_content_change(
    block_id_arg, editor_key
):  # Renamed block_id to block_id_arg
    """Handles changes in a block's content editor."""
    new_content = st.session_state[editor_key]
    for block in st.session_state.documentEditorBlocks:
        if block["id"] == block_id_arg:
            block["content"] = new_content
            break


def _format_attributes_for_markdown(attrs_dict):
    """Helper to format attributes for Markdown reconstruction."""
    attrs = []
    # ID is handled specially for headings/divs, but can be part of keyvals too
    if attrs_dict.get("id"):
        attrs.append(f"#{attrs_dict['id']}")
    if attrs_dict.get("classes"):
        attrs.extend([f".{cls}" for cls in attrs_dict["classes"]])
    if attrs_dict.get("keyvals"):
        attrs.extend([f'{k}="{v}"' for k, v in attrs_dict["keyvals"].items()])
    return f" {{{' '.join(attrs)}}}" if attrs else ""


def reconstruct_markdown_from_editor_blocks():
    """Reconstructs the full Markdown document from editor blocks."""
    parts = []
    for block in st.session_state.documentEditorBlocks:
        if block["kind"] == "heading":
            # For headings, id is part of attributes, level is separate
            attr_str = _format_attributes_for_markdown(block["attributes"])
            # Ensure block['id'] is also included if not already in attributes
            heading_id_attr = ""
            if block.get("id") and f"#{block['id']}" not in attr_str:
                heading_id_attr = f" {{{'#' + block['id']}}}"  # Minimal attr if only ID
                if attr_str:  # if other attrs exist, try to merge or append
                    attr_str = attr_str[:-1] + f" #{block['id']}}}"  # Append
                else:
                    attr_str = heading_id_attr

            parts.append(f"{'#' * block['level']} {block['content']}{attr_str}")
        elif block["kind"] == "semantic":
            # For semantic divs, attributes dict holds id, classes, keyvals
            attr_str = _format_attributes_for_markdown(block["attributes"])
            content = block["content"]
            # Ensure content has a trailing newline if not empty, for Pandoc ::: syntax
            content = (
                (content + "\n")
                if content and not content.endswith("\n")
                else (content if content else "\n")
            )
            parts.append(f":::{attr_str}\n{content}:::")
        else:  # Paragraphs, code blocks etc.
            parts.append(block["content"])
    return "\n\n".join(parts)


# --- Streamlit Session State Initialization ---
def initialize_session_state():
    """Initializes Streamlit session state variables."""
    # Only initialize once - critical for performance
    if "documentEditorBlocks" not in st.session_state:
        print(f"DEBUG: Initializing session state at {time.time()}")  # PERFORMANCE DEBUG
        
        # Initialize with empty blocks - will be populated by parsing step
        st.session_state.documentEditorBlocks = [create_editor_block(content="")]
        st.session_state.initial_load_processed = False
        
        # Use simple default content for development - avoid file I/O during init
        default_content = """# Pandoc Block Editor

## Quick Start
Start editing your **Markdown** content here.

### Features
- Live preview with Pandoc rendering
- Block-based editing
- Math support with MathJax: $E = mc^2$

```python
# Code blocks work too
print("Hello, world!")
```

> Blockquotes and other Markdown elements render properly.

---

Ready to start editing!
"""
        
        # For development, use fast default content instead of loading large test file
        # Only load torture test if explicitly requested via environment variable
        import os
        load_torture_test = os.environ.get('LOAD_TORTURE_TEST', '').lower() in ('1', 'true', 'yes')
        
        if load_torture_test:
            print("DEBUG: Loading torture test document (LOAD_TORTURE_TEST=true)")
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(script_dir)
                torture_test_path = os.path.join(project_root, "test_fixtures", "torture_test_document.md")
                
                if os.path.exists(torture_test_path):
                    with open(torture_test_path, "r", encoding="utf-8") as f:
                        st.session_state.initial_markdown_content = f.read()
                    print("DEBUG: Loaded torture test document")
                else:
                    st.session_state.initial_markdown_content = default_content
                    st.session_state.missing_torture_file = True
                    print("DEBUG: Torture test file not found, using default")
            except (IOError, OSError) as e:
                print(f"DEBUG: Error loading torture test: {e}")
                st.session_state.initial_markdown_content = default_content
        else:
            # PERFORMANCE OPTIMIZATION: Use fast parsing for default content
            # This will use the heading-based splitting instead of expensive AST operations
            st.session_state.initial_markdown_content = default_content
            print("DEBUG: Using fast default content (will use fast heading-based parsing)")
        
        print(f"DEBUG: Session state initialized at {time.time()}")  # PERFORMANCE DEBUG


def _render_editor_pane():
    """Renders the editor pane with text areas for each block."""
    for i, block in enumerate(st.session_state.documentEditorBlocks):
        block_id_display_html = (
            f"<div class='block-id-display editor-block-id'>"
            f"Editor ID: `{block['id']}`</div>"
        )
        st.markdown(block_id_display_html, unsafe_allow_html=True)
        editor_key = f"editor_{block['id']}_{i}"
        # Dynamic height based on actual content - ultra-compact
        content_lines = max(1, block["content"].count('\n') + 1)
        
        # Smart widget selection: text_input for single lines, text_area for multi-line
        is_single_line = '\n' not in block["content"]
        
        if is_single_line:
            # Use text_input for single-line content (much more compact)
            st.text_input(
                label=f"Block Content {i+1} ({block['kind']})",
                value=block["content"],
                key=editor_key,
                on_change=handle_block_content_change,
                args=(block["id"], editor_key),
                label_visibility="collapsed"
            )
        else:
            # Use text_area for multi-line content with Streamlit's minimum
            content_lines = max(1, block["content"].count('\n') + 1)
            line_height = 20
            padding = 48  # Streamlit's overhead
            dynamic_height = max(68, (content_lines * line_height) + padding)
            dynamic_height = min(300, dynamic_height)
            
            st.text_area(
                label=f"Block Content {i+1} ({block['kind']})",
                value=block["content"],
                key=editor_key,
                on_change=handle_block_content_change,
                args=(block["id"], editor_key),
                height=dynamic_height,
                label_visibility="collapsed"
            )
        st.markdown("---")


def _render_preview_pane():
    """Renders the preview pane with HTML conversion for each block."""
    for i, block in enumerate(st.session_state.documentEditorBlocks):
        viewer_id_display_html = (
            f"<div class='block-id-display viewer-block-id'>"
            f"Viewer ID: `{block['id']}`</div>"
        )
        st.markdown(viewer_id_display_html, unsafe_allow_html=True)
        preview_div_id = f"preview-block-{block['id']}-{i}"
        try:
            # PERFORMANCE: Use ultra-fast markdown for block previews
            html_content = pandoc_utils.convert_markdown_to_html_ultrafast(block["content"])
            
            preview_wrapper_html = (
                f"<div id='{preview_div_id}' "
                f"class='block-preview-wrapper'>{html_content}</div>"
            )
            st.markdown(preview_wrapper_html, unsafe_allow_html=True)

            js_typeset_script = f"""<script>
            setTimeout(function() {{
                if (typeof window.typesetMathJaxForElement === 'function') {{
                    window.typesetMathJaxForElement('{preview_div_id}');
                }} else {{
                    let attempts = 0;
                    const maxAttempts = 5;
                    const interval = 100;
                    function retryTypeset() {{
                        if (typeof window.typesetMathJaxForElement === 'function') {{
                            window.typesetMathJaxForElement('{preview_div_id}');
                        }} else if (attempts < maxAttempts) {{
                            attempts++;
                            setTimeout(retryTypeset, interval);
                        }} else {{
                            console.error(
                                'window.typesetMathJaxForElement not found for ' +
                                '{preview_div_id}'
                            );
                        }}
                    }}
                    retryTypeset();
                }}
            }}, 50);</script>"""
            st.components.v1.html(js_typeset_script, height=0)
        except RuntimeError as e:  # Pandoc conversion error
            st.error(f"Error rendering block {block['id']}:\n{e}")
        except Exception as e:  # pylint: disable=broad-except
            st.error(f"Unexpected error rendering block {block['id']}:\n{e}")
        st.markdown("---")


def _render_top_menu_bar():
    """Renders the desktop app-style top menu bar using Tailwind CSS."""
    
    # Create menu bar with Tailwind CSS
    menu_bar_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <script>
            tailwind.config = {
                theme: {
                    extend: {
                        fontFamily: {
                            'mono': ['Monaco', 'Menlo', 'Ubuntu Mono', 'monospace']
                        }
                    }
                }
            }
        </script>
    </head>
    <body class="m-0 p-0">
        <div class="bg-gradient-to-b from-gray-50 to-gray-100 border-b border-gray-300 px-4 py-2 flex items-center gap-2">
            <span class="font-semibold text-gray-700 mr-4">📋 Pandoc Editor</span>
            
            <div class="flex border border-gray-300 rounded overflow-hidden bg-white">
                <button id="menu-open" class="px-3 py-1.5 text-sm hover:bg-gray-100 transition-colors border-none bg-white cursor-pointer">
                    📁 Open
                </button>
                <button id="menu-save" class="px-3 py-1.5 text-sm hover:bg-gray-100 transition-colors border-l border-gray-300 bg-white cursor-pointer">
                    💾 Save
                </button>
                <button id="menu-add" class="px-3 py-1.5 text-sm hover:bg-gray-100 transition-colors border-l border-gray-300 bg-white cursor-pointer">
                    ➕ Add Block
                </button>
                <button id="menu-debug" class="px-3 py-1.5 text-sm hover:bg-gray-100 transition-colors border-l border-gray-300 bg-white cursor-pointer">
                    🐛 Debug
                </button>
            </div>
        </div>
        
        <!-- Hidden file input for file operations -->
        <input type="file" id="file-input" accept=".md,.markdown" style="display: none;">
        
        <script>
            // File input handler
            document.getElementById('file-input').addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const content = e.target.result;
                        // Encode content for URL
                        const encodedContent = btoa(unescape(encodeURIComponent(content)));
                        window.location.href = window.location.pathname + '?file_content=' + encodedContent;
                    };
                    reader.readAsText(file);
                }
            });
            
            // Helper function to get current document content for saving
            function getCurrentDocument() {
                // Try to reconstruct from text areas
                const textAreas = document.querySelectorAll('textarea');
                let content = "# Document\\n\\n";
                textAreas.forEach((textarea, index) => {
                    if (textarea.value.trim()) {
                        content += textarea.value + "\\n\\n";
                    }
                });
                return content || "# Empty Document\\n\\nNo content found.";
            }
            
            // Menu event handlers
            document.getElementById('menu-open')?.addEventListener('click', function() {
                document.getElementById('file-input').click();
            });
            
            document.getElementById('menu-save')?.addEventListener('click', function() {
                const content = getCurrentDocument();
                const blob = new Blob([content], { type: 'text/markdown' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'document.md';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            });
            
            document.getElementById('menu-add')?.addEventListener('click', function() {
                window.location.href = window.location.pathname + '?add_block=true';
            });
            
            document.getElementById('menu-debug')?.addEventListener('click', function() {
                window.location.href = window.location.pathname + '?toggle_debug=true';
            });
            
            // Keyboard shortcuts
            document.addEventListener('keydown', function(e) {
                if (e.ctrlKey && e.key === 'o') {
                    e.preventDefault();
                    document.getElementById('file-input').click();
                }
                if (e.ctrlKey && e.key === 's') {
                    e.preventDefault();
                    document.getElementById('menu-save').click();
                }
            });
            
            // Add some sample logging for demonstration
            console.log('Menu bar initialized successfully');
            
            // Log when buttons are clicked for debugging
            document.getElementById('menu-open')?.addEventListener('click', function() {
                console.log('Open button clicked');
            });
            document.getElementById('menu-save')?.addEventListener('click', function() {
                console.log('Save button clicked');
            });
            document.getElementById('menu-add')?.addEventListener('click', function() {
                console.log('Add block button clicked');
            });
            document.getElementById('menu-debug')?.addEventListener('click', function() {
                console.log('Debug console toggled');
            });
        </script>
    </body>
    </html>
    """
    
    # Render the menu bar
    st.components.v1.html(menu_bar_html, height=60)
    
    # Check for URL query parameters to handle actions
    query_params = st.query_params
    
    if 'add_block' in query_params:
        st.session_state.documentEditorBlocks.append(
            create_editor_block(content="")
        )
        # Clear the query param and rerun
        st.query_params.clear()
        st.rerun()
    
    if 'toggle_debug' in query_params:
        if "show_debug_console" not in st.session_state:
            st.session_state.show_debug_console = False
        st.session_state.show_debug_console = not st.session_state.show_debug_console
        # Clear the query param and rerun
        st.query_params.clear()
        st.rerun()
    
    if 'file_content' in query_params:
        try:
            import base64
            content = base64.b64decode(query_params['file_content']).decode('utf-8')
            st.session_state.documentEditorBlocks = (
                parse_full_markdown_to_editor_blocks(content)
            )
            # Clear the query param and rerun
            st.query_params.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Error processing uploaded file: {e}")


# --- Main Application ---
# R0915: Too many statements (80/50) - main() is long due to UI setup.
# Breaking it down might involve passing st object or using classes,
# which could increase complexity. Accepting for now.
def main():  # pylint: disable=too-many-statements,too-many-branches
    """Main function to run the Streamlit application."""
    st.set_page_config(layout="wide", page_title="Pandoc Block Editor")
    
    # Initialize session state only once inside main()
    initialize_session_state()

    # Inject Tailwind CSS and custom styling
    st.markdown(
        """<style>
            /* Hide sidebar navigation */
            [data-testid="stSidebarNav"] { display: none !important; }
            [data-testid="stSidebar"] { display: none !important; }
            
            /* Clean interface - no hidden controls needed */
            
            /* Desktop app container with Tailwind-inspired styling */
            .main .block-container {
                padding: 0 !important;
                max-width: none !important;
                background: #f9fafb;
                min-height: 100vh;
            }
            
            /* Clean block alignment - ultra-compact */
            div[data-testid="stHorizontalBlock"] { 
                align-items: flex-start;
                background: white;
                border-radius: 6px;
                margin: 4px;
                padding: 8px;
                box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
                border: 1px solid #e5e7eb;
            }
            
            /* Block ID styling - very compact */
            .block-id-display {
                font-size: 8px !important; 
                color: #9ca3af !important; 
                margin-bottom: 2px !important;
                margin-top: 0px !important;
                font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace !important;
                background: transparent !important;
                padding: 1px 3px !important;
                border-radius: 3px !important;
                display: inline-block !important;
                border: none !important;
                line-height: 1 !important;
            }
            
            /* Text input styling - ultra-compact for single lines */
            div[data-testid="stTextInput"] > label { display: none !important; }
            div[data-testid="stTextInput"] input { 
                padding: 4px 6px !important; 
                margin: 0 !important;
                font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace !important;
                font-size: 13px !important;
                line-height: 1.4 !important;
                border: 1px solid #d1d5db !important;
                border-radius: 4px !important;
                background: #ffffff !important;
                transition: border-color 0.2s !important;
                box-sizing: border-box !important;
                height: 28px !important;
            }
            
            /* Text area styling - compact for multi-line */
            div[data-testid="stTextArea"] > label { display: none !important; }
            div[data-testid="stTextArea"] textarea { 
                padding: 4px 6px !important; 
                margin: 0 !important;
                font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace !important;
                font-size: 13px !important;
                line-height: 1.4 !important;
                border: 1px solid #d1d5db !important;
                border-radius: 4px !important;
                background: #ffffff !important;
                transition: border-color 0.2s !important;
                resize: vertical !important;
                box-sizing: border-box !important;
            }
            
            div[data-testid="stTextArea"] textarea:focus { 
                border-color: #3b82f6 !important;
                outline: none !important;
                box-shadow: 0 0 0 3px rgb(59 130 246 / 0.1) !important;
            }
            
            /* Preview styling with modern card design */
            .block-preview-wrapper {
                background: #ffffff;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                padding: 16px;
                min-height: 120px;
            }
            .block-preview-wrapper > div { 
                padding: 0;
                margin: 0;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
                line-height: 1.7;
                color: #374151;
            }
            
            /* Typography improvements with better contrast */
            .block-preview-wrapper h1 { 
                margin-top: 0; 
                color: #111827;
                font-weight: 700;
                border-bottom: 2px solid #e5e7eb;
                padding-bottom: 8px;
            }
            .block-preview-wrapper h2 { 
                color: #1f2937;
                font-weight: 600;
                margin-top: 1.5rem;
            }
            .block-preview-wrapper h3 { 
                color: #374151;
                font-weight: 600;
                margin-top: 1.25rem;
            }
            .block-preview-wrapper p { 
                color: #374151; 
                margin-bottom: 1rem;
                line-height: 1.7;
            }
            .block-preview-wrapper code { 
                background: #f3f4f6; 
                padding: 2px 6px; 
                border-radius: 4px;
                font-size: 0.9em;
                color: #dc2626;
                border: 1px solid #e5e7eb;
            }
            .block-preview-wrapper pre {
                background: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 16px;
                overflow-x: auto;
                font-size: 13px;
                line-height: 1.5;
            }
            .block-preview-wrapper pre code {
                background: none;
                border: none;
                padding: 0;
                color: #374151;
            }
            
            /* Semantic block cards with special styling */
            .block-preview-wrapper div[class*="theorem"],
            .block-preview-wrapper div[class*="definition"],
            .block-preview-wrapper div[class*="proof"],
            .block-preview-wrapper div[class*="callout"] {
                border-left: 4px solid #3b82f6;
                background: #eff6ff;
                padding: 12px 16px;
                margin: 12px 0;
                border-radius: 0 6px 6px 0;
            }
            
            /* Remove default margins - ultra-compact */
            .element-container {
                margin-bottom: 0 !important;
                margin-top: 0 !important;
            }
            
            /* Compact separator lines */
            hr {
                margin: 4px 0 !important;
                border: none !important;
                border-top: 1px solid #f3f4f6 !important;
                opacity: 0.5 !important;
            }
            
            /* Reduce spacing in the main container */
            .main .block-container > div {
                padding-top: 0 !important;
                padding-bottom: 0 !important;
            }
        </style>""",
        unsafe_allow_html=True,
    )

    # MathJax Setup
    mathjax_script_html = """
        <script id="MathJax-script" async
                src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
        <script>
        window.MathJax = {
          tex: {
            inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
            displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
            processEscapes: true
          },
          svg: { fontCache: 'global' },
          options: {
            skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code'],
            ignoreHtmlClass: 'tex2jax_ignore',
            processHtmlClass: 'tex2jax_process'
          }
        };
        window.typesetMathJaxForElement = function(elementId) {
            if (window.MathJax && window.MathJax.typesetPromise) {
                const element = document.getElementById(elementId);
                if (element) {
                    window.MathJax.typesetPromise([element]).catch(
                        (err) => console.error(
                            'MathJax error for ' + elementId + ':', err
                        )
                    );
                } else {
                    console.warn('MathJax typeset: Element not found: ' + elementId);
                }
            } else {
                console.warn('MathJax not ready for element: ' + elementId);
            }
        };
        </script>
    """
    st.components.v1.html(mathjax_script_html, height=0)

    # --- Top Menu Bar ---
    _render_top_menu_bar()

    # --- Main Content Area ---

    if st.session_state.get("missing_torture_file", False):
        st.warning(
            "`test_fixtures/torture_test_document.md` was not found. "
            "A default document has been loaded. "
            "Please create this file for comprehensive testing."
        )
        st.session_state.missing_torture_file = False  # Show only once

    if st.session_state.get("exit_message"):
        st.info(st.session_state.exit_message)
        return  # Stop further rendering if "exited"

    # Initial load of content
    if not st.session_state.get("initial_load_processed", False):
        # Use direct default content instead of session state variable
        default_fallback = "# Welcome\n\nStart editing your document here."
        initial_content_to_load = st.session_state.get(
            "initial_markdown_content", default_fallback
        )
        try:
            parsed_blocks = parse_full_markdown_to_editor_blocks(
                initial_content_to_load
            )
            if parsed_blocks:
                st.session_state.documentEditorBlocks = parsed_blocks
            else:
                st.warning(
                    "Initial document parsed to no blocks. "
                    "Starting with a default empty block."
                )
                st.session_state.documentEditorBlocks = [
                    create_editor_block(content="")
                ]
        except (IOError, OSError, RuntimeError) as e:  # More specific exceptions
            st.error(
                f"Error parsing initial document: {e}. "
                "Starting with a default empty block."
            )
            st.session_state.documentEditorBlocks = [create_editor_block(content="")]

        st.session_state.initial_load_processed = True
        if "initial_markdown_content" in st.session_state:
            del st.session_state.initial_markdown_content

    # --- Document Flow Area (Editor and Preview Panes) ---
    editor_pane, preview_pane = st.columns(2)

    with editor_pane:
        _render_editor_pane()

    with preview_pane:
        _render_preview_pane()

    # Debug Console - Chrome-like live logging console
    if "show_debug_console" not in st.session_state:
        st.session_state.show_debug_console = False

    # The height of the component can be minimal as the console is fixed position
    st.components.v1.html(
        ui_elements.render_debug_console(
            initial_visible=st.session_state.show_debug_console
        ),
        height=0,  # Console is fixed, doesn't need layout space
    )


if __name__ == "__main__":
    main()
