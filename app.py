import streamlit as st
import uuid
import pandoc_utils # Import the new module
from io import StringIO # Needed for file uploader processing
import json # For passing debug data
import ui_elements # Import the new UI elements module

# --- Global Helper Functions & Data Structures ---

def create_editor_block(id=None, kind="paragraph", content="", attributes=None, level=0):
    """Creates an EditorBlock dictionary."""
    return { "id": id if id else str(uuid.uuid4()), "kind": kind, "content": content, "attributes": attributes if attributes else {}, "level": level }

def parse_full_markdown_to_editor_blocks(full_markdown_string):
    if not full_markdown_string: return [create_editor_block(content="")]
    try: ast = pandoc_utils.parse_markdown_to_ast_json(full_markdown_string)
    except RuntimeError as e:
        st.error(f"Failed to parse Markdown AST: {e}")
        return [create_editor_block(content=full_markdown_string, kind="paragraph")]
    editor_blocks, pandoc_api_version = [], ast.get("pandoc-api-version", [1, 22])
    for ast_block in ast.get('blocks', []):
        block_id_str = None
        attrs_container = ast_block.get('c', [])
        if isinstance(attrs_container, list) and len(attrs_container) > 0:
            attrs_tuple = None
            if ast_block['t'] == 'Header' and len(attrs_container) > 1 and isinstance(attrs_container[1], list): attrs_tuple = attrs_container[1]
            elif ast_block['t'] == 'Div' and isinstance(attrs_container[0], list): attrs_tuple = attrs_container[0]
            if attrs_tuple and len(attrs_tuple) > 0 and isinstance(attrs_tuple[0], str): block_id_str = attrs_tuple[0] if attrs_tuple[0] else None
        
        if ast_block['t'] == 'Header':
            level, header_attrs, inlines = ast_block['c'][0], ast_block['c'][1], ast_block['c'][2]
            actual_id = header_attrs[0] if header_attrs[0] else str(uuid.uuid4())
            content_ast = {"pandoc-api-version": pandoc_api_version, "meta": {}, "blocks": [{"t": "Plain", "c": inlines}]}
            content = pandoc_utils.convert_ast_json_to_markdown(content_ast, is_full_ast=True).strip()
            editor_blocks.append(create_editor_block(id=actual_id, kind='heading', level=level, content=content, attributes=dict(header_attrs[2])))
        elif ast_block['t'] == 'Div':
            div_attrs, inner_blocks = ast_block['c'][0], ast_block['c'][1]
            actual_id = div_attrs[0] if div_attrs[0] else str(uuid.uuid4())
            content_ast = {"pandoc-api-version": pandoc_api_version, "meta": {}, "blocks": inner_blocks}
            content = pandoc_utils.convert_ast_json_to_markdown(content_ast, is_full_ast=True)
            editor_blocks.append(create_editor_block(id=actual_id, kind='semantic', content=content, attributes={'id': actual_id, 'classes': div_attrs[1], 'keyvals': dict(div_attrs[2])}))
        else:
            content_ast = {"pandoc-api-version": pandoc_api_version, "meta": {}, "blocks": [ast_block]}
            content = pandoc_utils.convert_ast_json_to_markdown(content_ast, is_full_ast=True).strip()
            editor_blocks.append(create_editor_block(id=block_id_str if block_id_str else str(uuid.uuid4()), kind='paragraph', content=content, attributes={}))
    return editor_blocks if editor_blocks else [create_editor_block(content="")]

def handle_block_content_change(block_id, editor_key):
    new_content = st.session_state[editor_key]
    for block in st.session_state.documentEditorBlocks:
        if block['id'] == block_id: block['content'] = new_content; break

def reconstruct_markdown_from_editor_blocks():
    parts = []
    for block in st.session_state.documentEditorBlocks:
        if block['kind'] == 'heading':
            attrs = []
            if block.get('id'): attrs.append(f"#{block['id']}")
            if block['attributes'].get('classes'): attrs.extend([f".{cls}" for cls in block['attributes']['classes']])
            if block['attributes'].get('keyvals'): attrs.extend([f'{k}="{v}"' for k, v in block['attributes']['keyvals'].items()])
            attr_str = f" {{{' '.join(attrs)}}}" if attrs else ""
            parts.append(f"{'#' * block['level']} {block['content']}{attr_str}")
        elif block['kind'] == 'semantic':
            attrs = []
            div_attrs = block.get('attributes', {})
            if div_attrs.get('id'): attrs.append(f"#{div_attrs['id']}")
            if div_attrs.get('classes'): attrs.extend([f".{cls}" for cls in div_attrs['classes']])
            if div_attrs.get('keyvals'): attrs.extend([f'{k}="{v}"' for k, v in div_attrs['keyvals'].items()])
            attr_str = f" {{{' '.join(attrs)}}}" if attrs else ""
            content = block['content']
            content = (content + '\n') if content and not content.endswith('\n') else (content if content else '\n')
            parts.append(f":::{attr_str}\n{content}:::")
        else: parts.append(block['content'])
    return "\n\n".join(parts)

# --- Streamlit Session State Initialization ---
if 'documentEditorBlocks' not in st.session_state:
    st.session_state.documentEditorBlocks = [create_editor_block(content="")]
    st.session_state.initial_load_processed = False
    try:
        with open("test.md", "r", encoding="utf-8") as f: st.session_state.initial_markdown_content = f.read()
    except FileNotFoundError: st.session_state.initial_markdown_content = None
    except Exception: st.session_state.initial_markdown_content = None

# --- Main Application ---
def main():
    st.set_page_config(layout="wide", page_title="Pandoc Block Editor")

    # Inject Global Custom CSS for alignment and styling
    # Step 6: UI Adjustments and Styling for Vertical Alignment
    st.markdown("""
        <style>
            /* Ensure columns themselves don't add unexpected vertical space */
            .stApp > header { display: none; } /* Hide default Streamlit header if not used */
            div[data-testid="stHorizontalBlock"] { align-items: flex-start; } /* Align items at the start of cross axis */

            .block-id-display {
                font-size: 0.75em;
                color: #888;
                margin-bottom: 2px; /* Small space before the main content block */
                height: 20px; /* Fixed height for alignment */
                line-height: 20px; /* Vertically center text if needed */
            }
            /* Specific styling for editor text_area and preview div might be needed */
            /* Try to ensure the text_area and the preview div start at the same vertical point after ID */
            div[data-testid="stTextArea"] > label { display: none; } /* Hide text_area label if not needed */
            div[data-testid="stTextArea"] textarea { padding-top: 5px; } /* Adjust as needed */
            
            /* Ensure preview div has similar top padding/margin to text_area's internal content */
            .block-preview-wrapper > div { padding-top: 5px; margin-top:0; } /* Target first div inside wrapper */

            /* Horizontal rule styling for consistency */
            hr {
                margin-top: 10px !important;
                margin-bottom: 10px !important;
                border-top: 1px solid #ddd !important; /* Make it visible and consistent */
            }
        </style>
    """, unsafe_allow_html=True)


    # MathJax Setup
    st.markdown("""
        <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
        <script>
        window.MathJax = {
          tex: { inlineMath: [['$', '$'], ['\\\\(', '\\\\)']], displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']], processEscapes: true },
          svg: { fontCache: 'global' },
          options: { skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code'], ignoreHtmlClass: 'tex2jax_ignore', processHtmlClass: 'tex2jax_process'}
        };
        window.typesetMathJaxForElement = function(elementId) {
            if (window.MathJax && window.MathJax.typesetPromise) {
                const element = document.getElementById(elementId);
                if (element) { window.MathJax.typesetPromise([element]).catch((err) => console.error('MathJax error for ' + elementId + ':', err)); }
                else { console.warn('MathJax typeset: Element not found: ' + elementId); }
            } else { console.warn('MathJax not ready for element: ' + elementId); }
        };
        </script>
    """, unsafe_allow_html=True)

    # Initial load of test.md
    if not st.session_state.get('initial_load_processed', False):
        initial_content = st.session_state.get('initial_markdown_content')
        if initial_content:
            try:
                parsed_blocks = parse_full_markdown_to_editor_blocks(initial_content)
                if parsed_blocks: st.session_state.documentEditorBlocks = parsed_blocks
                else:
                    st.warning("test.md parsed to no blocks. Starting with default.")
                    st.session_state.documentEditorBlocks = [create_editor_block(content="")]
            except Exception as e:
                st.error(f"Error parsing test.md: {e}. Starting with default.")
                st.session_state.documentEditorBlocks = [create_editor_block(content="")]
        elif initial_content is None and 'initial_markdown_content' in st.session_state:
            st.info("test.md not found. Starting with default.")
            st.session_state.documentEditorBlocks = [create_editor_block(content="")]
        st.session_state.initial_load_processed = True
        if 'initial_markdown_content' in st.session_state: del st.session_state.initial_markdown_content

    # --- UI Elements Rendering ---
    st.markdown(ui_elements.render_file_menu(), unsafe_allow_html=True)
    st.markdown('<div id="streamlit_file_uploader_wrapper" style="display: none;">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("OpenHidden", type=['md', 'markdown'], key="hidden_file_uploader", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    if uploaded_file is not None:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        st.session_state.documentEditorBlocks = parse_full_markdown_to_editor_blocks(stringio.read())
        st.rerun() 
    
    full_doc_md = reconstruct_markdown_from_editor_blocks()
    st.markdown('<div id="streamlit_download_button_wrapper" style="display: none;">', unsafe_allow_html=True)
    st.download_button(label="SaveHidden", data=full_doc_md, file_name="document.md", mime="text/markdown", key="hidden_download_button")
    st.markdown('</div>', unsafe_allow_html=True)

    st.title("Pandoc Block Editor") # Title below the file menu

    st.markdown(ui_elements.render_floating_add_button(), unsafe_allow_html=True)
    st.markdown('<div id="hidden_add_block_button_trigger_div" style="display: none;">', unsafe_allow_html=True)
    if st.button("AddBlockHidden", key="hidden_add_block_button", help="Hidden add block trigger"):
        st.session_state.documentEditorBlocks.append(create_editor_block(content=""))
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Document Flow Area (Editor and Preview Panes) ---
    editor_pane, preview_pane = st.columns(2)

    with editor_pane:
        # st.subheader("📝 Editor Pane") # Removed
        for i, block in enumerate(st.session_state.documentEditorBlocks):
            st.markdown(f"<div class='block-id-display editor-block-id'>Editor ID: `{block['id']}`</div>", unsafe_allow_html=True)
            editor_key = f"editor_{block['id']}_{i}"
            # The label for st.text_area will be hidden by CSS if not desired.
            st.text_area(
                label=f"Block Content {i+1} ({block['kind']})", # Label provides context for screen readers
                value=block['content'], key=editor_key,
                on_change=handle_block_content_change, args=(block['id'], editor_key),
                height=max(150, int(len(block['content']) / 1.5)) # Slightly taller based on content
            )
            st.markdown("---") # Horizontal rule

    with preview_pane:
        # st.subheader("👀 Preview Pane") # Removed
        for i, block in enumerate(st.session_state.documentEditorBlocks):
            st.markdown(f"<div class='block-id-display viewer-block-id'>Viewer ID: `{block['id']}`</div>", unsafe_allow_html=True)
            preview_div_id = f"preview-block-{block['id']}-{i}"
            try:
                html_content = pandoc_utils.convert_markdown_to_html(block['content'])
                # Added a wrapper class for more specific CSS targeting if needed
                st.markdown(f"<div id='{preview_div_id}' class='block-preview-wrapper'>{html_content}</div>", unsafe_allow_html=True)
                js_typeset_script = f"""
                <script>
                setTimeout(function() {{
                    if (typeof window.typesetMathJaxForElement === 'function') {{ window.typesetMathJaxForElement('{preview_div_id}'); }}
                    else {{
                        let attempts = 0; const maxAttempts = 5; const interval = 100;
                        function retryTypeset() {{
                            if (typeof window.typesetMathJaxForElement === 'function') {{ window.typesetMathJaxForElement('{preview_div_id}'); }}
                            else if (attempts < maxAttempts) {{ attempts++; setTimeout(retryTypeset, interval); }}
                            else {{ console.error('window.typesetMathJaxForElement not found for {preview_div_id}'); }} }}
                        retryTypeset();
                    }} }}, 50);
                </script>"""
                st.components.v1.html(js_typeset_script, height=0)
            except RuntimeError as e: st.error(f"Error rendering block {block['id']}:\n{e}")
            except Exception as e: st.error(f"Unexpected error rendering block {block['id']}:\n{e}")
            st.markdown("---") # Horizontal rule
    
    # Debug Modal
    debug_data_str = json.dumps(st.session_state.documentEditorBlocks, indent=2, ensure_ascii=False)
    st.components.v1.html(ui_elements.render_debug_modal(debug_data_str), height=0)
    
if __name__ == "__main__":
    main()

