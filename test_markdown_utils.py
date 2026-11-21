
from markdown_utils import validate_markdown


def test_valid_markdown():
    content = """
    ## Python Variables

    **Variables** store references to objects.

    ```python
    name = "Prakash"
    ```
    """

    assert validate_markdown(content) is True


def test_empty_markdown():
    assert validate_markdown("") is False


def test_whitespace_markdown():
    assert validate_markdown("   ") is False


def test_unclosed_code_block():
    content = """
    ```python
    print("Hello")
    """

    assert validate_markdown(content) is False


def test_non_string_content():
    assert validate_markdown(None) is False
