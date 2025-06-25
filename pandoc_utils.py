import subprocess
import json

# 2. Implement pandocService Equivalent

def run_pandoc(args):
    """Helper function to run a pandoc command and return its output."""
    try:
        process = subprocess.run(['pandoc'] + args, capture_output=True, text=True, check=True)
        return process.stdout
    except FileNotFoundError:
        # This error occurs if pandoc command is not found
        raise RuntimeError("Pandoc command not found. Please ensure Pandoc is installed and in your system's PATH.")
    except subprocess.CalledProcessError as e:
        # This error occurs if pandoc returns a non-zero exit code
        error_message = f"Pandoc error (exit code {e.returncode}):\n{e.stderr}"
        # Try to parse stderr as JSON if it's a Pandoc internal error
        try:
            error_json = json.loads(e.stderr)
            if error_json and isinstance(error_json, list) and error_json[0].get("tag") == "PandocError":
                error_message = f"Pandoc internal error: {error_json[0].get('message', e.stderr)}"
        except json.JSONDecodeError:
            pass # Stderr was not JSON
        raise RuntimeError(error_message)
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred while running Pandoc: {str(e)}")

def parse_markdown_to_ast_json(markdown_string):
    """Converts Markdown string to Pandoc JSON AST."""
    if not isinstance(markdown_string, str):
        raise ValueError("Input must be a string.")
    # Use 'json' format for Pandoc AST output, earlier versions used 'native'
    # Pandoc versions >= 2.0 use 'json' for AST output.
    # Using '-f markdown-citations' to enable citation processing by default if any.
    # Adding common extensions that are useful for academic/technical markdown.
    from_format = 'markdown+pipe_tables+strikeout+auto_identifiers+smart+tex_math_dollars+raw_tex+citations'
    try:
        ast_str = run_pandoc(['-f', from_format, '-t', 'json', '--preserve-tabs'])
        # Pandoc with -t json takes input from stdin by default
        process = subprocess.run(['pandoc', '-f', from_format, '-t', 'json', '--preserve-tabs'],
                                 input=markdown_string, capture_output=True, text=True, check=True)
        return json.loads(process.stdout)
    except json.JSONDecodeError:
        raise RuntimeError("Failed to decode Pandoc AST JSON output.")
    except RuntimeError as e:
        # Re-raise with more context if needed
        raise RuntimeError(f"Error parsing Markdown to AST: {e}")


def convert_ast_json_to_html(ast_json, mathjax=True, highlight_style='pygments'):
    """Converts Pandoc JSON AST to HTML."""
    if not isinstance(ast_json, dict):
        raise ValueError("Input AST must be a dictionary.")
    
    args = ['-f', 'json', '-t', 'html', '--standalone'] # --standalone to get a full HTML document structure for block previews initially
    if mathjax:
        args.append('--mathjax') # Default MathJax CDN
    if highlight_style:
        args.extend(['--highlight-style', highlight_style])
    
    # Pandoc expects the AST as a JSON string via stdin
    ast_string = json.dumps(ast_json)
    try:
        return run_pandoc(args, input_data=ast_string)
    except RuntimeError as e:
        # Re-raise with more context
        raise RuntimeError(f"Error converting AST to HTML: {e}")

def convert_markdown_to_html(markdown_string, mathjax=True, highlight_style='pygments'):
    """Converts a Markdown string directly to HTML."""
    if not isinstance(markdown_string, str):
        raise ValueError("Input must be a string.")
    
    # Base format for Markdown input
    from_format = 'markdown+pipe_tables+strikeout+auto_identifiers+smart+tex_math_dollars+raw_tex+citations'
    
    args = ['-f', from_format, '-t', 'html'] # Not standalone for block content
    if mathjax:
        args.append('--mathjax')
    if highlight_style:
        args.extend(['--highlight-style', highlight_style])
    
    try:
        # Pass markdown_string as input to pandoc
        process = subprocess.run(['pandoc'] + args, input=markdown_string, capture_output=True, text=True, check=True)
        return process.stdout
    except RuntimeError as e:
        raise RuntimeError(f"Error converting Markdown to HTML: {e}")
    except FileNotFoundError:
        raise RuntimeError("Pandoc command not found. Please ensure Pandoc is installed and in your system's PATH.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Pandoc error (exit code {e.returncode}) converting Markdown to HTML:\n{e.stderr}")


def convert_ast_json_to_markdown(ast_json):
    """Converts Pandoc JSON AST back to Markdown."""
    if not isinstance(ast_json, dict):
        # This function might receive just a list of blocks, e.g. for inline content or content of a Div
        # The pandoc JSON AST structure is {"pandoc-api-version": [...], "meta": {...}, "blocks": [...]}
        # If we get just a list of blocks, we need to wrap it for Pandoc.
        # However, for converting parts like header inlines or div content, we might have a simpler structure.
        # Let's assume for now ast_json is a full valid Pandoc AST document structure.
        # If it's just a list of blocks, we might need to construct a minimal AST document.
        if isinstance(ast_json, list): # Assuming this is a list of block elements
            # Create a minimal valid Pandoc AST document
            # Find the API version from a full parse if possible, or use a common one.
            # For now, let's assume ast_json is always a full AST.
            # A more robust solution would detect this and wrap appropriately.
            pass # Fall through to assume it's a dict. If it's a list, it will error.
        else:
            raise ValueError("Input AST must be a dictionary (full Pandoc AST).")

    # Target format for Markdown output
    to_format = 'markdown_strict+pipe_tables+strikeout+auto_identifiers+smart+tex_math_dollars+raw_tex-citations'
    # Using markdown_strict to get simpler markdown, but adding extensions for features we want to preserve.
    # Removed +citations from output format to avoid pandoc trying to process bibliography if not present.
    
    args = ['-f', 'json', '-t', to_format, '--preserve-tabs']
    
    ast_string = json.dumps(ast_json)
    try:
        # Pass ast_string as input to pandoc
        process = subprocess.run(['pandoc'] + args, input=ast_string, capture_output=True, text=True, check=True)
        return process.stdout.strip() # Strip trailing newlines often added by Pandoc
    except RuntimeError as e:
        raise RuntimeError(f"Error converting AST to Markdown: {e}")
    except FileNotFoundError:
        raise RuntimeError("Pandoc command not found. Please ensure Pandoc is installed and in your system's PATH.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Pandoc error (exit code {e.returncode}) converting AST to Markdown:\n{e.stderr}")

# Helper to modify run_pandoc to accept input_data
def run_pandoc(args, input_data=None):
    """Helper function to run a pandoc command and return its output, optionally with input_data."""
    try:
        process = subprocess.run(['pandoc'] + args, input=input_data, capture_output=True, text=True, check=True)
        return process.stdout
    except FileNotFoundError:
        raise RuntimeError("Pandoc command not found. Please ensure Pandoc is installed and in your system's PATH.")
    except subprocess.CalledProcessError as e:
        error_message = f"Pandoc error (exit code {e.returncode}):\n{e.stderr}"
        # Attempt to parse stderr as JSON for Pandoc internal errors
        try:
            # Pandoc sometimes outputs JSON errors to stderr
            error_content = e.stderr.strip()
            # A common Pandoc JSON error starts with '[{"tag":"PandocError"'
            if error_content.startswith('[') and error_content.endswith(']'):
                error_json = json.loads(error_content)
                if error_json and isinstance(error_json, list) and len(error_json) > 0 and "tag" in error_json[0] and error_json[0]["tag"] == "PandocError":
                    error_message = f"Pandoc internal error: {error_json[0].get('message', e.stderr)}"
            # Sometimes it's just a plain text message
            elif "PandocError" in e.stderr: # Heuristic
                 error_message = f"Pandoc internal error: {e.stderr}"

        except json.JSONDecodeError:
            pass # stderr was not JSON or not the expected structure
        raise RuntimeError(error_message)
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred while running Pandoc: {str(e)}")


# Refined parse_markdown_to_ast_json
def parse_markdown_to_ast_json(markdown_string):
    if not isinstance(markdown_string, str):
        raise ValueError("Input must be a string.")
    from_format = 'markdown+pipe_tables+strikeout+auto_identifiers+smart+tex_math_dollars+raw_tex+citations+fenced_divs+bracketed_spans+definition_lists'
    args = ['-f', from_format, '-t', 'json', '--preserve-tabs']
    try:
        ast_str = run_pandoc(args, input_data=markdown_string)
        return json.loads(ast_str)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to decode Pandoc AST JSON output. Output was: {ast_str[:500]}... Error: {e}")
    except RuntimeError as e:
        raise RuntimeError(f"Error parsing Markdown to AST: {e}")


# Refined convert_ast_json_to_html
def convert_ast_json_to_html(ast_json, mathjax=True, highlight_style='pygments'):
    if not isinstance(ast_json, dict):
        raise ValueError("Input AST must be a dictionary.")
    
    # For block previews, we don't want a full standalone HTML document,
    # just the HTML fragment corresponding to the block's content.
    # Pandoc's default HTML output isn't standalone unless specified.
    args = ['-f', 'json', '-t', 'html'] 
    if mathjax:
        args.append('--mathjax') 
    if highlight_style:
        args.extend(['--highlight-style', highlight_style])
    
    ast_string = json.dumps(ast_json)
    try:
        return run_pandoc(args, input_data=ast_string)
    except RuntimeError as e:
        raise RuntimeError(f"Error converting AST to HTML: {e}")

# Refined convert_markdown_to_html (this is a key function for live preview of a block)
def convert_markdown_to_html(markdown_string, mathjax=True, highlight_style='pygments'):
    if not isinstance(markdown_string, str):
        if markdown_string is None:
            markdown_string = ""
        else:
            raise ValueError("Input must be a string or None.")

    # Added +tex_math_single_backslash for \(...\) and \[...\]
    from_format = 'markdown+pipe_tables+strikeout+auto_identifiers+smart+tex_math_dollars+raw_tex+citations+fenced_divs+bracketed_spans+definition_lists+tex_math_single_backslash'
    
    args = ['-f', from_format, '-t', 'html']
    if mathjax:
        args.append('--mathjax') # This will add MathJax CDN link if block contains math
    if highlight_style:
        args.extend(['--highlight-style', highlight_style])
    
    try:
        html_output = run_pandoc(args, input_data=markdown_string)
        return html_output
    except RuntimeError as e:
        # Provide the failing markdown for easier debugging
        # Limit length of markdown in error to avoid huge messages
        md_snippet = markdown_string[:200] + "..." if len(markdown_string) > 200 else markdown_string
        raise RuntimeError(f"Error converting Markdown to HTML for content: '{md_snippet}'. Details: {e}")


# Refined convert_ast_json_to_markdown
def convert_ast_json_to_markdown(ast_json_or_list_of_blocks, is_full_ast=True):
    """
    Converts Pandoc JSON AST (or just a list of blocks from an AST) back to Markdown.
    :param ast_json_or_list_of_blocks: Either a full Pandoc AST dict or a list of block elements.
    :param is_full_ast: Set to False if ast_json_or_list_of_blocks is just a list of blocks.
    """
    target_ast = {}
    if is_full_ast:
        if not isinstance(ast_json_or_list_of_blocks, dict):
            raise ValueError("Input AST must be a dictionary if is_full_ast is True.")
        target_ast = ast_json_or_list_of_blocks
    else:
        if not isinstance(ast_json_or_list_of_blocks, list):
            raise ValueError("Input must be a list of blocks if is_full_ast is False.")
        # Construct a minimal valid Pandoc AST document from the list of blocks
        # A common Pandoc API version. This should ideally be dynamic or configurable.
        target_ast = {
            "pandoc-api-version": [1, 22, 2, 1], # Example, might need adjustment
            "meta": {},
            "blocks": ast_json_or_list_of_blocks
        }

    to_format = 'markdown_strict+pipe_tables+strikeout+auto_identifiers+smart+tex_math_dollars+raw_tex-citations+fenced_divs+bracketed_spans+definition_lists'
    args = ['-f', 'json', '-t', to_format, '--preserve-tabs']
    
    ast_string = json.dumps(target_ast)
    try:
        markdown_output = run_pandoc(args, input_data=ast_string)
        return markdown_output.strip() 
    except RuntimeError as e:
        raise RuntimeError(f"Error converting AST to Markdown: {e}")

# Example Usage (for testing, will be removed or commented out)
if __name__ == '__main__':
    test_md = """
# Hello World

This is a test.

- Item 1
- Item 2

```python
print("Hello")
```

::: {.custom id="mydiv"}
This is a div.
:::

$$E=mc^2$$
"""
    print("--- Testing parse_markdown_to_ast_json ---")
    try:
        ast = parse_markdown_to_ast_json(test_md)
        # print(json.dumps(ast, indent=2))
        print("AST parsing successful (output omitted for brevity).")
        
        print("\n--- Testing convert_ast_json_to_html ---")
        html_from_ast = convert_ast_json_to_html(ast)
        # print(html_from_ast)
        print("HTML from AST conversion successful (output omitted for brevity).")

        print("\n--- Testing convert_markdown_to_html ---")
        direct_html = convert_markdown_to_html(test_md)
        # print(direct_html)
        print("Direct Markdown to HTML conversion successful (output omitted for brevity).")

        print("\n--- Testing convert_ast_json_to_markdown ---")
        # Test with full AST
        md_from_ast = convert_ast_json_to_markdown(ast, is_full_ast=True)
        # print(md_from_ast)
        print("Markdown from full AST conversion successful (output omitted for brevity).")
        
        # Test with just blocks (e.g. content of a Div)
        if ast['blocks'] and len(ast['blocks']) > 3 and ast['blocks'][3].get('t') == 'Div':
            div_content_blocks = ast['blocks'][3]['c'][1] # Get the content blocks of the Div
            print("\n--- Testing convert_ast_json_to_markdown (list of blocks) ---")
            md_from_blocks = convert_ast_json_to_markdown(div_content_blocks, is_full_ast=False)
            # print(md_from_blocks)
            print("Markdown from list of blocks (Div content) successful (output omitted for brevity).")

        print("\n--- Testing error handling for malformed markdown (HTML conversion) ---")
        malformed_md = "This is [an unclosed bracket."
        try:
            convert_markdown_to_html(malformed_md)
        except RuntimeError as e:
            print(f"Successfully caught error for malformed Markdown: {e}")

        print("\n--- Testing error handling for Pandoc not found (simulated) ---")
        # This test would require actually renaming pandoc, so skip for automated run
        # but keep the logic in run_pandoc.
        print("Skipping active test for Pandoc not found (requires manual intervention).")

    except RuntimeError as e:
        print(f"A test failed: {e}")
    except ValueError as e:
        print(f"A test failed due to value error: {e}")

