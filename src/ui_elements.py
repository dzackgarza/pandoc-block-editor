"""
Custom UI elements for the Pandoc Block Editor, rendered using st.components.v1.html.
"""

import streamlit as st
import json  # For passing data to JS


def render_file_menu():
    """
    Renders the HTML for the File dropdown menu.
    """
    html = """
    <div id="file-menu-container">
        <button id="file-menu-button" onclick="toggleFileMenu(event)">File</button>
        <ul id="file-menu-dropdown" style="display: none;">
            <li onclick="triggerStreamlitAction('streamlit_file_uploader_wrapper', event)">Open from Disk...</li>
            <li onclick="triggerStreamlitAction('streamlit_download_button_wrapper', event)">Save to Disk...</li>
        </ul>
    </div>
    <script>
        function toggleFileMenu(event) {
            event.stopPropagation(); // Prevent window.onclick from closing menu immediately
            var dropdown = document.getElementById('file-menu-dropdown');
            dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
        }

        function triggerStreamlitAction(wrapperId, event) {
            event.stopPropagation(); // Prevent window.onclick from closing menu immediately
            const wrapper = document.getElementById(wrapperId);
            if (wrapper) {
                const targetElement = wrapper.querySelector('input[type="file"], button, label');
                if (targetElement) {
                    targetElement.click();
                    console.log("Clicked hidden element via wrapper: " + wrapperId);
                } else {
                    console.error("No clickable element found in wrapper: " + wrapperId);
                    alert("Action failed: UI element not found.");
                }
            } else {
                console.error("Could not find Streamlit widget wrapper: " + wrapperId);
                alert("Action failed: UI wrapper not found.");
            }
            var dropdown = document.getElementById('file-menu-dropdown');
            if (dropdown) dropdown.style.display = 'none'; // Close menu after action
        }

        // Close dropdown if clicking outside
        window.addEventListener('click', function(event) {
            var dropdown = document.getElementById('file-menu-dropdown');
            var menuButton = document.getElementById('file-menu-button');
            // If dropdown is visible and the click is not on the menu button itself
            // and not inside the dropdown menu (though clicks inside dropdown are handled by stopPropagation)
            if (dropdown && dropdown.style.display === 'block' && !menuButton.contains(event.target) && !dropdown.contains(event.target)) {
                dropdown.style.display = 'none';
            }
        });
    </script>
    <style>
        #file-menu-container {
            position: relative;
            display: inline-block;
            margin-bottom: 15px;
            font-family: sans-serif;
            z-index: 10000; /* High z-index */
        }
        #file-menu-button {
            background-color: #f0f2f6;
            color: #31333F;
            padding: 8px 12px;
            border: 1px solid #d3d3d3;
            border-radius: 0.25rem;
            cursor: pointer;
        }
        #file-menu-dropdown {
            display: none;
            position: absolute;
            background-color: white;
            min-width: 160px;
            box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
            padding: 0;
            margin: 0;
            list-style-type: none;
            border: 1px solid #ddd;
            border-radius: 0.25rem;
        }
        #file-menu-dropdown li {
            padding: 10px 15px;
            text-decoration: none;
            display: block;
            cursor: pointer;
            color: #31333F;
        }
        #file-menu-dropdown li:hover {
            background-color: #f0f2f6;
        }
    </style>
    """
    return html


def render_debug_modal(debug_data_json_string="{}"):
    """
    Renders the HTML for the debug modal.
    - debug_data_json_string: A JSON string of the data to display.
    """
    escaped_debug_data = json.dumps(
        debug_data_json_string
    )  # Escape for JS string literal

    html = f"""
    <button id="debug-modal-toggle-btn" title="Toggle Debug View">🐞</button>

    <div id="debug-modal-overlay-container" style="display: none;">
        <div id="debug-modal-panel-content">
            <button id="debug-modal-close-btn" title="Close Debug View">&times;</button>
            <h3>Document Blocks (Debug Data)</h3>
            <pre id="debug-modal-actual-content"></pre>
        </div>
    </div>

    <script>
        const debugModalOverlay = document.getElementById('debug-modal-overlay-container');
        const debugModalPanel = document.getElementById('debug-modal-panel-content');
        const debugModalToggle = document.getElementById('debug-modal-toggle-btn');
        const debugModalClose = document.getElementById('debug-modal-close-btn');
        const debugContentHolder = document.getElementById('debug-modal-actual-content');

        const rawDebugStrForModal = {escaped_debug_data};
        try {{
            const jsonData = JSON.parse(rawDebugStrForModal); // Parse the string from Python
            debugContentHolder.textContent = JSON.stringify(jsonData, null, 2); // Re-stringify for pretty print
        }} catch (e) {{
            console.error("Error parsing debug data JSON for modal:", e);
            debugContentHolder.textContent = "Error parsing debug data: " + rawDebugStrForModal;
        }}

        function showDebugModal() {{
            if (!debugModalOverlay || !debugModalPanel) return;
            debugModalOverlay.style.display = 'flex';
            setTimeout(() => {{
                debugModalPanel.style.transform = 'translateY(0)';
            }}, 10);
        }}

        function hideDebugModal() {{
            if (!debugModalOverlay || !debugModalPanel) return;
            debugModalPanel.style.transform = 'translateY(100%)';
            setTimeout(() => {{
                debugModalOverlay.style.display = 'none';
            }}, 300);
        }}

        if (debugModalToggle) debugModalToggle.addEventListener('click', showDebugModal);
        if (debugModalClose) debugModalClose.addEventListener('click', hideDebugModal);
        if (debugModalOverlay) {{
            debugModalOverlay.addEventListener('click', function(event) {{
                if (event.target === debugModalOverlay) hideDebugModal();
            }});
        }}
    </script>
    <style>
        #debug-modal-toggle-btn {{
            position: fixed; bottom: 30px; right: 30px; width: 50px; height: 50px;
            background-color: #6c757d; color: white; border: none; border-radius: 50%;
            font-size: 24px; cursor: pointer; box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            z-index: 10000; /* High z-index */
        }}
        #debug-modal-toggle-btn:hover {{ background-color: #5a6268; }}

        #debug-modal-overlay-container {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background-color: rgba(0,0,0,0.5);
            display: none; /* Initially hidden */
            justify-content: center; align-items: flex-end;
            z-index: 10001; /* Higher than toggle */
        }}
        #debug-modal-panel-content {{
            background-color: #fefefe; padding: 20px;
            border-top-left-radius: 10px; border-top-right-radius: 10px;
            box-shadow: 0 -5px 15px rgba(0,0,0,0.3);
            width: 90%; max-width: 800px; height: 60vh; max-height: 500px;
            overflow-y: hidden; display: flex; flex-direction: column;
            transform: translateY(100%); transition: transform 0.3s ease-out;
        }}
        #debug-modal-panel-content h3 {{ margin-top: 0; color: #333; }}
        #debug-modal-close-btn {{
            position: absolute; top: 10px; right: 15px; font-size: 28px;
            font-weight: bold; color: #aaa; background: none; border: none; cursor: pointer;
        }}
        #debug-modal-close-btn:hover {{ color: #333; }}
        #debug-modal-actual-content {{
            flex-grow: 1; background-color: #282c34; color: #abb2bf;
            padding: 15px; border-radius: 5px; overflow-y: auto; white-space: pre;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
            font-size: 0.85em;
        }}
    </style>
    """
    return html


def render_floating_add_button():
    """
    Renders the HTML for a floating action button (FAB) to add blocks.
    """
    html = """
    <div id="floating-add-block-button" title="Add New Block">
        +
    </div>
    <script>
        const fabElement = document.getElementById('floating-add-block-button');
        if (fabElement) {
            fabElement.addEventListener('click', function() {
                const hiddenButtonWrapper = document.getElementById('hidden_add_block_button_trigger_div');
                if (hiddenButtonWrapper) {
                    const hiddenButton = hiddenButtonWrapper.querySelector('button');
                    if (hiddenButton) {
                        hiddenButton.click();
                        console.log('Clicked hidden add block button via FAB.');
                    } else {
                        console.error('FAB: Hidden add block button (actual button element) not found inside wrapper.');
                        alert('Error: Add block action failed (button not found).');
                    }
                } else {
                    console.error('FAB: Hidden add block button wrapper div not found.');
                    alert('Error: Add block action failed (wrapper not found).');
                }
            });
        } else {
            // This might be normal if the component isn't rendered, but good to know.
            // console.warn("Floating add button element not found by ID: floating-add-block-button");
        }
    </script>
    <style>
        #floating-add-block-button {{
            position: fixed; bottom: 30px; left: 30px; width: 56px; height: 56px;
            background-color: #007bff; color: white; border-radius: 50%;
            text-align: center; line-height: 56px; font-size: 28px; font-weight: bold;
            cursor: pointer; box-shadow: 0 4px 8px rgba(0,0,0,0.2), 0 6px 20px rgba(0,0,0,0.19);
            z-index: 9999; /* High z-index */
            user-select: none;
        }}
        #floating-add-block-button:hover {{ background-color: #0056b3; }}
    </style>
    """
    return html


if __name__ == "__main__":
    print("--- File Menu ---")
    print(render_file_menu())
    print("\n--- Debug Modal ---")
    sample_data = {"key": "value", "blocks": [1, 2, 3]}
    # Pass the string representation of the JSON
    print(render_debug_modal(json.dumps(sample_data)))
    print("\n--- Floating Add Button ---")
    print(render_floating_add_button())
