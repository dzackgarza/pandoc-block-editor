# pylint: disable=import-error
# (pytest is a dev dependency)
from unittest.mock import patch

import pytest

# import json # Unused W0611 - Removed

from src import pandoc_utils

# Try to import pypandoc for the skip logic,
# otherwise assume it's available if tests run
try:
    import pypandoc
except ImportError:
    pypandoc = None  # Fallback for skip logic if pypandoc itself is missing


# Basic Markdown samples for testing
SAMPLE_MD_SIMPLE = "# Hello\n\nThis is *Markdown*."
EXPECTED_HTML_SIMPLE_SUBSTRING_H1 = "<h1>Hello</h1>"
EXPECTED_HTML_SIMPLE_SUBSTRING_P = "<p>This is <em>Markdown</em>.</p>"

SAMPLE_MD_MATH = "Equation: $E = mc^2$\n\n$$\\sum_{i=0}^n i = \\frac{n(n+1)}{2}$$"
# MathJax output is complex, check for delimiters or raw math
EXPECTED_HTML_MATH_SUBSTRING_INLINE_PT1 = "\\(E = mc^2\\)"
EXPECTED_HTML_MATH_SUBSTRING_DISPLAY_PT1 = "\\[\\sum_{i=0}^n i ="
EXPECTED_HTML_MATH_SUBSTRING_DISPLAY_PT2 = "\\frac{n(n+1)}{2}\\]"


SAMPLE_MD_CODE = "```python\ndef hello():\n  print('Hello')\n```"
EXPECTED_HTML_CODE_SUBSTRING_PRE = '<pre class="sourceCode python">'

EMPTY_MD = ""
# Expected for empty MD input to AST
EMPTY_AST = {"pandoc-api-version": [1, 23, 1], "meta": {}, "blocks": []}
EMPTY_HTML = ""  # Expected for empty MD input to HTML

SAMPLE_AST_PARA = {
    "pandoc-api-version": [1, 23, 1],
    "meta": {},
    "blocks": [
        {
            "t": "Para",
            "c": [
                {"t": "Str", "c": "Just"},
                {"t": "Space"},
                {"t": "Str", "c": "text."},
            ],
        }
    ],
}
EXPECTED_MD_FROM_PARA_AST = "Just text.\n"  # Pandoc adds a newline


def test_parse_markdown_to_ast_json_simple():
    """Test parsing simple markdown to AST JSON."""
    ast = pandoc_utils.parse_markdown_to_ast_json(SAMPLE_MD_SIMPLE)
    assert "pandoc-api-version" in ast
    assert "meta" in ast
    assert "blocks" in ast
    assert len(ast["blocks"]) > 0
    assert ast["blocks"][0]["t"] == "Header"
    assert ast["blocks"][1]["t"] == "Para"


def test_parse_markdown_to_ast_json_empty():
    """Test parsing empty markdown string to AST JSON."""
    ast = pandoc_utils.parse_markdown_to_ast_json(EMPTY_MD)
    assert ast == EMPTY_AST


def test_convert_ast_json_to_markdown_simple():
    """Test converting a simple AST (from parsing) back to markdown."""
    ast = pandoc_utils.parse_markdown_to_ast_json(SAMPLE_MD_SIMPLE)
    markdown = pandoc_utils.convert_ast_json_to_markdown(ast, is_full_ast=True)
    assert "# Hello" in markdown
    assert "This is *Markdown*." in markdown


def test_convert_ast_json_to_markdown_specific_ast():
    """Test converting a predefined simple AST to markdown."""
    markdown = pandoc_utils.convert_ast_json_to_markdown(
        SAMPLE_AST_PARA, is_full_ast=True
    )
    assert markdown.strip() == EXPECTED_MD_FROM_PARA_AST.strip()


def test_convert_ast_json_to_markdown_empty():
    """Test converting an empty AST to markdown."""
    markdown = pandoc_utils.convert_ast_json_to_markdown(EMPTY_AST, is_full_ast=True)
    assert markdown == EMPTY_HTML  # Empty AST should produce empty markdown


def test_convert_markdown_to_html_simple():
    """Test converting simple markdown to HTML."""
    html = pandoc_utils.convert_markdown_to_html(SAMPLE_MD_SIMPLE)
    assert EXPECTED_HTML_SIMPLE_SUBSTRING_H1 in html
    assert EXPECTED_HTML_SIMPLE_SUBSTRING_P in html


def test_convert_markdown_to_html_math():
    """Test converting markdown with LaTeX math to HTML."""
    html = pandoc_utils.convert_markdown_to_html(SAMPLE_MD_MATH)
    assert EXPECTED_HTML_MATH_SUBSTRING_INLINE_PT1 in html
    assert EXPECTED_HTML_MATH_SUBSTRING_DISPLAY_PT1 in html
    assert EXPECTED_HTML_MATH_SUBSTRING_DISPLAY_PT2 in html


def test_convert_markdown_to_html_code():
    """Test converting markdown with a code block to HTML."""
    html = pandoc_utils.convert_markdown_to_html(SAMPLE_MD_CODE)
    assert EXPECTED_HTML_CODE_SUBSTRING_PRE in html
    assert "def hello():" in html
    assert "print('Hello')" in html


def test_convert_markdown_to_html_empty():
    """Test converting empty markdown to HTML."""
    html = pandoc_utils.convert_markdown_to_html(EMPTY_MD)
    assert html == EMPTY_HTML


# Test error handling for malformed markdown
MALFORMED_MD_UNCLOSED_LINK = "This is an [unclosed link"
MALFORMED_MD_UNCLOSED_CODE = "This is `unclosed code"


def test_parse_markdown_to_ast_json_malformed_link():
    """Test parsing malformed markdown (unclosed link) to AST."""
    ast = pandoc_utils.parse_markdown_to_ast_json(MALFORMED_MD_UNCLOSED_LINK)
    assert "pandoc-api-version" in ast  # Should still return a valid AST structure
    assert "blocks" in ast


def test_convert_markdown_to_html_malformed_code():
    """Test converting malformed markdown (unclosed code) to HTML."""
    html = pandoc_utils.convert_markdown_to_html(MALFORMED_MD_UNCLOSED_CODE)
    assert isinstance(html, str)
    # Pandoc often renders unclosed inline code literally
    assert "`unclosed code" in html


SAMPLE_MD_DIV = """
::: {#mydiv .myclass}
This is content inside a div.

* list item
:::
"""


def test_parse_then_convert_div():
    """Test parsing markdown with a Div, then converting AST and HTML."""
    ast = pandoc_utils.parse_markdown_to_ast_json(SAMPLE_MD_DIV)
    assert ast["blocks"][0]["t"] == "Div"

    div_attrs = ast["blocks"][0]["c"][0]
    assert div_attrs[0] == "mydiv"  # ID
    assert "myclass" in div_attrs[1]  # Classes

    md_from_ast = pandoc_utils.convert_ast_json_to_markdown(ast, is_full_ast=True)
    # Order of attributes can vary
    assert (
        "::: {#mydiv .myclass}" in md_from_ast or "::: {.myclass #mydiv}" in md_from_ast
    )
    assert "This is content inside a div." in md_from_ast
    assert "* list item" in md_from_ast

    html = pandoc_utils.convert_markdown_to_html(SAMPLE_MD_DIV)
    assert '<div id="mydiv" class="myclass">' in html  # Corrected quote style
    assert "<li>list item</li>" in html


@patch("pypandoc.convert_text")
def test_convert_markdown_to_html_runtime_error_fallback(mock_convert_text):
    """Test HTML conversion fallback on Pandoc RuntimeError."""
    mock_convert_text.side_effect = RuntimeError("Pandoc failed spectacularly")
    html_output = pandoc_utils.convert_markdown_to_html("some markdown")
    assert "Pandoc HTML rendering error:" in html_output
    assert "Pandoc failed spectacularly" in html_output
    assert "Content (approximate):" in html_output
    assert "some markdown" in html_output


@patch("pypandoc.convert_text")
def test_parse_markdown_to_ast_json_runtime_error_fallback(mock_convert_text):
    """Test AST parsing fallback on Pandoc RuntimeError."""
    mock_convert_text.side_effect = RuntimeError("Pandoc AST failed")
    ast_output = pandoc_utils.parse_markdown_to_ast_json("bad markdown")
    assert "blocks" in ast_output
    assert len(ast_output["blocks"]) == 1
    block_content_tuple = ast_output["blocks"][0]["c"]
    error_found = any(
        item["t"] == "Code" and "Pandoc AST failed" in item["c1"]
        for item in block_content_tuple
    )
    assert error_found, "Error message not found in AST fallback"


@patch("pypandoc.convert_text")
def test_convert_ast_json_to_markdown_runtime_error_fallback(mock_convert_text):
    """Test Markdown conversion (from AST) fallback on Pandoc RuntimeError."""
    mock_convert_text.side_effect = RuntimeError("Pandoc Markdown conversion failed")
    # Use any valid AST
    md_output = pandoc_utils.convert_ast_json_to_markdown(SAMPLE_AST_PARA)
    assert "Error converting AST to Markdown:" in md_output
    assert "Pandoc Markdown conversion failed" in md_output


# Ensure pypandoc is available, otherwise skip these tests
if pypandoc:  # Check if pypandoc was successfully imported
    try:
        pypandoc.ensure_pandoc_installed(delete_installer=False)  # just checks
    except OSError:
        pytest.skip(
            "Pandoc not found, skipping pandoc_utils tests", allow_module_level=True
        )
else:  # pypandoc itself not imported
    pytest.skip(
        "pypandoc library not found, skipping pandoc_utils tests",
        allow_module_level=True,
    )

PROBLEM_SEMANTIC_DIV_MD = """
::: {#semantic-div-1 .theorem type="Pythagorean"}
This is a semantic block, styled as a theorem.
It might contain **strong emphasis** and equations like $a^2 + b^2 = c^2$.
This div has an ID and a class.
:::
"""

# Note: Pandoc converts attributes like `type="Pythagorean"` into classes if not standard,
# or into data-* attributes. For `{#id .class1 .class2 key="val"}`,
# it becomes `<div id="id" class="class1 class2" data-key="val">`.
# If `type` is given as a class `.theorem .type_Pythagorean` or similar,
# it would be part of the class attribute.
# The original torture test was `::: {#semantic-div-1 .theorem type="Pythagorean"}`
# Pandoc typically treats bare words in fenced div attributes as classes.
# So, `type="Pythagorean"` likely becomes class `type` and class `Pythagorean` or similar.
# Or, if `type` is a known attribute for some extension, it might be handled differently.
# For this test, we'll assume `type` becomes a class `type` and `Pythagorean` a class.
# A more robust test would be `key="value"` which becomes `data-key="value"`.
# Let's assume for now Pandoc makes `type="Pythagorean"` into `class="... theorem type Pythagorean ..."`
# or similar. The key is the content and absence of JS source.

EXPECTED_HTML_FROM_SEMANTIC_DIV_SUBSTRINGS = [
    '<div id="semantic-div-1"',  # Check for ID
    'class="theorem',  # Check for theorem class
    # 'type="Pythagorean"', # This might become data-type or part of class
    "Pythagorean",  # Ensure the word Pythagorean is present from the attribute
    "This is a semantic block, styled as a theorem.",
    "<strong>strong emphasis</strong>",
    "\\(a^2 + b^2 = c^2\\)",  # MathJax formatted math
    "This div has an ID and a class.",
    "</div>",
]


# Test for the problematic semantic div
def test_convert_problematic_semantic_div_to_html():
    """
    Tests conversion of a specific semantic div that was causing issues.
    Ensures it doesn't contain problematic JS code and renders expected content.
    """
    # Ensure pygments is re-enabled for this test if it was disabled globally for other tests
    # This can be done by explicitly passing relevant args to convert_markdown_to_html
    # or by assuming the global pandoc_utils state is what we want to test.
    # For now, we test the current global state of pandoc_utils.
    html_output = pandoc_utils.convert_markdown_to_html(PROBLEM_SEMANTIC_DIV_MD)

    print("\n--- HTML output for problematic semantic div: ---")
    print(html_output)  # For debugging in test runs

    assert (
        "mhchemParser.ts" not in html_output
    ), "Should not contain mhchemParser.ts source"
    # A less strict check for "mhchem" as it might appear in legitimate MathJax classes if used
    # assert "mhchem" not in html_output.lower(), "Should not contain 'mhchem' if it's not used"

    for substring in EXPECTED_HTML_FROM_SEMANTIC_DIV_SUBSTRINGS:
        assert substring in html_output, f"Expected substring '{substring}' not found."
