# pylint: disable=import-error
# (streamlit is a core dep for the app, pylint might not find it in all CI envs)
import json
import os
from io import StringIO
import time  # Added for performance logging
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
    func_start_time = time.time()
    print(
        f"[PERF_LOG] parse_full_markdown_to_editor_blocks: Start (input len: {len(full_markdown_string)})"
    )

    if not full_markdown_string:
        print(
            f"[PERF_LOG] parse_full_markdown_to_editor_blocks: Finished (empty input) in {time.time() - func_start_time:.4f}s"
        )
        return [create_editor_block(content="")]

    ast_call_start_time = time.time()
    try:
        ast = pandoc_utils.parse_markdown_to_ast_json(full_markdown_string)
        ast_call_duration = time.time() - ast_call_start_time
        print(
            f"[PERF_LOG] parse_full_markdown_to_editor_blocks: Got full AST from Pandoc in {ast_call_duration:.4f}s"
        )
    except RuntimeError as e:
        st.error(f"Failed to parse Markdown AST: {e}")
        ast_call_duration = time.time() - ast_call_start_time
        print(
            f"[PERF_LOG] parse_full_markdown_to_editor_blocks: Pandoc AST call ERRORED in {ast_call_duration:.4f}s"
        )
        return [create_editor_block(content=full_markdown_string, kind="paragraph")]

    editor_blocks = []
    pandoc_api_version = ast.get("pandoc-api-version", [1, 22])

    print(
        f"[PERF_LOG] parse_full_markdown_to_editor_blocks: Starting block processing loop for {len(ast.get('blocks', []))} blocks."
    )
    total_block_processing_time = 0

    for i, ast_block in enumerate(ast.get("blocks", [])):
        block_process_start_time = time.time()
        block_data = _process_ast_block(ast_block, pandoc_api_version)
        editor_blocks.append(create_editor_block(**block_data))
        block_process_duration = time.time() - block_process_start_time
        total_block_processing_time += block_process_duration
        # Limit logging for many blocks, e.g., log every 10th block or if slow
        if i < 5 or i % 10 == 0 or block_process_duration > 0.1:
            print(
                f"[PERF_LOG] parse_full_markdown_to_editor_blocks: Processed block {i} (type: {ast_block.get('t', 'Unknown')}) in {block_process_duration:.4f}s"
            )

    print(
        f"[PERF_LOG] parse_full_markdown_to_editor_blocks: Finished block processing loop. Total block processing time: {total_block_processing_time:.4f}s"
    )
    print(
        f"[PERF_LOG] parse_full_markdown_to_editor_blocks: Finished in {time.time() - func_start_time:.4f}s"
    )
    return editor_blocks if editor_blocks else [create_editor_block(content="")]


    """Helper function to process a single AST block for parsing."""
def _process_ast_block(ast_block, pandoc_api_version):
    """Helper function to process a single AST block for parsing."""
    # Unused variables for optional logging are now removed.

    block_id_str = _extract_ast_block_attributes(ast_block)
    # content_ast_blocks = [] # Not needed universally, defined in branches
    block_kind = "paragraph"  # Default kind
    block_level = 0
    block_attrs = {}
    actual_block_id = block_id_str
    content = ""  # Initialize content to ensure it's always defined

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
        # For Divs, content is typically a list of blocks.
        # Reconstructing this accurately without Pandoc is complex if we want
        # the *exact* Markdown for the Div's content.
        # So, we still use Pandoc for Div content for now.
        content_ast_blocks = inner_blocks_ast
        block_kind = "semantic"
        block_attrs = {
            "id": actual_block_id,
            "classes": div_attrs_tuple[1],
            "keyvals": dict(div_attrs_tuple[2]),
        }
        # Use Pandoc to reconstruct Markdown content for Divs
        current_block_ast_for_content = {
            "pandoc-api-version": pandoc_api_version,
            "meta": {},
            "blocks": content_ast_blocks,
        }
        content = pandoc_utils.convert_ast_json_to_markdown(
            current_block_ast_for_content, is_full_ast=True
        ).strip()

    elif ast_block["t"] == "Para":
        actual_block_id = block_id_str if block_id_str else str(uuid.uuid4())
        content = _inlines_to_markdown(ast_block["c"])
        block_kind = "paragraph"
        # block_attrs remains empty, block_level remains 0

    elif ast_block["t"] == "Plain":
        actual_block_id = block_id_str if block_id_str else str(uuid.uuid4())
        content = _inlines_to_markdown(ast_block["c"])
        block_kind = (
            "plain"  # Or treat as paragraph if 'plain' is not a useful distinction
        )

    elif ast_block["t"] == "CodeBlock":
        actual_block_id = block_id_str if block_id_str else str(uuid.uuid4())
        # c[0] is attributes: [id, [classes], [[key,val]]]
        # c[1] is the code string
        attrs, code_text = ast_block["c"]
        lang_class = ""
        if attrs[1]:  # classes
            lang_class = attrs[1][0] if attrs[1] else ""  # Take first class as language

        # Basic reconstruction: ```lang\ncode\n```
        # Pandoc's own reconstruction might be more nuanced with attributes.
        # For performance, this simple version is used.
        content = f"```{lang_class}\n{code_text}\n```"
        block_kind = "code"
        block_attrs = {"classes": attrs[1]}  # Store original classes

    else:  # Fallback for RawBlock, Table, Lists, BlockQuote, HorizontalRule etc.
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
        # Try to infer kind from AST type if not 'paragraph'
        simple_kind_map = {
            "CodeBlock": "code",  # Example
            "BlockQuote": "blockquote",
            "BulletList": "ul",
            "OrderedList": "ol",
            "HorizontalRule": "hr",
        }
        block_kind = simple_kind_map.get(ast_block["t"], "paragraph")
        # pandoc_call_needed = True # This was for the commented-out log line

    # Optional: More verbose logging for _process_ast_block itself.
    # The primary per-block timing is now in parse_full_markdown_to_editor_blocks.
    # This log can be enabled if detailed tracing of Python vs Pandoc path per block is needed.
    # block_type_for_log = ast_block.get('t', 'Unknown')
    # pandoc_marker_str = "(Pandoc)" if pandoc_call_needed else "(Python)" # Renamed for clarity
    # func_duration = time.time() - func_start_time
    # print(f"[PERF_LOG] _process_ast_block: Finished (type: {block_type_for_log} {pandoc_marker_str}) in {func_duration:.4f}s")

    return {
        "block_id": actual_block_id,
        "kind": block_kind,
        "level": block_level,
        "content": content,
        "attributes": block_attrs,
    }


# --- Helper for AST to Markdown reconstruction (for performance) ---
def _inlines_to_markdown(inlines):
    """
    Converts a list of Pandoc inline AST elements to a Markdown string.
    This is a simplified converter focusing on common elements to avoid
    excessive Pandoc subprocess calls for simple content.
    """
    parts = []
    for inline in inlines:
        t = inline.get("t")
        c = inline.get("c")
        if t == "Str":
            parts.append(c)
        elif t == "Space":
            parts.append(" ")
        elif t == "SoftBreak":
            parts.append("\n")  # Or " " depending on desired Markdown strictness
        elif t == "LineBreak":
            parts.append("\\\n")  # Or "  \n"
        elif t == "Emph":
            parts.append(f"*{_inlines_to_markdown(c)}*")
        elif t == "Strong":
            parts.append(f"**{_inlines_to_markdown(c)}**")
        elif t == "Strikeout":
            parts.append(f"~~{_inlines_to_markdown(c)}~~")
        elif t == "Superscript":
            parts.append(f"^{_inlines_to_markdown(c)}^")
        elif t == "Subscript":
            parts.append(f"~{_inlines_to_markdown(c)}~")
        elif t == "SmallCaps":
            # No standard Markdown, Pandoc uses <span style="font-variant:small-caps;">
            # For simplicity, just output content. Or could be configurable.
            parts.append(_inlines_to_markdown(c))
        elif t == "Quoted":
            quote_type = c[0].get("t")
            content = _inlines_to_markdown(c[1])
            if quote_type == "SingleQuote":
                parts.append(f"'{content}'")
            elif quote_type == "DoubleQuote":
                parts.append(f'"{content}"')
            else:  # Should not happen
                parts.append(content)
        elif t == "Code":
            # c[0] is attributes, c[1] is the code string
            attrs_str = (
                ""  # Could reconstruct attributes if needed, e.g. for {#id .class}
            )
            parts.append(f"`{c[1]}`{attrs_str}")
        elif t == "Math":
            # c[0] is MathType (DisplayMath or InlineMath), c[1] is the math string
            math_type = c[0].get("t")
            math_content = c[1]
            if math_type == "InlineMath":
                parts.append(f"${math_content}$")
            elif math_type == "DisplayMath":
                parts.append(f"$$\n{math_content}\n$$")
        elif t == "RawInline":
            # c[0] is format (e.g., "html"), c[1] is the raw string
            # This is tricky for Markdown output; often best to keep as is.
            parts.append(c[1])
        elif t == "Link":
            # c[0] is attributes, c[1] is content (inlines), c[2] is [url, title]
            link_content = _inlines_to_markdown(c[1])
            url = c[2][0]
            title = c[2][1]
            title_str = f' "{title}"' if title else ""
            parts.append(f"[{link_content}]({url}{title_str})")
        elif t == "Image":
            # c[0] is attributes, c[1] is alt text (inlines), c[2] is [url, title]
            alt_text = _inlines_to_markdown(c[1])
            url = c[2][0]
            title = c[2][1]
            title_str = f' "{title}"' if title else ""
            parts.append(f"![{alt_text}]({url}{title_str})")
        elif t == "Note":
            # Pandoc extension: [^note_content].
            # c[0] is a list of blocks (the footnote content)
            # This is complex to reconstruct inline. Usually handled at block level.
            # For simplicity here, might omit or use a placeholder.
            # For now, let's indicate a note was here.
            parts.append("[^note]")  # Placeholder
        elif t == "Span":
            # c[0] is attributes, c[1] is content (inlines)
            # Pandoc extension: [content]{attrs}
            # For simplicity, just output content. Could reconstruct with attrs.
            parts.append(_inlines_to_markdown(c[1]))
        # Add other inline types as needed: Cite, Underline etc.
        else:
            # Fallback for unknown types: try to get text if possible or skip
            # This is a simplification. A robust converter would handle all types.
            # For now, we are aiming for common cases.
            # If 'c' is a list of inlines, recurse. If string, append.
            if isinstance(c, list):
                parts.append(_inlines_to_markdown(c))
            elif isinstance(c, str):
                parts.append(c)
            # else: ignore for now
    return "".join(parts)


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
    func_start_time = time.time()
    print("[PERF_LOG] initialize_session_state: Start")

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
            # print(
            #     "DEBUG: Torture test path in initialize_session_state: "
            #     f"{torture_test_path}"
            # ) # DEBUG PRINT

            read_start_time = time.time()
            file_exists = os.path.exists(torture_test_path)
            # print(f"DEBUG: Torture test file exists: {file_exists}") # DEBUG PRINT

            if file_exists:
                with open(torture_test_path, "r", encoding="utf-8") as f:
                    st.session_state.initial_markdown_content = f.read()
                read_duration = time.time() - read_start_time
                print(
                    f"[PERF_LOG] initialize_session_state: Read torture_test_document.md in {read_duration:.4f}s"
                )
                # print(
                #     "DEBUG: Successfully read torture_test_document.md"
                # )  # DEBUG PRINT
            else:
                # print(
                #     f"DEBUG: Torture test file NOT FOUND at {torture_test_path}"
                # )  # DEBUG PRINT
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
                "Starting with a default document.\n\n"
                f"{st.session_state.default_markdown_content}"
            )

    func_duration = time.time() - func_start_time
    print(f"[PERF_LOG] initialize_session_state: Finished in {func_duration:.4f}s")


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
            html_conv_start_time = time.time()
            html_content = pandoc_utils.convert_markdown_to_html(block["content"])
            html_conv_duration = time.time() - html_conv_start_time
            # Log if conversion is slow, or for first few blocks
            if (
                i < 3 or html_conv_duration > 0.05
            ):  # Log first 3 blocks or any slow ones
                print(
                    f"[PERF_LOG] _render_preview_pane: Block {i} (ID: {block['id']}, kind: {block['kind']}) HTML conversion took {html_conv_duration:.4f}s"
                )

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


def _render_sidebar_menu():
    """Renders the sidebar menu."""
    with st.sidebar:
        st.title("📋 Pandoc Editor Menu")
        st.markdown("---")

        # File Menu
        st.subheader("📄 File")
        uploaded_file = st.file_uploader(
            "Open Document", type=["md", "markdown"], key="sidebar_file_uploader"
        )
        if uploaded_file is not None:
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            st.session_state.documentEditorBlocks = (
                parse_full_markdown_to_editor_blocks(stringio.read())
            )
            st.session_state.sidebar_file_uploader = None  # Clear uploader
            st.rerun()

        full_doc_md_for_download = reconstruct_markdown_from_editor_blocks()
        st.download_button(
            label="Save Document",
            data=full_doc_md_for_download,
            file_name="document.md",
            mime="text/markdown",
            key="sidebar_download_button",
        )
        st.markdown("---")

        # Edit Menu
        st.subheader("✏️ Edit")
        if st.button("➕ Add New Block", key="sidebar_add_block_button"):
            st.session_state.documentEditorBlocks.append(
                create_editor_block(content="# New Block\n\nStart writing here...")
            )
            st.rerun()
        st.markdown("---")

        # View Menu
        st.subheader("👁️ View")
        if "show_debug_modal" not in st.session_state:  # Initialize if not present
            st.session_state.show_debug_modal = False

        if st.button("Toggle Debug Info", key="sidebar_toggle_debug_button"):
            st.session_state.show_debug_modal = not st.session_state.show_debug_modal
            st.rerun()  # Rerun to update modal visibility


# --- Main Application ---
# R0915: Too many statements (80/50) - main() is long due to UI setup.
# Breaking it down might involve passing st object or using classes,
# which could increase complexity. Accepting for now.
def main():  # pylint: disable=too-many-statements,too-many-branches
    """Main function to run the Streamlit application."""
    st.set_page_config(layout="wide", page_title="Pandoc Block Editor")

    # Inject Global Custom CSS
    # Line lengths adjusted
    st.markdown(
        """<style>
            div[data-testid="stHorizontalBlock"] { align-items: flex-start; }
            .block-id-display {
                font-size: 0.75em; color: #888; margin-bottom: 2px;
                height: 20px; line-height: 20px;
            }
            div[data-testid="stTextArea"] > label { display: none; }
            div[data-testid="stTextArea"] textarea { padding-top: 5px; }
            .block-preview-wrapper > div { padding-top: 5px; margin-top:0; }
            hr {
                margin-top: 10px !important; margin-bottom: 10px !important;
                border-top: 1px solid #ddd !important;
            }
            [data-testid="stSidebarNav"] { display: none; }
            .stButton>button { width: 100%; margin-bottom: 5px; }
            div[data-testid="stFileUploader"] > label {
                width: 100%; display: block; text-align: center;
                padding: 0.25rem 0.75rem; background-color: #f0f2f6;
                color: #31333F; border: 1px solid #f0f2f6;
                border-radius: 0.25rem; cursor: pointer; margin-bottom: 5px;
            }
            div[data-testid="stFileUploader"] > label:hover {
                border-color: #ff4b4b; color: #ff4b4b;
            }
            div[data-testid="stDownloadButton"] > button:hover {
                border-color: #ff4b4b !important; color: #ff4b4b !important;
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
            packages: {'[-]': ['mhchem', 'physics', 'ams']}, // Attempt to disable mhchem and other common auto-loads not strictly needed for basic math
            inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
            displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
            processEscapes: true
          },
          // loader: { // Might need to configure loader if packages alone isn't enough
          //   load: ['input/tex', 'output/chtml', 'ui/menu'] // Minimal set
          // },
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

    # --- Sidebar (Menubar) ---
    _render_sidebar_menu()

    # --- Main Content Area ---
    st.title("Pandoc Block Editor")

    # Add the FAB and its hidden trigger button
    # The key for the hidden button must match the one used in ui_elements.render_floating_add_button()
    hidden_add_block_key = "hidden_add_block_trigger_button"
    if st.button(
        "Add Block (Hidden Trigger)",
        key=hidden_add_block_key,
        help="This is hidden and triggered by FAB",
        type="primary",
        # Use some CSS to truly hide it if Streamlit's default button is still visible
        # However, st.button doesn't have a direct visibility param.
        # A common trick is to put it in an empty container that's not rendered,
        # or use st.columns to make it very small / out of sight.
        # For now, let's assume the FAB's JS can click it even if technically in DOM.
        # A cleaner way is to use st.session_state flags if JS can set them.
        # Given the current FAB JS, it expects a clickable button.
        # We can wrap it in a div and hide the div with CSS.
    ):
        st.session_state.documentEditorBlocks.append(create_editor_block(content=""))
        st.rerun()

    # Render the FAB - this should be done after the hidden button it triggers
    # so the button exists in the DOM when the FAB's JS might run.
    st.components.v1.html(
        ui_elements.render_floating_add_button(), height=100
    )  # Increased height

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
        print("[PERF_LOG] main: Starting initial load processing.")
        initial_load_start_time = time.time()

        initial_content_to_load = st.session_state.get(
            "initial_markdown_content", st.session_state.default_markdown_content
        )

        print(
            f"[PERF_LOG] main: Calling parse_full_markdown_to_editor_blocks (content len: {len(initial_content_to_load)})"
        )
        parse_call_start_time = time.time()
        try:
            parsed_blocks = parse_full_markdown_to_editor_blocks(
                initial_content_to_load
            )
            parse_call_duration = time.time() - parse_call_start_time
            print(
                f"[PERF_LOG] main: parse_full_markdown_to_editor_blocks returned in {parse_call_duration:.4f}s"
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
        # The duplicated except block that caused W0705 is now removed.

        st.session_state.initial_load_processed = True
        if "initial_markdown_content" in st.session_state:
            del st.session_state.initial_markdown_content
        if "default_markdown_content" in st.session_state:
            del st.session_state.default_markdown_content

        initial_load_duration = time.time() - initial_load_start_time
        print(
            f"[PERF_LOG] main: Initial load processing finished in {initial_load_duration:.4f}s"
        )

    # --- Document Flow Area (Editor and Preview Panes) ---
    editor_pane, preview_pane = st.columns(2)

    with editor_pane:
        render_editor_start_time = time.time()
        _render_editor_pane()
        render_editor_duration = time.time() - render_editor_start_time
        print(
            f"[PERF_LOG] main: _render_editor_pane finished in {render_editor_duration:.4f}s"
        )

    with preview_pane:
        render_preview_start_time = time.time()
        _render_preview_pane()
        render_preview_duration = time.time() - render_preview_start_time
        print(
            f"[PERF_LOG] main: _render_preview_pane finished in {render_preview_duration:.4f}s"
        )

    # Debug Modal - Rendered based on session state.
    debug_data_str = json.dumps(
        st.session_state.documentEditorBlocks, indent=2, ensure_ascii=False
    )
    # Ensure show_debug_modal is initialized (already done in sidebar logic, but good for safety)
    if "show_debug_modal" not in st.session_state:
        st.session_state.show_debug_modal = False

    # The height of the component can be minimal as the modal is fixed position.
    # The component itself doesn't take up space in the normal document flow.
    st.components.v1.html(
        ui_elements.render_debug_modal(
            debug_data_json_string=debug_data_str,
            initial_visible=st.session_state.show_debug_modal,
        ),
        height=0,  # Modal is fixed, doesn't need layout space.
    )


if __name__ == "__main__":
    main()
