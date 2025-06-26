# Placeholder for Pandoc utility functions
# Will be implemented in a later step.


def parse_markdown_to_ast_json(markdown_string):
    """
    Placeholder: Parses Markdown to Pandoc's JSON AST.
    """
    print(
        f"DEBUG: pandoc_utils.parse_markdown_to_ast_json called with: {markdown_string[:50]}..."
    )  # TODO: Remove
    # Simulate a basic AST structure for now to avoid breaking app.py too much
    return {
        "pandoc-api-version": [1, 23, 1],  # Example version
        "meta": {},
        "blocks": [
            {
                "t": "Para",
                "c": [{"t": "Str", "c": "Placeholder content from pandoc_utils."}],
            }
        ],
    }


def convert_ast_json_to_markdown(ast_json, is_full_ast=False):
    """
    Placeholder: Converts Pandoc's JSON AST back to Markdown.
    """
    print(
        f"DEBUG: pandoc_utils.convert_ast_json_to_markdown called with AST: {str(ast_json)[:50]}..."
    )  # TODO: Remove
    return "Placeholder Markdown from AST."


def convert_markdown_to_html(markdown_string):
    """
    Placeholder: Converts Markdown directly to HTML.
    """
    print(
        f"DEBUG: pandoc_utils.convert_markdown_to_html called with: {markdown_string[:50]}..."
    )  # TODO: Remove
    return f"<p>Placeholder HTML for: {markdown_string}</p>"
