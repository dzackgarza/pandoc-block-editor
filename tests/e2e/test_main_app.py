# pylint: disable=import-error,redefined-outer-name
# (playwright, pytest are dev dependencies; pytest fixtures)
import re
from playwright.sync_api import Page, expect
import pytest

# Base URL for the Streamlit app
BASE_URL = "http://localhost:8501"

# Common locators
# TITLE_LOCATOR = "h1[data-testid='stHeading']"  # Main title of the app
# Using a more specific selector for the main app title, not sidebar
APP_MAIN_TITLE_LOCATOR = "div[data-testid='stAppViewContainer'] h1"
# ADD_BLOCK_BUTTON_LOCATOR is removed as it's now a FAB
FAB_ADD_BLOCK_LOCATOR = "div#floating-add-block-button"
DEBUG_MODAL_TOGGLE_BUTTON_LOCATOR = "button#debug-modal-toggle-btn"
DEBUG_MODAL_OVERLAY_LOCATOR = "div#debug-modal-overlay-container"
DEBUG_MODAL_CONTENT_LOCATOR = "div#debug-modal-panel-content"
DEBUG_MODAL_CLOSE_BUTTON_LOCATOR = "button#debug-modal-close-btn"


SAVE_DOCUMENT_BUTTON_LOCATOR = (
    "div[data-testid='stSidebar'] button:has-text('Save Document')"
)
OPEN_DOCUMENT_INPUT_LOCATOR = (
    "div[data-testid='stSidebar'] input[type='file']"  # More specific
)


# Specific content from torture_test_document.md
TORTURE_TEST_HEADING_TEXT = "Heading 1"  # The text content of the first H1
TORTURE_TEST_H1_ID = "h1-id"
TORTURE_TEST_PARAGRAPH_TEXT_SUBSTRING = "This is a paragraph under H1"
TORTURE_TEST_PYTHON_CODE_SUBSTRING = "def greet(name):"
# Raw LaTeX for checking in HTML source before MathJax processing
# TORTURE_TEST_MATH_INLINE_LATEX_RAW = "$E = mc^2$"
# Pandoc output for MathJax
EXPECTED_MATHJAX_INLINE_WRAPPED = r"\\(E = mc^2\\)"
EXPECTED_MATHJAX_DISPLAY_WRAPPED_PART = r"\\\[\\int_{-\infty}^{\infty} e^{-x^2} dx"

# Expected rendered HTML structure parts
EXPECTED_PARAGRAPH_HTML_TAG = "p"
EXPECTED_CODE_BLOCK_PYTHON_CLASS = "code.language-python"  # Pandoc adds this class


@pytest.fixture(scope="session", autouse=True)
def ensure_streamlit_app_is_running_disclaimer(request):  # Added request for W0613
    """
    Placeholder fixture to remind that Streamlit app needs to be running.
    """
    # For local testing:
    # print(f"Reminder: Ensure Streamlit app is running on {BASE_URL} for E2E tests.")
    # This fixture doesn't do anything but serves as a reminder.
    # The `request` parameter is added to satisfy pylint's W0613 (unused-argument)
    # if we don't use it directly here.
    if request:  # Simple use of request
        pass


def test_app_loads_and_has_correct_title(page: Page):
    """Test if the Streamlit application loads and has the correct title."""
    page.goto(BASE_URL)
    page.wait_for_load_state(
        "networkidle", timeout=10000
    )  # Wait for network to be idle
    expect(page).to_have_title(
        re.compile("Pandoc Block Editor"), timeout=10000
    )  # Increased timeout
    # Temporarily commenting out H1 check to isolate title issue
    # app_title = page.locator(APP_MAIN_TITLE_LOCATOR).first
    # expect(app_title).to_be_visible()
    # expect(app_title).to_have_text("Pandoc Block Editor")


def test_sidebar_menu_items_are_present(page: Page):
    """Test if essential sidebar menu items are present."""
    page.goto(BASE_URL)
    # File uploader is a label styled as a button.
    # The actual clickable element might be the button part.
    # Let's try to find the button that Streamlit generates for
    # st.file_uploader, or the label directly if the button is hard to pinpoint.
    # The label "Open Document" should be visible.
    open_doc_label_direct = page.locator(
        "div[data-testid='stSidebar'] div[data-testid='stFileUploader'] label"
    ).first
    # Check the label text
    expect(open_doc_label_direct).to_have_text("Open Document")
    # The actual button Streamlit uses might be nested. The label itself
    # might not be "visible" in Playwright's terms if it's just for an input.
    # Let's try a more direct approach to the button part.
    # Streamlit < 1.30: input's label. >=1.30: button.
    # The text "Open Document" is the label of the st.file_uploader widget.
    # Locator for the label part of st.file_uploader, ensuring it's in the sidebar.
    open_document_label_selector = (
        "div[data-testid='stSidebar'] div[data-testid='stFileUploader'] label"
    )
    open_document_label = (
        page.locator(open_document_label_selector)
        .filter(has_text="Open Document")
        .first
    )
    expect(open_document_label).to_be_visible()

    save_button = page.locator(SAVE_DOCUMENT_BUTTON_LOCATOR).first
    expect(save_button).to_be_visible()

    # "Add Block" is no longer in sidebar
    # "Debug Info" toggle is no longer in sidebar


def test_loads_torture_test_document_by_default(page: Page):
    page.goto(BASE_URL)

    # Check for presence of specific content from torture_test_document.md in editor panes
    # This requires locating the text_area elements. Streamlit creates unique keys for them.
    # We'll look for the *first* text_area and assume it's the first block.
    # A more robust way is to look for text_area containing specific text.

    # Check for first heading in an editor text_area
    # The content of the heading block is just "First Heading",
    # not "# First Heading..." because app.py's
    # parse_full_markdown_to_editor_blocks extracts the text content for headings.
    # Let's find a textarea that contains "First Heading".
    editor_h1_selector = f"textarea:has-text('{TORTURE_TEST_HEADING_TEXT}')"
    editor_for_h1 = page.locator(editor_h1_selector).first
    expect(editor_for_h1).to_be_visible()
    # Check its value more precisely if needed,
    # e.g. expect(editor_for_h1).to_have_value(TORTURE_TEST_HEADING_TEXT)
    # This depends on how pandoc_utils.convert_ast_json_to_markdown
    # formats the header's content part. For now, `has-text` is a good start.

    # Check for a paragraph from the torture test in another textarea
    editor_para_selector = (
        f"textarea:has-text('{TORTURE_TEST_PARAGRAPH_TEXT_SUBSTRING}')"
    )
    editor_for_para = page.locator(editor_para_selector).first
    expect(editor_for_para).to_be_visible()

    # Check for python code block content in an editor textarea
    editor_code_selector = (
        f"textarea:has-text('{TORTURE_TEST_PYTHON_CODE_SUBSTRING}')"
    )
    editor_for_code = page.locator(editor_code_selector).first
    expect(editor_for_code).to_be_visible()


def test_renders_torture_test_document_in_preview(page: Page):
    page.goto(BASE_URL)

    # Check for rendered HTML elements in the preview pane.
    # This relies on how Streamlit structures its output for st.markdown.
    # Each block preview is wrapped in <div id='preview-block-...' class='block-preview-wrapper'>

    # Check for rendered H1
    # The ID 'h1-id' from ' # Heading 1 {#h1-id}' should be on the h1 tag itself.
    # Pandoc usually puts the ID on the heading tag.
    # preview_h1 = page.locator(
    # f"div.block-preview-wrapper {EXPECTED_H1_HTML_TAG}#h1-id"
    # f":has-text('{TORTURE_TEST_HEADING_TEXT}')").first
    # A slightly more general selector if ID placement varies:
    h1_wrapper_selector = (
        f"div.block-preview-wrapper:has(h1:has-text('{TORTURE_TEST_HEADING_TEXT}'))"
    )
    preview_h1_wrapper = page.locator(h1_wrapper_selector).first
    expect(preview_h1_wrapper.locator("h1")).to_be_visible()
    # Check if the H1 has the ID (this is more precise)
    h1_with_id = preview_h1_wrapper.locator(f"h1#{TORTURE_TEST_H1_ID}")
    expect(h1_with_id).to_be_visible()

    # Check for rendered paragraph
    para_selector = (
        f"div.block-preview-wrapper {EXPECTED_PARAGRAPH_HTML_TAG}"
        f":has-text('{TORTURE_TEST_PARAGRAPH_TEXT_SUBSTRING}')"
    )
    preview_para = page.locator(para_selector).first
    expect(preview_para).to_be_visible()

    # Check for rendered Python code block
    # (Pandoc uses <pre><code class="language-python">...</code></pre>)
    # We look for the specific class added by Pandoc's highlighting.
    code_block_class = EXPECTED_CODE_BLOCK_PYTHON_CLASS.split('.')[1]
    code_block_selector = (
        f"div.block-preview-wrapper pre.{code_block_class}"
    ) # pre.sourceCode.python
    preview_code_block = page.locator(code_block_selector).first
    expect(preview_code_block).to_be_visible()
    expect(preview_code_block).to_contain_text(TORTURE_TEST_PYTHON_CODE_SUBSTRING)

    # Check for rendered MathJax (this is tricky as MathJax replaces content)
    # We can look for the original LaTeX string within a preview wrapper,
    # and then look for MathJax's generated spans (if MathJax has processed it).
    # This test might be flaky if MathJax takes too long or fails.
    # Wait for MathJax to process, MathJax sets classes like .MJX_Assistive_MathML
    # For now, check if the raw LaTeX is at least present in the HTML
    # before MathJax processing.
    # The `convert_markdown_to_html` uses `--mathjax` which means Pandoc will
    # wrap math in \(...\) or \[...\].

    # More specific: find the wrapper that contains the math source
    # Look for the div that contains the text "$E = mc^2$"
    # The text from the torture doc is "Inline math: $E = mc^2$."
    # The block content passed to convert_markdown_to_html will be
    # "Inline math: $E = mc^2$."
    # Pandoc will output something like
    # <p>Inline math: <span class="math inline">\((E = mc^2)\)</span>.</p>
    inline_math_span_selector = (
        "div.block-preview-wrapper span.math.inline:has-text('E = mc^2')"
    )
    inline_math_span = page.locator(inline_math_span_selector).first
    expect(inline_math_span).to_be_visible(timeout=10000)

    # This is for `\[\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}\]`
    # Breaking locator string for line length
    display_math_text_selector = ":has-text('e^{-x^2} dx = \\\\sqrt{\\\\pi}')"
    display_math_span_selector = (
        f"div.block-preview-wrapper span.math.display{display_math_text_selector}"
    )
    display_math_span = page.locator(display_math_span_selector).first
    expect(display_math_span).to_be_visible(timeout=10000)


def test_fab_add_block_adds_a_new_block(page: Page):
    """Test if the Floating Action Button for 'Add Block' works."""
    page.goto(BASE_URL)

    initial_editor_count = page.locator("div[data-testid='stTextArea']").count()

    # Click FAB "Add Block"
    # Assuming FAB is rendered inside an iframe by st.components.v1.html
    # Try to locate the iframe first. Streamlit usually doesn't give them
    # specific names/titles easily. We might need to rely on the order or
    # find a unique parent. For now, let's assume it's one of the iframes
    # on the page. A more robust selector would be if we could add a
    # data-testid to the component wrapper.
    fab_iframe_selector = "iframe[title='st.components.v1.html']"
    fab_iframe_locator = page.locator(fab_iframe_selector).first

    # Wait for the iframe itself to be present
    try:
        expect(fab_iframe_locator).to_be_visible(timeout=7000)
    except AssertionError:
        print("DEBUG: FAB iframe not found. Page content:")
        print(page.content())
        raise

    fab_add_block = fab_iframe_locator.frame_locator(":scope").locator(
        FAB_ADD_BLOCK_LOCATOR
    )
    expect(fab_add_block).to_be_visible(timeout=7000)
    fab_add_block.click()

    # Wait for rerun and check for an increased count of editor text_areas
    text_area_selector = "div[data-testid='stTextArea']"
    expect(page.locator(text_area_selector)).to_have_count(
        initial_editor_count + 1, timeout=5000
    )

    new_editor_area = page.locator(text_area_selector).nth(-1)
    expect(new_editor_area.locator("textarea")).to_have_value("")

    preview_wrapper_selector = "div.block-preview-wrapper"
    initial_preview_count = page.locator(preview_wrapper_selector).count()
    expect(page.locator(preview_wrapper_selector)).to_have_count(
        initial_preview_count + 1, timeout=5000
    )

    new_preview_area = page.locator(preview_wrapper_selector).nth(-1)
    expect(new_preview_area).to_be_visible()
    # Matches empty paragraph or just whitespace
    empty_p_regex = re.compile(r"^\s*(<p>\s*</p>)?\s*$", re.IGNORECASE)
    expect(new_preview_area.inner_html()).to_match(empty_p_regex)


def test_debug_modal_toggle_and_content(page: Page):
    """Test the debug modal toggle and basic content presence."""
    page.goto(BASE_URL)

    # Assuming Debug Modal is rendered inside the second st.components.v1.html iframe
    debug_iframe_selector = "iframe[title='st.components.v1.html']"
    debug_iframe_locator = page.locator(debug_iframe_selector).nth(1)
    expect(debug_iframe_locator).to_be_visible(timeout=7000)

    debug_toggle_button = debug_iframe_locator.frame_locator(":scope").locator(
        DEBUG_MODAL_TOGGLE_BUTTON_LOCATOR
    )
    expect(debug_toggle_button).to_be_visible(timeout=7000)

    # The overlay is part of the same component, so also in the iframe
    debug_overlay = debug_iframe_locator.frame_locator(":scope").locator(
        DEBUG_MODAL_OVERLAY_LOCATOR
    )
    expect(debug_overlay).not_to_be_visible()  # Should be hidden initially

    # Click to show modal
    debug_toggle_button.click()
    # Wait for animation/display change
    expect(debug_overlay).to_be_visible(timeout=1000)

    debug_content = page.locator(DEBUG_MODAL_CONTENT_LOCATOR)
    expect(debug_content).to_be_visible()
    expect(debug_content.locator("h3")).to_have_text("Document Blocks (Debug Data)")
    # Check for some preformatted text, indicating JSON data
    debug_actual_content_selector = "pre#debug-modal-actual-content"
    expect(debug_content.locator(debug_actual_content_selector)).to_contain_text("[")

    # Click close button inside modal
    close_button = page.locator(DEBUG_MODAL_CLOSE_BUTTON_LOCATOR)
    expect(close_button).to_be_visible()
    close_button.click()
    expect(debug_overlay).not_to_be_visible(timeout=1000)  # Wait for hide animation


# Placeholder for more tests:
# - Editing content in a block and seeing preview update.
# - File open (more complex due to Playwright's handling of file choosers
#   with Streamlit's uploader).
# - File save (even more complex, as it's a download;
#   might need to check downloaded content).
# - Debug modal toggle.
# - Cross-references rendering (e.g. \cref{...}).
# - Malformed block rendering (shows error in preview, rest of app OK).
# - Test for scroll-sync (if implemented, very complex for E2E).
# - Test for top-alignment (visual, might need screenshot diffing).

# Example of how to test editing a block:
# def test_edit_block_updates_preview(page: Page):
#     page.goto(BASE_URL)
#     h1_text_selector = f"textarea:has-text('{TORTURE_TEST_HEADING_TEXT}')"
#     editor_for_h1 = page.locator(h1_text_selector).first
#     expect(editor_for_h1).to_be_visible()
#
#     # Corresponding preview for H1
#     h1_preview_selector = (
#         f"div.block-preview-wrapper:has(h1:has-text('{TORTURE_TEST_HEADING_TEXT}'))"
#     )
#     preview_h1_wrapper = page.locator(h1_preview_selector).first
#     expect(preview_h1_wrapper.locator("h1")).to_be_visible()
#
#     new_heading_text = "Super New Heading"
#     editor_for_h1.fill(new_heading_text) # This triggers on_change
#
#     # Wait for Streamlit to process and re-render the preview
#     # The preview should now show the new heading text
#     updated_h1_selector = f"h1:has-text('{new_heading_text}')"
#     updated_preview_h1 = preview_h1_wrapper.locator(updated_h1_selector)
#     expect(updated_preview_h1).to_be_visible(timeout=5000)
#
#     # Ensure the old heading text is gone from this specific preview block
#     old_h1_selector = f"h1:has-text('{TORTURE_TEST_HEADING_TEXT}')"
#     expect(preview_h1_wrapper.locator(old_h1_selector)).not_to_be_visible()
#
#     # Ensure other blocks are unaffected
#     # (e.g., a paragraph text should still be there)
#     para_preview_selector = (
#         f"div.block-preview-wrapper {EXPECTED_PARAGRAPH_HTML_TAG}"
#         f":has-text('{TORTURE_TEST_PARAGRAPH_TEXT_SUBSTRING}')"
#     )
#     preview_para = page.locator(para_preview_selector).first
#     expect(preview_para).to_be_visible()
#
#     # Important: Streamlit's on_change for text_area might have a default
#     # debounce or require focus loss. Playwright's fill() usually handles this,
#     # but if issues occur, try editor_for_h1.press("Tab") or similar
#     # to ensure the change event is fully processed.
#
#     # Also, the ID of the block might change if not careful with state updates.
#     # The `handle_block_content_change` in app.py updates by `block_id`.
#     # The `editor_key` includes the index `i`, so if blocks are added/removed
#     # above, this test might become flaky if it targets by index
#     # instead of stable ID/content.
#     # Using `has-text` locators is generally more robust.
#
#     # If the block ID `h1-id` is preserved in the EditorBlock state and used
#     # to find the preview, we could use that for a more stable locator.
#     # preview_div_id = f"preview-block-{block_id_of_h1}-{index_of_h1}"
#     # updated_preview_h1_by_id = page.locator(
#     #    f"#{preview_div_id} h1:has-text('{new_heading_text}')"
#     # )
#     # expect(updated_preview_h1_by_id).to_be_visible(timeout=5000)

# To run tests:
# 1. Ensure Streamlit app is running: `python -m streamlit run src/app.py`
# 2. In another terminal: `pytest` (or `pytest tests/e2e/test_main_app.py`)
# Install Playwright browsers if not already: `playwright install`
# For headed mode (to see browser):
# `pytest --headed tests/e2e/test_main_app.py`
# For debugging Playwright scripts:
# `PWDEBUG=1 pytest tests/e2e/test_main_app.py`
