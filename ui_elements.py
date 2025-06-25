"""
Custom UI elements for the Pandoc Block Editor, rendered using st.components.v1.html.
"""

import streamlit as st
import json # For passing data to JS

def render_file_menu():
    """
    Renders a placeholder for the File dropdown menu.
    Actual implementation will involve HTML/CSS/JS for dropdown behavior
    and mechanisms to trigger Python callbacks for 'Open' and 'Save'.
    """
    # For now, just a placeholder.
    # In a real implementation, this would be more complex, likely involving
    # JavaScript to handle dropdown clicks and communicate back to Streamlit.
    html = """
    <div class="file-menu-placeholder">
        <strong>File Menu (Placeholder)</strong>
        <button onclick="handleFileMenu('open')">Open</button>
        <button onclick="handleFileMenu('save')">Save</button>
    </div>
    <div id="file-menu-container">
        <button id="file-menu-button" onclick="toggleFileMenu()">File</button>
        <ul id="file-menu-dropdown" style="display: none;">
            <li onclick="triggerStreamlitAction('streamlit_file_uploader')">Open from Disk...</li>
            <li onclick="triggerStreamlitAction('streamlit_download_button')">Save to Disk...</li>
        </ul>
    </div>
    <script>
        function toggleFileMenu() {
            var dropdown = document.getElementById('file-menu-dropdown');
            dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
        }

        function triggerStreamlitAction(elementId) {
            // Find the Streamlit widget (which will be hidden).
            // Streamlit widgets are often complex structures, we need to find the actual clickable element.
            // For st.file_uploader, it's an input element. For st.download_button, it's an anchor <a> or button.
            // These IDs ('streamlit_file_uploader', 'streamlit_download_button') will be assigned to
            // wrapper divs around the actual Streamlit widgets in app.py.
            
            var targetElement = null;
            if (elementId === 'streamlit_file_uploader') {
                // st.file_uploader creates a label which, when clicked, triggers the input.
                // Or, we might need to find the input[type="file"] directly.
                // Let's assume we wrap st.file_uploader in a div with id="streamlit_file_uploader_wrapper"
                // and the actual input is inside.
                // A common trick: the label itself can be targeted.
                // Streamlit often generates labels like `label-for-<widget-id>`.
                // For simplicity, we'll assume the *wrapper div* we create has the ID,
                // and we trigger a click on the first interactive child.
                const wrapper = document.getElementById('streamlit_file_uploader_wrapper');
                if (wrapper) {
                    // Try to find the actual input file element
                    targetElement = wrapper.querySelector('input[type="file"]');
                    if (!targetElement) { // Fallback: try clicking the first button-like element if any
                         targetElement = wrapper.querySelector('button, label');
                    }
                }
            } else if (elementId === 'streamlit_download_button') {
                // st.download_button renders as a button.
                // We'll wrap it in a div with id="streamlit_download_button_wrapper"
                const wrapper = document.getElementById('streamlit_download_button_wrapper');
                if (wrapper) {
                    targetElement = wrapper.querySelector('button');
                }
            }

            if (targetElement) {
                targetElement.click();
                console.log("Clicked hidden element for action: " + elementId);
            } else {
                console.error("Could not find target Streamlit widget for action: " + elementId + ". Ensure wrappers have correct IDs.");
                alert("Action '" + elementId.replace('streamlit_', '') + "' failed. Widget not found.");
            }
            toggleFileMenu(); // Close menu after action
        }

        // Close dropdown if clicking outside
        window.onclick = function(event) {
            if (!event.target.matches('#file-menu-button')) {
                var dropdown = document.getElementById('file-menu-dropdown');
                if (dropdown.style.display === 'block') {
                    dropdown.style.display = 'none';
                }
            }
        }
    </script>
    <style>
        #file-menu-container {
            position: relative; /* Or absolute/fixed depending on layout */
            display: inline-block;
            margin-bottom: 15px; /* Space it out a bit */
            font-family: sans-serif;
            z-index: 1000; /* Ensure it's above other elements */
        }
        #file-menu-button {
            background-color: #f0f2f6; /* Streamlit-like button */
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
    Renders a placeholder for the debug modal.
    - debug_data_json_string: A JSON string of the data to display.
    """
    html = f"""
    <button id="debug-modal-toggle" title="Toggle Debug View">🐞</button>
    
    <div id="debug-modal-overlay">
        <div id="debug-modal-panel">
            <button id="debug-modal-close" title="Close Debug View">&times;</button>
            <h3>Document Blocks (Debug Data)</h3>
            <pre id="debug-modal-content"></pre>
        </div>
    </div>

    <script>
        const debugModalOverlay = document.getElementById('debug-modal-overlay');
        const debugModalPanel = document.getElementById('debug-modal-panel');
        const debugModalToggle = document.getElementById('debug-modal-toggle');
        const debugModalClose = document.getElementById('debug-modal-close');
        const debugModalContent = document.getElementById('debug-modal-content');

        const debugData = {debug_data_json_string};

        debugModalContent.textContent = JSON.stringify(debugData, null, 2);

        function showDebugModal() {{
            debugModalOverlay.style.display = 'flex';
            setTimeout(() => {{ // Allow display change to register before transition
                debugModalPanel.style.transform = 'translateY(0)';
            }}, 10);
        }}

        function hideDebugModal() {{
            debugModalPanel.style.transform = 'translateY(100%)';
            setTimeout(() => {{ // Wait for transition to finish
                debugModalOverlay.style.display = 'none';
            }}, 300); // Corresponds to CSS transition duration
        }}

        debugModalToggle.addEventListener('click', showDebugModal);
        debugModalClose.addEventListener('click', hideDebugModal);
        debugModalOverlay.addEventListener('click', function(event) {{
            if (event.target === debugModalOverlay) {{ // Click on overlay itself, not panel
                hideDebugModal();
            }}
        }});
    </script>
    <style>
        #debug-modal-toggle {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 50px;
            height: 50px;
            background-color: #6c757d; /* Gray */
            color: white;
            border: none;
            border-radius: 50%;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            z-index: 1000;
        }}
        #debug-modal-toggle:hover {{
            background-color: #5a6268;
        }}
        #debug-modal-overlay {{
            display: none; /* Hidden by default */
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5); /* Semi-transparent overlay */
            justify-content: center; /* For centering panel, not used with bottom slide */
            align-items: flex-end; /* Align panel to bottom */
            z-index: 1001; 
        }}
        #debug-modal-panel {{
            background-color: #fefefe;
            padding: 20px;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            box-shadow: 0 -5px 15px rgba(0,0,0,0.3);
            width: 90%;
            max-width: 800px; /* Max width for larger screens */
            height: 60vh; /* 60% of viewport height */
            max-height: 500px;
            overflow-y: hidden; /* Modal panel itself does not scroll */
            display: flex;
            flex-direction: column;
            transform: translateY(100%); /* Start off-screen */
            transition: transform 0.3s ease-out;
        }}
        #debug-modal-panel h3 {{
            margin-top: 0;
            color: #333;
        }}
        #debug-modal-close {{
            position: absolute;
            top: 10px;
            right: 15px;
            font-size: 28px;
            font-weight: bold;
            color: #aaa;
            background: none;
            border: none;
            cursor: pointer;
        }}
        #debug-modal-close:hover {{
            color: #333;
        }}
        #debug-modal-content {{
            flex-grow: 1; /* Allows pre to take available space */
            background-color: #282c34; /* Dark background for JSON */
            color: #abb2bf; /* Light text for JSON */
            padding: 15px;
            border-radius: 5px;
            overflow-y: auto; /* Enable scrolling for content */
            white-space: pre; /* Keep JSON formatting */
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
            font-size: 0.85em;
        }}
    </style>
    """
    return html

def render_floating_add_button():
    """
    Renders a placeholder for the floating action button (FAB) to add blocks.
    """
    # This will be styled with CSS to float at bottom-left.
    # JS will handle click and communication back to Streamlit by clicking a hidden button.
    # The target hidden button in app.py should have the id 'hidden_add_block_button_trigger_div' wrapping it.
    html = """
    <div id="floating-add-button" title="Add New Block">
        +
    </div>
    <script>
        document.getElementById('floating-add-button').addEventListener('click', function() {
            const hiddenButtonWrapper = document.getElementById('hidden_add_block_button_trigger_div');
            if (hiddenButtonWrapper) {
                const hiddenButton = hiddenButtonWrapper.querySelector('button');
                if (hiddenButton) {
                    hiddenButton.click();
                    console.log('Clicked hidden add block button.');
                } else {
                    console.error('Hidden add block button (actual button element) not found inside wrapper.');
                    alert('Error: Add block action failed (button not found).');
                }
            } else {
                console.error('Hidden add block button wrapper div not found.');
                alert('Error: Add block action failed (wrapper not found).');
            }
        });
    </script>
    <style>
        #floating-add-button {
            position: fixed;
            bottom: 30px;
            left: 30px;
            width: 56px;
            height: 56px;
            background-color: #007bff; /* Standard blue */
            color: white;
            border-radius: 50%;
            text-align: center;
            line-height: 56px; /* Vertically center '+' */
            font-size: 28px; /* Size of '+' */
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2), 0 6px 20px rgba(0,0,0,0.19);
            z-index: 999; /* Ensure it's above most other content */
            user-select: none; /* Prevent text selection on click */
        }
        #floating-add-button:hover {
            background-color: #0056b3; /* Darker blue on hover */
        }
    </style>
    """
    return html

if __name__ == '__main__':
    # Example of how these might be called (won't render correctly outside Streamlit)
    print("--- File Menu ---")
    print(render_file_menu())
    print("\n--- Debug Modal ---")
    sample_data = {"key": "value", "blocks": [1,2,3]}
    print(render_debug_modal(json.dumps(sample_data, indent=2)))
    print("\n--- Floating Add Button ---")
    print(render_floating_add_button())

