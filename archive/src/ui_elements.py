"""
Custom UI elements for the Pandoc Block Editor,
rendered using st.components.v1.html.
"""

import json  # For passing data to JS


def render_debug_console(initial_visible=False):
    """
    Renders a Chrome-like debug console for live logging and errors.

    Args:
        initial_visible (bool): Whether the console should be visible initially.
    """
    console_id = "debug-console"
    content_id = "debug-console-content"
    input_id = "debug-console-input"
    # Determine initial bottom position based on initial_visible
    initial_bottom = "0" if initial_visible else "-350px"

    html_content = f"""
<style>
    #{console_id} {{
        position: fixed;
        bottom: {initial_bottom};
        left: 0;
        right: 0;
        height: 350px;
        background-color: #1e1e1e;
        color: #ffffff;
        border-top: 2px solid #333;
        z-index: 1500;
        transition: bottom 0.3s ease-in-out;
        display: flex;
        flex-direction: column;
        box-shadow: 0 -5px 15px rgba(0,0,0,0.3);
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    }}
    .debug-console-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 12px;
        background-color: #2d2d2d;
        border-bottom: 1px solid #444;
        min-height: 32px;
    }}
    .debug-console-title {{
        margin: 0;
        font-size: 13px;
        font-weight: bold;
        color: #fff;
    }}
    .debug-console-controls {{
        display: flex;
        gap: 8px;
        align-items: center;
    }}
    .debug-console-clear-btn {{
        color: #aaa;
        font-size: 12px;
        cursor: pointer;
        background: none;
        border: 1px solid #555;
        padding: 4px 8px;
        border-radius: 3px;
        transition: all 0.2s;
    }}
    .debug-console-clear-btn:hover {{
        color: #fff;
        border-color: #777;
    }}
    .debug-console-close-btn {{
        color: #aaa;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        background: none;
        border: none;
        padding: 4px;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 3px;
    }}
    .debug-console-close-btn:hover {{
        color: #fff;
        background-color: #444;
    }}
    #{content_id} {{
        flex-grow: 1;
        overflow-y: auto;
        background-color: #1e1e1e;
        padding: 8px 12px;
        font-size: 12px;
        line-height: 1.4;
    }}
    .log-entry {{
        margin: 2px 0;
        padding: 2px 0;
        border-bottom: 1px solid #333;
    }}
    .log-entry:last-child {{
        border-bottom: none;
    }}
    .log-timestamp {{
        color: #666;
        font-size: 11px;
        margin-right: 8px;
    }}
    .log-level-info {{
        color: #4fc3f7;
    }}
    .log-level-warn {{
        color: #ffb74d;
    }}
    .log-level-error {{
        color: #f44336;
    }}
    .log-level-debug {{
        color: #81c784;
    }}
    .debug-console-input-area {{
        border-top: 1px solid #444;
        padding: 8px 12px;
        background-color: #2d2d2d;
        display: flex;
        align-items: center;
    }}
    #{input_id} {{
        flex-grow: 1;
        background: #1e1e1e;
        border: 1px solid #555;
        color: #fff;
        padding: 6px 8px;
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        font-size: 12px;
        border-radius: 3px;
        outline: none;
    }}
    #{input_id}:focus {{
        border-color: #4fc3f7;
    }}
    .prompt {{
        color: #4fc3f7;
        margin-right: 8px;
        font-weight: bold;
    }}
</style>

<div id="{console_id}">
    <div class="debug-console-header">
        <h3 class="debug-console-title">🔍 Console</h3>
        <div class="debug-console-controls">
            <button class="debug-console-clear-btn" title="Clear Console">Clear</button>
            <button class="debug-console-close-btn" title="Close Console">&times;</button>
        </div>
    </div>
    <div id="{content_id}">
        <div class="log-entry">
            <span class="log-timestamp"></span>
            <span class="log-level-info">Console ready. Type JavaScript commands below or view live logs here.</span>
        </div>
    </div>
    <div class="debug-console-input-area">
        <span class="prompt">&gt;</span>
        <input type="text" id="{input_id}" placeholder="Enter JavaScript command..." />
    </div>
</div>

<script>
(function() {{
    const consoleEl = document.getElementById('{console_id}');
    const contentEl = document.getElementById('{content_id}');
    const inputEl = document.getElementById('{input_id}');
    const closeButton = consoleEl.querySelector('.debug-console-close-btn');
    const clearButton = consoleEl.querySelector('.debug-console-clear-btn');

    // Store original console methods
    const originalConsole = {{
        log: console.log,
        error: console.error,
        warn: console.warn,
        info: console.info,
        debug: console.debug
    }};

    function formatTimestamp() {{
        const now = new Date();
        return now.toLocaleTimeString() + '.' + now.getMilliseconds().toString().padStart(3, '0');
    }}

    function addLogEntry(level, args) {{
        const entry = document.createElement('div');
        entry.className = 'log-entry';
        
        const timestamp = document.createElement('span');
        timestamp.className = 'log-timestamp';
        timestamp.textContent = formatTimestamp();
        
        const content = document.createElement('span');
        content.className = `log-level-${{level}}`;
        
        // Convert arguments to strings
        const message = Array.from(args).map(arg => {{
            if (typeof arg === 'object') {{
                try {{
                    return JSON.stringify(arg, null, 2);
                }} catch(e) {{
                    return String(arg);
                }}
            }}
            return String(arg);
        }}).join(' ');
        
        content.textContent = message;
        
        entry.appendChild(timestamp);
        entry.appendChild(content);
        contentEl.appendChild(entry);
        
        // Auto-scroll to bottom
        contentEl.scrollTop = contentEl.scrollHeight;
    }}

    // Override console methods to capture logs
    console.log = function(...args) {{
        originalConsole.log.apply(console, args);
        addLogEntry('info', args);
    }};

    console.error = function(...args) {{
        originalConsole.error.apply(console, args);
        addLogEntry('error', args);
    }};

    console.warn = function(...args) {{
        originalConsole.warn.apply(console, args);
        addLogEntry('warn', args);
    }};

    console.info = function(...args) {{
        originalConsole.info.apply(console, args);
        addLogEntry('info', args);
    }};

    console.debug = function(...args) {{
        originalConsole.debug.apply(console, args);
        addLogEntry('debug', args);
    }};

    // Capture uncaught errors
    window.addEventListener('error', function(event) {{
        addLogEntry('error', [`Uncaught ${{event.error?.name || 'Error'}}: ${{event.message}}`]);
    }});

    // Console controls
    function closeConsole() {{
        if (consoleEl) consoleEl.style.bottom = '-350px';
    }}

    function openConsole() {{
        if (consoleEl) consoleEl.style.bottom = '0';
    }}

    function clearConsole() {{
        contentEl.innerHTML = '<div class="log-entry"><span class="log-timestamp"></span><span class="log-level-info">Console cleared.</span></div>';
    }}

    if (closeButton) {{
        closeButton.addEventListener('click', closeConsole);
    }}

    if (clearButton) {{
        clearButton.addEventListener('click', clearConsole);
    }}

    // Input handling
    if (inputEl) {{
        inputEl.addEventListener('keydown', function(event) {{
            if (event.key === 'Enter') {{
                const command = inputEl.value.trim();
                if (command) {{
                    // Echo the command
                    addLogEntry('debug', [`> ${{command}}`]);
                    
                    try {{
                        // Execute the command
                        const result = eval(command);
                        if (result !== undefined) {{
                            addLogEntry('info', [result]);
                        }}
                    }} catch (error) {{
                        addLogEntry('error', [error.toString()]);
                    }}
                    
                    inputEl.value = '';
                }}
            }}
        }});
    }}

    // Close with Escape key
    document.addEventListener('keydown', function(event) {{
        if (event.key === "Escape" && consoleEl.style.bottom === '0px') {{
            closeConsole();
        }}
    }});

    // Set initial state
    if ({str(initial_visible).lower()}) {{
        openConsole();
    }} else {{
        closeConsole();
    }}

    // Add initial log entry
    setTimeout(() => {{
        console.log('Debug console initialized - Pandoc Block Editor');
    }}, 100);
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
