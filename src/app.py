# pylint: disable=import-error
# (streamlit is a core dep for the app, pylint might not find it in all CI envs)
import json
import os
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


def parse_full_markdown_to_editor_blocks(full_markdown_string):
    """
    Parses a full Markdown string into a list of EditorBlock dictionaries.
    R0914: Too many local variables (17/15) - This is borderline, structure is complex.
    R0912: Too many branches (17/12) - Due to AST node types.
    Accepting these for now as breaking it down further might reduce clarity
    of AST processing.
    """
    if not full_markdown_string:
        return [create_editor_block(content="")]
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
    if "documentEditorBlocks" not in st.session_state:
        st.session_state.documentEditorBlocks = [create_editor_block(content="")]
        st.session_state.initial_load_processed = False
        st.session_state.default_markdown_content = (
            "# New Document\n\nStart writing here."
        )
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            torture_test_filename = "torture_test_document.md"
            torture_test_path = os.path.join(
                project_root, "test_fixtures", torture_test_filename
            )
            print(
                "DEBUG: Torture test path in initialize_session_state: "
                f"{torture_test_path}"
            )  # DEBUG PRINT
            file_exists = os.path.exists(torture_test_path)
            print(f"DEBUG: Torture test file exists: {file_exists}")  # DEBUG PRINT

            if file_exists:
                with open(torture_test_path, "r", encoding="utf-8") as f:
                    st.session_state.initial_markdown_content = f.read()
                    print(
                        "DEBUG: Successfully read torture_test_document.md"
                    )  # DEBUG PRINT
            else:
                print(
                    f"DEBUG: Torture test file NOT FOUND at {torture_test_path}"
                )  # DEBUG PRINT
                error_message = (
                    f"# Welcome\n\nCould not find `{torture_test_filename}`. "
                    "Starting with a default document.\n\n"
                    f"{st.session_state.default_markdown_content}"
                )
                st.session_state.initial_markdown_content = error_message
                st.session_state.missing_torture_file = True
        except (IOError, OSError) as e:  # More specific exceptions
            st.error(f"Error loading initial document: {e}")
            st.session_state.initial_markdown_content = (
                f"# Error\n\nError loading initial document. "
                f"Starting with a default document.\n\n"
                f"{st.session_state.default_markdown_content}"
            )


initialize_session_state()


def _render_editor_pane():
    """Renders the editor pane with text areas for each block."""
    for i, block in enumerate(st.session_state.documentEditorBlocks):
        block_id_display_html = (
            f"<div class='block-id-display editor-block-id'>"
            f"Editor ID: `{block['id']}`</div>"
        )
        st.markdown(block_id_display_html, unsafe_allow_html=True)
        editor_key = f"editor_{block['id']}_{i}"
        st.text_area(
            label=f"Block Content {i+1} ({block['kind']})",
            value=block["content"],
            key=editor_key,
            on_change=handle_block_content_change,
            args=(block["id"], editor_key),
            height=max(150, int(len(block["content"]) / 1.5)),
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
            # Use direct pandoc call for maximum speed
            html_content = pandoc_utils.convert_markdown_to_html_direct(block["content"])
            
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
            
            // No localStorage handling needed - using query params instead
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
            
            /* Clean block alignment with card styling */
            div[data-testid="stHorizontalBlock"] { 
                align-items: flex-start;
                background: white;
                border-radius: 12px;
                margin: 12px;
                padding: 20px;
                box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
                border: 1px solid #e5e7eb;
            }
            
            /* Block ID styling with modern badge design */
            .block-id-display {
                font-size: 11px; 
                color: #6b7280; 
                margin-bottom: 8px;
                font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                background: #f3f4f6;
                padding: 4px 8px;
                border-radius: 6px;
                display: inline-block;
                border: 1px solid #e5e7eb;
            }
            
            /* Editor styling with modern input design */
            div[data-testid="stTextArea"] > label { display: none !important; }
            div[data-testid="stTextArea"] textarea { 
                padding: 16px !important; 
                font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace !important;
                font-size: 14px !important;
                line-height: 1.6 !important;
                border: 2px solid #e5e7eb !important;
                border-radius: 8px !important;
                background: #ffffff !important;
                transition: border-color 0.2s !important;
                resize: vertical !important;
                min-height: 120px !important;
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
            
            /* Remove default margins */
            .element-container {
                margin-bottom: 0 !important;
            }
            
            /* Separator lines */
            hr {
                margin: 20px 0 !important;
                border: none !important;
                border-top: 1px solid #e5e7eb !important;
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
        initial_content_to_load = st.session_state.get(
            "initial_markdown_content", st.session_state.default_markdown_content
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
        if "default_markdown_content" in st.session_state:
            del st.session_state.default_markdown_content

    # --- Document Flow Area (Editor and Preview Panes) ---
    editor_pane, preview_pane = st.columns(2)

    with editor_pane:
        _render_editor_pane()

    with preview_pane:
        _render_preview_pane()

    # Debug Console - Rendered based on session state
    debug_data_str = json.dumps(
        st.session_state.documentEditorBlocks, indent=2, ensure_ascii=False
    )
    # Ensure show_debug_console is initialized (already done in top menu, but good for safety)
    if "show_debug_console" not in st.session_state:
        st.session_state.show_debug_console = False

    # The height of the component can be minimal as the console is fixed position
    st.components.v1.html(
        ui_elements.render_debug_console(
            debug_data_json_string=debug_data_str,
            initial_visible=st.session_state.show_debug_console,
        ),
        height=0,  # Console is fixed, doesn't need layout space
    )


if __name__ == "__main__":
    main()
