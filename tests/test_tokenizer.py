"""
Tests for markdown tokenizer functionality
"""

from resume_md.tokenizer import MarkdownTokenizer


def test_heading_tokenization():
    """Test that headings are properly tokenized"""
    # Arrange
    markdown = "# Heading 1\n## Heading 2"
    tokenizer = MarkdownTokenizer(markdown)

    # Act
    tokens = tokenizer.tokenize()

    # Assert
    assert len(tokens) == 2
    assert tokens[0]["type"] == "heading"
    assert tokens[0]["level"] == 1
    assert tokens[0]["content"] == "Heading 1"
    assert tokens[1]["type"] == "heading"
    assert tokens[1]["level"] == 2
    assert tokens[1]["content"] == "Heading 2"


def test_paragraph_tokenization():
    """Test that paragraphs are properly tokenized"""
    # Arrange
    markdown = "This is a paragraph.\nIt has multiple lines."
    tokenizer = MarkdownTokenizer(markdown)

    # Act
    tokens = tokenizer.tokenize()

    # Assert
    assert len(tokens) == 1
    assert tokens[0]["type"] == "paragraph"
    assert tokens[0]["content"] == "This is a paragraph. It has multiple lines."


def test_list_tokenization():
    """Test that lists are properly tokenized"""
    # Arrange
    markdown = "* Item 1\n* Item 2\n* Item 3"
    tokenizer = MarkdownTokenizer(markdown)

    # Act
    tokens = tokenizer.tokenize()

    # Assert
    assert len(tokens) == 1
    assert tokens[0]["type"] == "list"
    assert tokens[0]["list_type"] == "unordered"
    assert len(tokens[0]["items"]) == 3
    assert tokens[0]["items"][0] == "Item 1"
    assert tokens[0]["items"][1] == "Item 2"
    assert tokens[0]["items"][2] == "Item 3"
