import json
import os

import pypandoc

# Try to get pandoc path if it's bundled or in a known location
# This is a common pattern if you're distributing pandoc with your app
PANDOC_PATH = os.getenv("PANDOC_PATH")


def _get_pandoc_path():
    """
    Attempts to find the pandoc executable.
    pypandoc usually handles this, but this is an explicit check.
    """
    if PANDOC_PATH and os.path.exists(PANDOC_PATH):
        return PANDOC_PATH

    # pypandoc will search in common locations and PATH.
    # If pypandoc fails to find it, it will raise an OSError.
    try:
        # This ensures pypandoc has downloaded its version of pandoc if necessary
        # and checks if it's available.
        pypandoc.ensure_pandoc_installed(delete_installer=True)
    except OSError:
        # This means pandoc is not found or pypandoc couldn't install it.
        # We can log this or raise a more specific error for the app to handle.
        print("Warning: Pandoc might not be installed or found by pypandoc.")
        # Unnecessary pass removed (W0107)
    return None  # Indicates pypandoc should use its default search logic


# Call it once to ensure pandoc is ready
_get_pandoc_path()


def parse_markdown_to_ast_json(markdown_string):
    """
    Parses Markdown to Pandoc's JSON AST.
    """
    if not markdown_string:
        # Return a valid empty AST
        return {"pandoc-api-version": [1, 23, 1], "meta": {}, "blocks": []}
    try:
        ast_json_str = pypandoc.convert_text(
            source=markdown_string,
            to="json",
            format="markdown",
            encoding="utf-8",
        )
        return json.loads(ast_json_str)
    except RuntimeError as e:
        print(f"Error in parse_markdown_to_ast_json: {e}")
        # Fallback for critical errors. Unused variable 'error_message' removed.
        # Line length of the original f-string for error_message was too long.
        return {
            "pandoc-api-version": [1, 23, 1],
            "meta": {},
            "blocks": [
                {
                    "t": "Para",
                    "c": [
                        {"t": "Str", "c": "Error: Could not parse content. Details: "},
                        {"t": "Code", "c": ["", [], []], "c1": str(e)},
                    ],
                }
            ],
        }
    except (IOError, ValueError) as e:  # Catching more specific exceptions
        print(f"Unexpected error (IO/Value) in parse_markdown_to_ast_json: {e}")
        # Generic fallback
        return {
            "pandoc-api-version": [1, 23, 1],
            "meta": {},
            "blocks": [
                {
                    "t": "Para",
                    "c": [
                        {
                            "t": "Str",
                            "c": f"Unexpected IO/Value error during parsing: {e}",
                        }
                    ],
                }
            ],
        }


def convert_ast_json_to_markdown(ast_json, is_full_ast=False):
    """
    Converts Pandoc's JSON AST back to Markdown.
    """
    if not ast_json or (is_full_ast and not ast_json.get("blocks")):
        return ""
    # Unnecessary pass removed (was in an 'if not is_full_ast' block)

    try:
        markdown_output = pypandoc.convert_text(
            source=json.dumps(ast_json),
            to="markdown",
            format="json",
            encoding="utf-8",
            extra_args=[
                "--strip-comments",
                "--wrap=none",  # Try to preserve line breaks as much as possible
            ],
        )
        return markdown_output
    except RuntimeError as e:
        print(f"Error in convert_ast_json_to_markdown: {e}")
        return f"Error converting AST to Markdown: {e}"
    except (IOError, ValueError) as e:  # Catching more specific exceptions
        print(f"Unexpected error (IO/Value) in convert_ast_json_to_markdown: {e}")
        return f"Unexpected IO/Value error converting AST to Markdown: {e}"


def convert_markdown_to_html(markdown_string):
    """
    Converts Markdown directly to HTML using Pandoc.
    Includes MathJax and Pygments syntax highlighting.
    """
    if not markdown_string:
        return ""
    try:
        extra_args = [
            "--mathjax",  # Enables MathJax for LaTeX math
            "--highlight-style=pygments",  # Enables syntax highlighting
            "--self-contained",  # Embeds assets (though MathJax links to CDN)
            "--strip-comments",
        ]
        html_output = pypandoc.convert_text(
            source=markdown_string,
            to="html5",
            format="markdown",
            extra_args=extra_args,
            encoding="utf-8",
        )
        return html_output
    except RuntimeError as e:
        print(f"Error in convert_markdown_to_html: {e}")
        # Return HTML-formatted error. Broken long f-string for line length.
        error_intro = (
            "<pre style='color: red; background-color: #fdd; "
            "padding: 10px; border: 1px solid red;'>"
            "Pandoc HTML rendering error:\n"
        )
        error_details = (
            f"{str(e)}\n\nContent (approximate):\n{markdown_string[:200]}...</pre>"
        )
        return error_intro + error_details
    except (IOError, ValueError) as e:  # Catching more specific exceptions
        print(f"Unexpected error (IO/Value) in convert_markdown_to_html: {e}")
        # Broken long f-string for line length.
        return (
            "<pre style='color: red; background-color: #fdd; padding: 10px; "
            "border: 1px solid red;'>Unexpected IO/Value error during HTML "
            f"rendering:\n{str(e)}</pre>"
        )


if __name__ == "__main__":
    # Basic test cases
    MD_TEXT_SIMPLE = "# Hello\n\nThis is *Markdown*."
    print("--- Simple Markdown to AST ---")
    ast_result = parse_markdown_to_ast_json(MD_TEXT_SIMPLE)
    print(json.dumps(ast_result, indent=2))

    print("\n--- AST back to Markdown ---")
    md_from_ast_result = convert_ast_json_to_markdown(ast_result)
    print(md_from_ast_result)

    print("\n--- Simple Markdown to HTML ---")
    html_result = convert_markdown_to_html(MD_TEXT_SIMPLE)
    print(html_result)

    MD_TEXT_MATH = "Equation: $E = mc^2$\n\n$$\\sum_{i=0}^n i = \\frac{n(n+1)}{2}$$"
    print("\n--- Math Markdown to HTML ---")
    html_math_result = convert_markdown_to_html(MD_TEXT_MATH)
    print(html_math_result)

    MD_CODE = "```python\ndef hello():\n  print('Hello')\n```"
    print("\n--- Code Block Markdown to HTML ---")
    html_code_result = convert_markdown_to_html(MD_CODE)
    print(html_code_result)

    MD_TEXT_ERROR = "This is an unclosed [link example."
    print("\n--- Error Markdown to AST (expecting fallback) ---")
    # Pandoc might handle this leniently
    ast_error_result = parse_markdown_to_ast_json(MD_TEXT_ERROR)
    print(json.dumps(ast_error_result, indent=2))

    print("\n--- Error Markdown to HTML (expecting fallback or error message) ---")
    # Pandoc might handle this
    html_error_result = convert_markdown_to_html(MD_TEXT_ERROR)
    print(html_error_result)

    # Test with a more complex AST structure for markdown conversion (e.g. from a Div)
    COMPLEX_AST_DIV = {
        "pandoc-api-version": [1, 23, 1],
        "meta": {},
        "blocks": [
            {
                "t": "Div",
                "c": [
                    ["my-div", ["theorem"], [["type", "Pythagorean"]]],
                    [
                        {
                            "t": "Para",
                            "c": [
                                {"t": "Str", "c": "This"},
                                {"t": "Space"},
                                {"t": "Str", "c": "is"},
                                {"t": "Space"},
                                {"t": "Str", "c": "a"},
                                {"t": "Space"},
                                {"t": "Str", "c": "test."},
                            ],
                        }
                    ],
                ],
            }
        ],
    }
    print("\n--- Complex AST (Div) to Markdown ---")
    md_from_complex_ast_result = convert_ast_json_to_markdown(
        COMPLEX_AST_DIV, is_full_ast=True
    )
    print(md_from_complex_ast_result)
