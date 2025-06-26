"""
Custom UI elements for the Pandoc Block Editor,
rendered using st.components.v1.html.
"""

import json  # For passing data to JS
# import streamlit as st # pylint: disable=import-error # Streamlit is not used in this file directly

# render_file_menu() has been removed as its functionality is now in Streamlit sidebar.


def render_debug_modal(debug_data_json_string="{}"):
    """
    Renders the HTML for the debug modal.
    The toggle button is removed from here; it's controlled by Streamlit sidebar.
    - debug_data_json_string: A JSON string of the data to display.
    """
    escaped_debug_data = json.dumps(
        debug_data_json_string
    )  # Escape for JS string literal

    # Lines broken for readability and to pass line length checks
    html_content = f"""
    <div id="debug-modal-overlay-container" style="display: none;">
        <div id="debug-modal-panel-content">
            <button id="debug-modal-close-btn" title="Close Debug View">&times;</button>
            <h3>Document Blocks (Debug Data)</h3>
            <pre id="debug-modal-actual-content"></pre>
        </div>
    </div>"""

    script_content = f"""
    <script>
        // Ensure functions are globally accessible or attached to window if not already
        if (!window.showDebugModal) {{
            window.showDebugModal = function() {{
                const overlay = document.getElementById('debug-modal-overlay-container');
                const panel = document.getElementById('debug-modal-panel-content');
                if (!overlay || !panel) return;
                overlay.style.display = 'flex';
                setTimeout(() => {{ panel.style.transform = 'translateY(0)'; }}, 10);
            }};
        }}

        if (!window.hideDebugModal) {{
            window.hideDebugModal = function() {{
                const overlay = document.getElementById('debug-modal-overlay-container');
                const panel = document.getElementById('debug-modal-panel-content');
                if (!overlay || !panel) return;
                panel.style.transform = 'translateY(100%)';
                setTimeout(() => {{ overlay.style.display = 'none'; }}, 300);
            }};
        }}

        // Initialize or update content when modal HTML is rendered/re-rendered
        (function initializeOrUpdateDebugModal() {{
            const overlay = document.getElementById('debug-modal-overlay-container');
            const closeBtn = document.getElementById('debug-modal-close-btn');
            const contentHolder = document.getElementById('debug-modal-actual-content');

            if (!contentHolder) return;

            const rawDebugStr = {escaped_debug_data};
            try {{
                const jsonData = JSON.parse(rawDebugStr);
                contentHolder.textContent = JSON.stringify(jsonData, null, 2);
            }} catch (e) {{
                console.error("Error parsing debug data JSON for modal:", e);
                contentHolder.textContent = "Error parsing debug data: " + rawDebugStr;
            }}

            if (closeBtn && !closeBtn.dataset.listenerAttached) {{
                closeBtn.addEventListener('click', window.hideDebugModal);
                closeBtn.dataset.listenerAttached = 'true';
            }}
            if (overlay && !overlay.dataset.listenerAttached) {{
                overlay.addEventListener('click', function(event) {{
                    if (event.target === overlay) window.hideDebugModal();
                }});
                overlay.dataset.listenerAttached = 'true';
            }}
        }})();
    </script>"""

    style_content = """
    <style>
        #debug-modal-overlay-container {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background-color: rgba(0,0,0,0.5);
            display: none; /* Initially hidden, controlled by JS */
            justify-content: center; align-items: flex-end;
            z-index: 10001;
        }
        #debug-modal-panel-content {
            background-color: #fefefe; padding: 20px;
            border-top-left-radius: 10px; border-top-right-radius: 10px;
            box-shadow: 0 -5px 15px rgba(0,0,0,0.3);
            width: 90%; max-width: 800px; height: 60vh; max-height: 500px;
            overflow-y: hidden; display: flex; flex-direction: column;
            transform: translateY(100%); transition: transform 0.3s ease-out;
        }
        #debug-modal-panel-content h3 { margin-top: 0; color: #333; }
        #debug-modal-close-btn {
            position: absolute; top: 10px; right: 15px; font-size: 28px;
            font-weight: bold; color: #aaa; background: none; border: none;
            cursor: pointer;
        }
        #debug-modal-close-btn:hover { color: #333; }
        #debug-modal-actual-content {
            flex-grow: 1; background-color: #282c34; color: #abb2bf;
            padding: 15px; border-radius: 5px; overflow-y: auto; white-space: pre;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier,
                         monospace; /* Line broken for length */
            font-size: 0.85em;
        }
    </style>"""
    return html_content + script_content + style_content


# render_floating_add_button() has been removed.

if __name__ == "__main__":
    print("\n--- Debug Modal (Example Usage) ---")
    SAMPLE_DATA = {"key": "value", "blocks": [1, 2, 3]}
    print(render_debug_modal(json.dumps(SAMPLE_DATA)))
