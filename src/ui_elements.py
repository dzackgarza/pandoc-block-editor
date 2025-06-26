"""
Custom UI elements for the Pandoc Block Editor,
rendered using st.components.v1.html.
"""

import json  # For passing data to JS


def render_debug_modal(debug_data_json_string="{}", initial_visible=False):
    """
    Renders an HTML modal to display debug information.

    Args:
        debug_data_json_string (str): A JSON string representing the data to display.
        initial_visible (bool): Whether the modal should be visible initially.
    """
    modal_id = "debug-info-modal"
    content_id = "debug-modal-content"
    # Determine initial display style based on initial_visible
    initial_display_style = "flex" if initial_visible else "none"

    html_content = f"""
<style>
    #{modal_id} {{
        display: {initial_display_style}; /* Controlled by initial_visible */
        position: fixed;
        z-index: 2000; /* Higher than FAB */
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        overflow: auto;
        background-color: rgba(0,0,0,0.4);
        align-items: center; /* For vertical centering */
        justify-content: center; /* For horizontal centering */
    }}
    .debug-modal-content-wrapper {{
        background-color: #fefefe;
        margin: auto;
        padding: 20px;
        border: 1px solid #888;
        width: 80%;
        max-width: 700px;
        max-height: 80vh; /* Max height to prevent overflow */
        display: flex;
        flex-direction: column;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        border-radius: 5px;
    }}
    .debug-modal-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 10px;
        border-bottom: 1px solid #eee;
    }}
    .debug-modal-header h2 {{
        margin: 0;
        font-size: 1.5em;
    }}
    .debug-modal-close-btn {{
        color: #aaa;
        font-size: 28px;
        font-weight: bold;
        cursor: pointer;
        background: none;
        border: none;
    }}
    .debug-modal-close-btn:hover,
    .debug-modal-close-btn:focus {{
        color: black;
        text-decoration: none;
    }}
    #{content_id} {{
        flex-grow: 1; /* Allow content to take available space */
        overflow-y: auto; /* Scrollable content */
        background-color: #f0f0f0;
        border: 1px solid #ddd;
        padding: 10px;
        font-family: monospace;
        white-space: pre;
        margin-top: 10px;
    }}
</style>

<div id="{modal_id}">
    <div class="debug-modal-content-wrapper">
        <div class="debug-modal-header">
            <h2>Debug Information</h2>
            <button class="debug-modal-close-btn" title="Close Debug Modal">&times;</button>
        </div>
        <pre id="{content_id}">{json.dumps(json.loads(debug_data_json_string), indent=2, ensure_ascii=False)}</pre>
    </div>
</div>

<script>
(function() {{
    const modal = document.getElementById('{modal_id}');
    const closeButton = modal.querySelector('.debug-modal-close-btn');

    function closeModal() {{
        if (modal) modal.style.display = 'none';
        // We cannot directly set st.session_state.show_debug_modal to false here.
        // The Streamlit button "Toggle Debug Info" is responsible for that.
        // This just closes the modal visually. If "Toggle Debug Info" is clicked again
        // while it's true, Streamlit will re-render the component with initial_visible=true.
    }}

    if (closeButton) {{
        closeButton.addEventListener('click', closeModal);
    }}

    // Close modal if clicked outside the content wrapper
    window.addEventListener('click', function(event) {{
        if (event.target === modal) {{
            closeModal();
        }}
    }});

    // Optional: Close with Escape key
    document.addEventListener('keydown', function(event) {{
        if (event.key === "Escape" && modal.style.display === 'flex') {{
            closeModal();
        }}
    }});

    // This component relies on Streamlit to re-render it with the correct
    // initial_visible state. The 'Toggle Debug Info' button in app.py
    // handles st.session_state.show_debug_modal and st.rerun().
    // If initial_visible is true, this script ensures it's shown.
    // If the modal was previously visible due to JavaScript interaction (not Streamlit state)
    // and Streamlit re-renders with initial_visible=false, it will be hidden.
    // The Streamlit state is the source of truth for initial visibility on re-renders.

    // Ensure correct display state on script load based on initial_visible.
    // This is mostly handled by the inline style, but good to be explicit.
    // if ({str(initial_visible).lower()}) {{
    //     if(modal) modal.style.display = 'flex';
    // }} else {{
    //     if(modal) modal.style.display = 'none';
    // }}
    // The above is redundant due to f-string in style.
}})();
</script>
"""
    return html_content


def render_floating_add_button(
    hidden_button_key_prefix="hidden_add_block_trigger_button",
):
    """
    Renders a Floating Action Button (FAB) that clicks a hidden Streamlit button.

    Args:
        hidden_button_key_prefix (str): The prefix of the key used for the hidden
                                       Streamlit button in app.py. Streamlit often
                                       appends to keys, so we search for a button
                                       whose `kind` attribute matches this prefix.
                                       More precisely, Streamlit uses the `key`
                                       in `data-testid` attribute like:
                                       `button-trigger-{key}` or similar, but this
                                       can change. A more robust way is to look for
                                       a button that Streamlit itself has tagged with
                                       the key, or a button with a specific help text.
                                       The current hidden button in app.py has a help text.
    """
    # The help text for the hidden button is "This is hidden and triggered by FAB"
    # Streamlit buttons store their key in a `kind` attribute on the button element
    # or as part of a data-testid. Let's try to find it via the help text.
    # Streamlit button structure can be complex. A more direct way might be if we can assign
    # a unique class or ID to the button, but st.button doesn't allow that directly.
    # The `help` attribute creates a title attribute on an element.

    # Let's try to find the button by its `title` (from `help` text)
    # and then its `kind` (related to Streamlit's internal keying)
    # Streamlit button structure:
    # <button kind="secondary" class="st-emotion-cache-xxx" data-testid="stButton">
    #   <div data-testid="stTooltipHoverTarget" class="st-emotion-cache-yyy">
    #     <span title="This is hidden and triggered by FAB"> <p>Add Block (Hidden Trigger)</p> </span>
    #   </div>
    # </button>
    # So we need to find the button whose span has the specific title.

    html_content = f"""
<style>
    #fab-add-block {{
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 60px;
        height: 60px;
        background-color: #FF4B4B; /* Streamlit's primary color */
        color: white;
        border-radius: 50%;
        text-align: center;
        font-size: 30px;
        line-height: 60px; /* Vertically center '+' */
        cursor: pointer;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        z-index: 1000;
        display: flex; /* For centering content */
        align-items: center; /* For centering content */
        justify-content: center; /* For centering content */
    }}
    #fab-add-block:hover {{
        background-color: #FF6B6B; /* Lighter shade on hover */
    }}
</style>

<div id="fab-add-block" title="Add New Block">
    +
</div>

<script>
    document.addEventListener('DOMContentLoaded', function() {{
        const fabButton = document.getElementById('fab-add-block');
        if (fabButton) {{
            fabButton.addEventListener('click', function() {{
                console.log('FAB clicked');
                // Attempt to find the Streamlit button.
                // Streamlit buttons are complex. The `key` is not directly an ID.
                // The hidden button has help text:
                // "This is hidden and triggered by FAB"
                // This help text becomes a 'title' attribute on an inner span.
                const hiddenButtonHelpText = "This is hidden and triggered by FAB";
                let hiddenButton = null;

                // Search for the span with the specific title attribute
                const selector = 'button span[title="' + hiddenButtonHelpText + '"]';
                const spans = document.querySelectorAll(selector);
                if (spans.length > 0) {{
                    // The actual button is an ancestor of this span
                    hiddenButton = spans[0].closest('button');
                }}

                if (hiddenButton) {{
                    console.log('Hidden trigger button found:', hiddenButton);
                    hiddenButton.click();
                }} else {{
                    console.error(
                        'Hidden trigger button with help text "' +
                        hiddenButtonHelpText + '" not found.'
                    );
                    // Fallback attempt using key prefix if available
                    // (less reliable for complex DOMs)
                    // This part is tricky because Streamlit modifies keys.
                    // For now, the title search is more specific.
                    // Example:
                    // const buttons = Array.from(document.querySelectorAll('button'));
                    // hiddenButton = buttons.find(
                    //    btn => btn.getAttribute('kind')?.startsWith('{hidden_button_key_prefix}')
                    // );
                }}
            }});
        }}
    }});
</script>
"""
    return html_content


if __name__ == "__main__":
    print("\n--- Debug Modal (Simplified Example Usage) ---")
    SAMPLE_DATA = {"key": "value", "blocks": [1, 2, 3]}
    print(render_debug_modal(json.dumps(SAMPLE_DATA)))
    print("\n--- Floating Add Button (Simplified Example Usage) ---")
    print(render_floating_add_button())
