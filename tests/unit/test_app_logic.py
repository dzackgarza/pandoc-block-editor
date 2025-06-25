from src.app_logic import sample_function, process_markdown_block


def test_sample_function():
    """
    Tests the sample_function.
    """
    assert sample_function(2) == 4
    assert sample_function(-3) == -6
    assert sample_function(0) == 0


def test_process_markdown_block_simple():
    """
    Tests basic markdown block processing.
    """
    input_md = "Hello World"
    expected_output = "Processed: Hello World"
    assert process_markdown_block(input_md) == expected_output


def test_process_markdown_block_with_whitespace():
    """
    Tests markdown block processing with leading/trailing whitespace.
    """
    input_md = "  Another test  "
    expected_output = "Processed: Another test"
    assert process_markdown_block(input_md) == expected_output


# Add more unit tests as functionalities are added to app_logic.py
