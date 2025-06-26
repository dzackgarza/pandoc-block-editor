"""
Custom UI elements for the Pandoc Block Editor,
rendered using st.components.v1.html.
"""

import json  # For passing data to JS


def render_debug_console(debug_data_json_string="{}", initial_visible=False):
    """
    Renders a debug console that slides up from the bottom of the screen.

    Args:
        debug_data_json_string (str): A JSON string representing the data to display.
        initial_visible (bool): Whether the console should be visible initially.
    """
    console_id = "debug-console"
    content_id = "debug-console-content"
    # Determine initial bottom position based on initial_visible
    initial_bottom = "0" if initial_visible else "-300px"

    html_content = f"""
<style>
    #{console_id} {{
        position: fixed;
        bottom: {initial_bottom};
        left: 0;
        right: 0;
        height: 300px;
        background-color: #1e1e1e;
        color: #ffffff;
        border-top: 2px solid #333;
        z-index: 1500;
        transition: bottom 0.3s ease-in-out;
        display: flex;
        flex-direction: column;
        box-shadow: 0 -5px 15px rgba(0,0,0,0.3);
    }}
    .debug-console-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 15px;
        background-color: #2d2d2d;
        border-bottom: 1px solid #444;
        min-height: 20px;
    }}
    .debug-console-title {{
        margin: 0;
        font-size: 14px;
        font-weight: bold;
        color: #fff;
    }}
    .debug-console-close-btn {{
        color: #aaa;
        font-size: 18px;
        font-weight: bold;
        cursor: pointer;
        background: none;
        border: none;
        padding: 0;
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    .debug-console-close-btn:hover {{
        color: #fff;
    }}
    #{content_id} {{
        flex-grow: 1;
        overflow-y: auto;
        background-color: #1e1e1e;
        padding: 15px;
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        white-space: pre;
        font-size: 12px;
        line-height: 1.4;
    }}
</style>

<div id="{console_id}">
    <div class="debug-console-header">
        <h3 class="debug-console-title">🐛 Debug Console</h3>
        <button class="debug-console-close-btn" title="Close Debug Console">&times;</button>
    </div>
    <pre id="{content_id}">{json.dumps(json.loads(debug_data_json_string), indent=2, ensure_ascii=False)}</pre>
</div>

<script>
(function() {{
    const console = document.getElementById('{console_id}');
    const closeButton = console.querySelector('.debug-console-close-btn');

    function closeConsole() {{
        if (console) console.style.bottom = '-300px';
    }}

    function openConsole() {{
        if (console) console.style.bottom = '0';
    }}

    if (closeButton) {{
        closeButton.addEventListener('click', closeConsole);
    }}

    // Optional: Close with Escape key
    document.addEventListener('keydown', function(event) {{
        if (event.key === "Escape" && console.style.bottom === '0px') {{
            closeConsole();
        }}
    }});

    // Set initial state
    if ({str(initial_visible).lower()}) {{
        openConsole();
    }} else {{
        closeConsole();
    }}
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
