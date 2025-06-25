import re
from playwright.sync_api import Page, expect

# Since Streamlit runs on a specific port (default 8501),
# we need to ensure the app is running before these tests.
# For automated CI, this might involve starting the Streamlit app as a subprocess.

BASE_URL = "http://localhost:8501"


def test_streamlit_app_loads_and_has_title(page: Page):
    """
    Tests if the Streamlit application loads and has the correct title.
    """
    page.goto(BASE_URL)

    # Check for the title set in main.py
    expect(page).to_have_title(re.compile("Pandoc Block Editor"))

    # Check for the welcome message
    welcome_message = page.locator(
        'text="Welcome to the Pandoc Block Editor (Streamlit Version)"'
    )
    expect(welcome_message).to_be_visible()


def test_basic_interaction_placeholder(page: Page):
    """
    Placeholder for a basic interaction test.
    This test will likely fail or need adjustment as UI elements are added.
    """
    page.goto(BASE_URL)
    # Example: look for a button (that doesn't exist yet)
    # add_block_button = page.get_by_role("button", name="Add Block")
    # expect(add_block_button).to_be_visible() # This would fail initially
    # Check for a known Streamlit container element instead of just 'body'
    expect(page.locator("div.stApp")).to_be_visible()


# More E2E tests will be added here as the application develops.
# These tests will simulate user workflows through the UI.
# Examples:
# - Opening a file
# - Editing a block
# - Adding new blocks
# - Observing scroll-sync and top-alignment (if applicable to Streamlit version)
# - Saving the file and verifying content (might be harder with Streamlit's model)
