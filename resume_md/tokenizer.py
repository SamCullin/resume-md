import re
from typing import Any


class MarkdownTokenizer:
    """
    A simple Markdown tokenizer that converts markdown text into structured tokens.
    """

    markdown: str
    tokens: list[dict[str, Any]]
    current_position: int

    def __init__(self, markdown_text: str):
        self.markdown = markdown_text
        self.tokens = []
        self.current_position = 0

    def tokenize(self) -> list[dict[str, Any]]:
        lines = self.markdown.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i]

            # Skip empty lines
            if not line.strip():
                i += 1
                continue

            # Process different markdown elements
            if self._is_header(line):
                i = self._process_header(lines, i)
            elif self._is_table(lines, i):
                i = self._process_table(lines, i)
            elif self._is_list_item(line):
                i = self._process_list(lines, i)
            else:
                i = self._process_paragraph(lines, i)

        return self.tokens

    def _is_header(self, line: str) -> bool:
        """Check if the line is a header."""
        return bool(re.match(r"^(#{1,6})\s+(.*?)(?:\s+#+)?$", line))

    def _process_header(self, lines: list[str], i: int) -> int:
        """Process a header line and add it to tokens."""
        line = lines[i]
        header_match = re.match(r"^(#{1,6})\s+(.*?)(?:\s+#+)?$", line)
        if header_match:
            level = len(header_match.group(1))
            content = header_match.group(2).strip()
            self.tokens.append({"type": "heading", "level": level, "content": content})
        return i + 1

    def _is_table(self, lines: list[str], i: int) -> bool:
        """Check if the current position contains a table."""
        return (
            i + 1 < len(lines)
            and "|" in lines[i]
            and "|" in lines[i + 1]
            and bool(re.match(r"^[\s|:*-]+$", lines[i + 1]))
        )

    def _process_table(self, lines: list[str], i: int) -> int:
        """Process a table and add it to tokens."""
        headers = [cell.strip() for cell in lines[i].strip("|").split("|")]
        separator = [cell.strip() for cell in lines[i + 1].strip("|").split("|")]

        # Table alignment based on separator
        alignments: list[str] = []
        for sep in separator:
            if sep.startswith(":") and sep.endswith(":"):
                alignments.append("center")
            elif sep.endswith(":"):
                alignments.append("right")
            else:
                alignments.append("left")

        rows: list[list[str]] = []
        i += 2  # Skip header and separator

        # Parse table rows
        while i < len(lines) and "|" in lines[i]:
            cells = [cell.strip() for cell in lines[i].strip("|").split("|")]
            rows.append(cells)
            i += 1

        self.tokens.append(
            {
                "type": "table",
                "headers": headers,
                "alignments": alignments,
                "rows": rows,
            }
        )
        return i

    def _is_list_item(self, line: str) -> bool:
        """Check if the line is a list item."""
        return bool(re.match(r"^(\s*)([*+-]|\d+\.)\s+(.*?)$", line))

    def _process_list(self, lines: list[str], i: int) -> int:
        """Process a list and add it to tokens."""
        line = lines[i]
        list_match = re.match(r"^(\s*)([*+-]|\d+\.)\s+(.*?)$", line)
        if list_match:
            indent = len(list_match.group(1))
            list_type = "unordered" if list_match.group(2) in "*+-" else "ordered"
            content = list_match.group(3).strip()

            items = [content]
            i += 1

            # Collect items of the same list
            while i < len(lines):
                next_match = re.match(r"^(\s*)([*+-]|\d+\.)\s+(.*?)$", lines[i])
                if next_match and len(next_match.group(1)) == indent:
                    items.append(next_match.group(3).strip())
                    i += 1
                else:
                    break

            self.tokens.append({"type": "list", "list_type": list_type, "items": items})
        return i

    def _process_paragraph(self, lines: list[str], i: int) -> int:
        """Process a paragraph and add it to tokens."""
        paragraph_content = [lines[i]]
        i += 1
        while (
            i < len(lines)
            and lines[i].strip()
            and not self._is_header(lines[i])
            and not self._is_list_item(lines[i])
            and not self._is_table(lines, i)
        ):
            paragraph_content.append(lines[i])
            i += 1

        self.tokens.append(
            {"type": "paragraph", "content": " ".join(paragraph_content)}
        )
        return i


def read_markdown_file(file_path: str) -> str:
    """
    Function to read the markdown file.

    Args:
        file_path: Path to the markdown file

    Returns:
        The contents of the markdown file as a string
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: The file {file_path} was not found.")
    except Exception as e:
        raise Exception(f"An error occurred while reading the file: {e}")
