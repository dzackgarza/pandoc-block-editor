import json
import os
import hashlib
import subprocess
from functools import lru_cache

import pypandoc

# Try to import fast markdown library, fallback if not available
try:
    import markdown
    FAST_MARKDOWN_AVAILABLE = True
except ImportError:
    FAST_MARKDOWN_AVAILABLE = False
    print("Warning: 'markdown' library not available. Install with: pip install markdown")

# Try to get pandoc path if it's bundled or in a known location
# This is a common pattern if you're distributing pandoc with your app
PANDOC_PATH = os.getenv("PANDOC_PATH")

# Simple cache for HTML conversions to avoid repeated Pandoc calls
_html_cache = {}


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
            extra_args=["--metadata", "title="],  # Suppress title warnings
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
                "--metadata", "title=",  # Suppress title warnings
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


def convert_markdown_to_html(markdown_string, use_cache=True):
    """
    Converts Markdown directly to HTML using Pandoc.
    Includes local MathML and Pygments syntax highlighting for faster performance.
    
    Args:
        markdown_string (str): The Markdown content to convert
        use_cache (bool): Whether to use caching for faster repeated conversions
    """
    if not markdown_string:
        return ""
    
    # Check cache first if enabled
    if use_cache:
        cache_key = hashlib.md5(markdown_string.encode('utf-8')).hexdigest()
        if cache_key in _html_cache:
            return _html_cache[cache_key]
    
    try:
        extra_args = [
            "--mathml",  # Use MathML instead of external MathJax for speed
            "--highlight-style=pygments",  # Enables syntax highlighting
            "--metadata", "title=",  # Suppress title warnings
        ]
        html_output = pypandoc.convert_text(
            source=markdown_string,
            to="html",  # HTML fragments, not full documents
            format="markdown",
            extra_args=extra_args,
            encoding="utf-8",
        )
        
        # Cache the result if caching is enabled
        if use_cache:
            _html_cache[cache_key] = html_output
        
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


def convert_markdown_to_html_fast(markdown_string):
    """
    Fast HTML conversion for block fragments - no CSS, no title warnings.
    """
    if not markdown_string:
        return ""
    try:
        # Minimal args for HTML fragments only
        extra_args = [
            "--metadata", "title=",  # Suppress title warnings
        ]
        html_output = pypandoc.convert_text(
            source=markdown_string,
            to="html",  # Just html, not html5 with full document
            format="markdown",
            extra_args=extra_args,
            encoding="utf-8",
        )
        return html_output
    except RuntimeError as e:
        print(f"Error in convert_markdown_to_html_fast: {e}")
        return f"<p>Error: {e}</p>"
    except (IOError, ValueError) as e:
        print(f"Unexpected error in convert_markdown_to_html_fast: {e}")
        return f"<p>Unexpected error: {e}</p>"


def convert_markdown_to_html_direct(markdown_string, use_cache=True):
    """
    Direct pandoc subprocess call for maximum speed.
    """
    if not markdown_string:
        return ""
    
    # Check cache first if enabled
    if use_cache:
        cache_key = hashlib.md5(markdown_string.encode('utf-8')).hexdigest()
        if cache_key in _html_cache:
            return _html_cache[cache_key]
    
    try:
        # Direct pandoc call with minimal overhead
        result = subprocess.run([
            'pandoc',
            '--from=markdown',
            '--to=html',
            '--metadata', 'title=',
        ], 
        input=markdown_string,
        text=True,
        capture_output=True,
        timeout=5  # Prevent hanging
        )
        
        if result.returncode == 0:
            html_output = result.stdout
            
            # Cache the result if caching is enabled
            if use_cache:
                _html_cache[cache_key] = html_output
            
            return html_output
        else:
            print(f"Pandoc error: {result.stderr}")
            return f"<p>Pandoc error: {result.stderr}</p>"
            
    except subprocess.TimeoutExpired:
        return "<p>Pandoc timeout - content too complex</p>"
    except FileNotFoundError:
        # Fall back to pypandoc if pandoc not found
        return convert_markdown_to_html_fast(markdown_string)
    except Exception as e:
        print(f"Direct pandoc error: {e}")
        return f"<p>Direct pandoc error: {e}</p>"


def convert_markdown_to_html_ultrafast(markdown_string):
    """
    Ultra-fast markdown to HTML conversion for block previews.
    Uses lightweight Python markdown library instead of Pandoc.
    Perfect for editing previews where speed > perfect compatibility.
    """
    if not markdown_string:
        return ""
    
    if not FAST_MARKDOWN_AVAILABLE:
        # Fallback to fast pandoc if markdown library not available
        return convert_markdown_to_html_direct(markdown_string)
    
    try:
        # Configure markdown with common extensions for better compatibility
        md = markdown.Markdown(extensions=[
            'codehilite',  # Syntax highlighting
            'fenced_code',  # ```code``` blocks
            'tables',  # Table support
            'toc',  # Table of contents
        ])
        html_output = md.convert(markdown_string)
        return html_output
    except Exception as e:
        print(f"Fast markdown error: {e}")
        # Fallback to pandoc on error
        return convert_markdown_to_html_direct(markdown_string)


def clear_html_cache():
    """Clear the HTML conversion cache to free memory."""
    global _html_cache
    _html_cache.clear()


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
