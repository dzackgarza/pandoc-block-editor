# pylint: disable=import-error (playwright, pytest are dev dependencies)
# pylint: disable=redefined-outer-name (pytest fixtures)
import re
from playwright.sync_api import Page, expect
import pytest

# Base URL for the Streamlit app
BASE_URL = "http://localhost:8501"

# Common locators
TITLE_LOCATOR = "h1[data-testid='stHeading']"  # Main title of the app
SIDEBAR_MENU_TITLE_LOCATOR = "div[data-testid='stSidebar'] h1"  # Title inside sidebar
ADD_BLOCK_BUTTON_LOCATOR = "div[data-testid='stSidebar'] button:has-text('Add Block')"
SAVE_DOCUMENT_BUTTON_LOCATOR = (
    "div[data-testid='stSidebar'] button:has-text('Save Document')"
)
OPEN_DOCUMENT_INPUT_LOCATOR = (
    "div[data-testid='stSidebar'] input[type='file']"  # More specific
)

# Locators for editor and preview panes (assuming they are direct children of columns)
# These might need to be more specific if the structure is complex.
# For now, let's assume each block has a text_area and a preview div.
EDITOR_PANE_LOCATOR = "div[data-testid='stVerticalBlock']:nth-child(1) > div[data-testid='stHorizontalBlock'] > div[data-testid='stVerticalBlock']:nth-child(1) > div[data-testid='stElementToolbar'] ~ div[data-testid='stBlock']"
PREVIEW_PANE_LOCATOR = "div[data-testid='stVerticalBlock']:nth-child(1) > div[data-testid='stHorizontalBlock'] > div[data-testid='stVerticalBlock']:nth-child(2) > div[data-testid='stElementToolbar'] ~ div[data-testid='stBlock']"

# Specific content from torture_test_document.md
TORTURE_TEST_HEADING_TEXT = "Heading 1"  # The text content of the first H1
TORTURE_TEST_H1_ID = "h1-id"
TORTURE_TEST_PARAGRAPH_TEXT_SUBSTRING = "This is a paragraph under H1"
TORTURE_TEST_PYTHON_CODE_SUBSTRING = "def greet(name):"
TORTURE_TEST_MATH_INLINE_LATEX = "$E = mc^2$"  # Raw LaTeX
TORTURE_TEST_MATH_DISPLAY_LATEX = (
    "\\int_{-\infty}^{\infty} e^{-x^2} dx = \\sqrt{\\pi}"  # Raw LaTeX
)

# Expected rendered HTML for some elements
EXPECTED_H1_HTML_TAG = f"h1"  # Check for tag, ID might be tricky if not directly on h1
EXPECTED_PREVIEW_H1_ID_WRAPPER_SELECTOR = (
    f"div.block-preview-wrapper h1#{TORTURE_TEST_H1_ID}"  # If ID is on H1
)
EXPECTED_PARAGRAPH_HTML_TAG = "p"
EXPECTED_CODE_BLOCK_PYTHON_CLASS = "code.language-python"  # Pandoc adds this class
EXPECTED_MATHJAX_INLINE_CLASS = (
    "span.MathJax_Preview"  # MathJax structure (can vary) or check for \(...\)
)


@pytest.fixture(scope="session", autouse=True)
def ensure_streamlit_app_is_running_disclaimer():
    """
    This is a placeholder fixture to remind that Streamlit app needs to be running.
    In a CI environment, you'd have a step to start the app.
    `pytest --headed` or `PWDEBUG=1 pytest` can be useful for debugging locally.
    """
    # For local testing: print("Reminder: Ensure Streamlit app is running on " + BASE_URL)
    pass


def test_app_loads_and_has_correct_title(page: Page):
    page.goto(BASE_URL)
    expect(page).to_have_title(re.compile("Pandoc Block Editor"))
    # Check for the main title element rendered by Streamlit
    app_title = page.locator(TITLE_LOCATOR).first  # Main page title, not sidebar
    expect(app_title).to_be_visible()
    expect(app_title).to_have_text("Pandoc Block Editor")


def test_sidebar_menu_items_are_present(page: Page):
    page.goto(BASE_URL)
    # Check for sidebar title
    # sidebar_title = page.locator(SIDEBAR_MENU_TITLE_LOCATOR)
    # expect(sidebar_title).to_have_text("Menu") #This is an h1, might clash with main title

    # Check for "File" submenu items (buttons/labels)
    # The file uploader is a label styled as a button
    open_button_label = page.locator(
        f"{OPEN_DOCUMENT_INPUT_LOCATOR} ~ label:has-text('Open Document')"
    ).first
    expect(open_button_label).to_be_visible()

    save_button = page.locator(SAVE_DOCUMENT_BUTTON_LOCATOR).first
    expect(save_button).to_be_visible()

    # Check for "Edit" submenu items
    add_block_button = page.locator(ADD_BLOCK_BUTTON_LOCATOR).first
    expect(add_block_button).to_be_visible()

    # Check for "View" submenu items
    debug_toggle = page.locator(
        "div[data-testid='stSidebar'] label:has-text('Show Debug Info')"
    ).first
    expect(debug_toggle).to_be_visible()


def test_loads_torture_test_document_by_default(page: Page):
    page.goto(BASE_URL)

    # Check for presence of specific content from torture_test_document.md in editor panes
    # This requires locating the text_area elements. Streamlit creates unique keys for them.
    # We'll look for the *first* text_area and assume it's the first block.
    # A more robust way is to look for text_area containing specific text.

    # Check for first heading in an editor text_area
    # The content of the heading block is just "First Heading", not "# First Heading..."
    # because app.py's parse_full_markdown_to_editor_blocks extracts the text content for headings.
    # Let's find a textarea that contains "First Heading".
    editor_for_h1 = page.locator(
        f"textarea:has-text('{TORTURE_TEST_HEADING_TEXT}')"
    ).first
    expect(editor_for_h1).to_be_visible()
    # Check its value more precisely if needed, e.g. expect(editor_for_h1).to_have_value(TORTURE_TEST_HEADING_TEXT)
    # This depends on how pandoc_utils.convert_ast_json_to_markdown formats the header's content part.
    # For now, `has-text` is a good start.

    # Check for a paragraph from the torture test in another textarea
    editor_for_para = page.locator(
        f"textarea:has-text('{TORTURE_TEST_PARAGRAPH_TEXT_SUBSTRING}')"
    ).first
    expect(editor_for_para).to_be_visible()

    # Check for python code block content in an editor textarea
    editor_for_code = page.locator(
        f"textarea:has-text('{TORTURE_TEST_PYTHON_CODE_SUBSTRING}')"
    ).first
    expect(editor_for_code).to_be_visible()


def test_renders_torture_test_document_in_preview(page: Page):
    page.goto(BASE_URL)

    # Check for rendered HTML elements in the preview pane.
    # This relies on how Streamlit structures its output for st.markdown.
    # Each block preview is wrapped in <div id='preview-block-...' class='block-preview-wrapper'>

    # Check for rendered H1
    # The ID 'h1-id' from ' # Heading 1 {#h1-id}' should be on the h1 tag itself.
    # Pandoc usually puts the ID on the heading tag.
    # preview_h1 = page.locator(f"div.block-preview-wrapper {EXPECTED_H1_HTML_TAG}#h1-id:has-text('{TORTURE_TEST_HEADING_TEXT}')").first
    # A slightly more general selector if ID placement varies:
    preview_h1_wrapper = page.locator(
        f"div.block-preview-wrapper:has(h1:has-text('{TORTURE_TEST_HEADING_TEXT}'))"
    ).first
    expect(preview_h1_wrapper.locator("h1")).to_be_visible()
    # Check if the H1 has the ID (this is more precise)
    h1_with_id = preview_h1_wrapper.locator(f"h1#{TORTURE_TEST_H1_ID}")
    expect(h1_with_id).to_be_visible()

    # Check for rendered paragraph
    preview_para = page.locator(
        f"div.block-preview-wrapper {EXPECTED_PARAGRAPH_HTML_TAG}:has-text('{TORTURE_TEST_PARAGRAPH_TEXT_SUBSTRING}')"
    ).first
    expect(preview_para).to_be_visible()

    # Check for rendered Python code block (Pandoc uses <pre><code class="language-python">...</code></pre>)
    # We look for the specific class added by Pandoc's highlighting.
    preview_code_block = page.locator(
        f"div.block-preview-wrapper pre.{EXPECTED_CODE_BLOCK_PYTHON_CLASS.split('.')[1]}"
    ).first  # pre.sourceCode.python
    expect(preview_code_block).to_be_visible()
    expect(preview_code_block).to_contain_text(TORTURE_TEST_PYTHON_CODE_SUBSTRING)

    # Check for rendered MathJax (this is tricky as MathJax replaces content)
    # We can look for the original LaTeX string within a preview wrapper,
    # and then look for MathJax's generated spans (if MathJax has processed it).
    # This test might be flaky if MathJax takes too long or fails.
    # Wait for MathJax to process, MathJax sets classes like .MJX_Assistive_MathML
    # For now, check if the raw LaTeX is at least present in the HTML before MathJax processing.
    # The `convert_markdown_to_html` uses `--mathjax` which means Pandoc will wrap math in \(...\) or \[...\]

    # Locate the preview block that should contain the inline math
    # The original torture test has "$E = mc^2$"
    # Pandoc with --mathjax will turn this into "\\(E = mc^2\\)" in the HTML source for MathJax to process.
    inline_math_wrapper = page.locator(
        f"div.block-preview-wrapper:has-text('{EXPECTED_MATHJAX_INLINE_CLASS}')"
    ).first  # This is too generic

    # More specific: find the wrapper that contains the math source
    # Look for the div that contains the text "$E = mc^2$"
    # The text from the torture doc is "Inline math: $E = mc^2$."
    # The block content passed to convert_markdown_to_html will be "Inline math: $E = mc^2$."
    # Pandoc will output something like <p>Inline math: <span class="math inline">\((E = mc^2)\)</span>.</p>
    inline_math_span = page.locator(
        "div.block-preview-wrapper span.math.inline:has-text('E = mc^2')"
    ).first
    expect(inline_math_span).to_be_visible(
        timeout=10000
    )  # Increased timeout for MathJax

    # For display math: \[ \int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi} \]
    # Pandoc will output <p><span class="math display">\[\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}\]</span></p>
    display_math_span = page.locator(
        "div.block-preview-wrapper span.math.display:has-text('e^{-x^2} dx = \\sqrt{\\pi}')"
    ).first
    expect(display_math_span).to_be_visible(timeout=10000)


def test_add_block_button_adds_a_new_block(page: Page):
    page.goto(BASE_URL)

    # Count initial number of editor text_areas
    initial_editor_count = page.locator("div[data-testid='stTextArea']").count()

    # Click "Add Block"
    add_block_button = page.locator(ADD_BLOCK_BUTTON_LOCATOR).first
    add_block_button.click()

    # Wait for rerun and check if a new editor text_area appears
    # It's important to wait for Streamlit's rerun to complete.
    # A simple way is to check for an increased count of a known element.
    expect(page.locator("div[data-testid='stTextArea']")).to_have_count(
        initial_editor_count + 1, timeout=5000
    )

    # Check if the new block is empty or has default content
    # The new block should be the last one.
    new_editor_area = page.locator("div[data-testid='stTextArea']").nth(-1)  # Last one
    # Default content is empty string ""
    expect(new_editor_area.locator("textarea")).to_have_value("")

    # Also check for a corresponding new preview area (it might be empty or show placeholder)
    initial_preview_count = page.locator(
        "div.block-preview-wrapper"
    ).count()  # Count existing previews
    # After adding a block, there should be one more preview wrapper
    # This assertion might be tricky if empty blocks don't render a distinct preview wrapper immediately
    # or if the structure is complex. Let's assume an empty block still creates a preview div.
    # The click above already triggered a rerun.
    expect(page.locator("div.block-preview-wrapper")).to_have_count(
        initial_preview_count + 1, timeout=5000
    )

    # The new preview area should be empty or reflect an empty markdown string
    new_preview_area = page.locator("div.block-preview-wrapper").nth(-1)
    # An empty markdown string "" renders to nothing or an empty <p></p> by Pandoc.
    # If it's nothing, the innerHTML might be empty. If <p></p>, it won't be empty.
    # Let's check that it doesn't contain substantial text.
    expect(new_preview_area).to_be_visible()  # Ensure it's there
    # If pandoc_utils.convert_markdown_to_html("") returns "", then innerHTML should be empty.
    # If it returns "<p></p>\n", then it won't be empty.
    # Current pandoc_utils.convert_markdown_to_html("") returns ""
    expect(new_preview_area.inner_html()).to_match(
        re.compile(r"^\s*(<p>\s*</p>)?\s*$", re.IGNORECASE)
    )


# Placeholder for more tests:
# - Editing content in a block and seeing preview update.
# - File open (more complex due to Playwright's handling of file choosers with Streamlit's uploader).
# - File save (even more complex, as it's a download; might need to check downloaded content).
# - Debug modal toggle.
# - Cross-references rendering (e.g. \cref{...}).
# - Malformed block rendering (shows error in preview, rest of app OK).
# - Test for scroll-sync (if implemented, very complex for E2E).
# - Test for top-alignment (visual, might need screenshot diffing).

# Example of how to test editing a block:
# def test_edit_block_updates_preview(page: Page):
#     page.goto(BASE_URL)
#     editor_for_h1 = page.locator(f"textarea:has-text('{TORTURE_TEST_HEADING_TEXT}')").first
#     expect(editor_for_h1).to_be_visible()
#
#     # Corresponding preview for H1
#     preview_h1_wrapper = page.locator(f"div.block-preview-wrapper:has(h1:has-text('{TORTURE_TEST_HEADING_TEXT}'))").first
#     expect(preview_h1_wrapper.locator("h1")).to_be_visible()
#
#     new_heading_text = "Super New Heading"
#     editor_for_h1.fill(new_heading_text) # This triggers on_change
#
#     # Wait for Streamlit to process and re-render the preview
#     # The preview should now show the new heading text
#     updated_preview_h1 = preview_h1_wrapper.locator(f"h1:has-text('{new_heading_text}')")
#     expect(updated_preview_h1).to_be_visible(timeout=5000)
#
#     # Ensure the old heading text is gone from this specific preview block
#     expect(preview_h1_wrapper.locator(f"h1:has-text('{TORTURE_TEST_HEADING_TEXT}')")).not_to_be_visible()
#
#     # Ensure other blocks are unaffected (e.g., a paragraph text should still be there)
#     preview_para = page.locator(f"div.block-preview-wrapper {EXPECTED_PARAGRAPH_HTML_TAG}:has-text('{TORTURE_TEST_PARAGRAPH_TEXT_SUBSTRING}')").first
#     expect(preview_para).to_be_visible()
#
#     # Important: Streamlit's on_change for text_area might have a default debounce or require focus loss.
#     # Playwright's fill() usually handles this, but if issues occur, try editor_for_h1.press("Tab") or similar
#     # to ensure the change event is fully processed.
#
#     # Also, the ID of the block might change if not careful with state updates.
#     # The `handle_block_content_change` in app.py updates by `block_id`.
#     # The `editor_key` includes the index `i`, so if blocks are added/removed above,
#     # this test might become flaky if it targets by index instead of stable ID/content.
#     # Using `has-text` locators is generally more robust.
#
#     # If the block ID `h1-id` is preserved in the EditorBlock state and used to find the preview,
#     # we could use that for a more stable locator.
#     # preview_div_id = f"preview-block-{block_id_of_h1}-{index_of_h1}"
#     # updated_preview_h1_by_id = page.locator(f"#{preview_div_id} h1:has-text('{new_heading_text}')")
#     # expect(updated_preview_h1_by_id).to_be_visible(timeout=5000)

# To run tests:
# 1. Ensure Streamlit app is running: `python -m streamlit run src/app.py`
# 2. In another terminal: `pytest` (or `pytest tests/e2e/test_main_app.py`)
# Install Playwright browsers if not already: `playwright install`
# For headed mode (to see browser): `pytest --headed tests/e2e/test_main_app.py`
# For debugging Playwright scripts: `PWDEBUG=1 pytest tests/e2e/test_main_app.py`
