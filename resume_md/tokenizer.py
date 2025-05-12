import re
from typing import Any, Dict, List


class MarkdownTokenizer:
    """
    A simple Markdown tokenizer that converts markdown text into structured tokens.
    """

    markdown: str
    tokens: List[Dict[str, Any]]
    current_position: int

    def __init__(self, markdown_text: str):
        self.markdown = markdown_text
        self.tokens = []
        self.current_position = 0

    def tokenize(self) -> List[Dict[str, Any]]:
        lines = self.markdown.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i]

            # Skip empty lines
            if not line.strip():
                i += 1
                continue

            # Headers (ATX style)
            header_match = re.match(r"^(#{1,6})\s+(.*?)(?:\s+#+)?$", line)
            if header_match:
                level = len(header_match.group(1))
                content = header_match.group(2).strip()
                self.tokens.append(
                    {"type": "heading", "level": level, "content": content}
                )
                i += 1
                continue

            # Tables
            # Check if this might be a table header
            if (
                "|" in line
                and i + 1 < len(lines)
                and "|" in lines[i + 1]
                and re.match(r"^[\s|:*-]+$", lines[i + 1])
            ):
                headers = [cell.strip() for cell in line.strip("|").split("|")]
                separator = [
                    cell.strip() for cell in lines[i + 1].strip("|").split("|")
                ]

                # Table alignment based on separator
                alignments: List[str] = []
                for sep in separator:
                    if sep.startswith(":") and sep.endswith(":"):
                        alignments.append("center")
                    elif sep.endswith(":"):
                        alignments.append("right")
                    else:
                        alignments.append("left")

                rows: List[List[str]] = []
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
                continue

            # Lists
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

                self.tokens.append(
                    {"type": "list", "list_type": list_type, "items": items}
                )
                continue

            # Paragraphs (including line breaks)
            paragraph_content = [line]
            i += 1
            while (
                i < len(lines)
                and lines[i].strip()
                and not any(
                    [
                        re.match(r"^#{1,6}\s+", lines[i]),  # No headers
                        re.match(r"^(\s*)([*+-]|\d+\.)\s+", lines[i]),  # No lists
                        "|" in lines[i]
                        and i + 1 < len(lines)
                        and re.match(r"^[\s|:*-]+$", lines[i + 1]),  # No tables
                    ]
                )
            ):
                paragraph_content.append(lines[i])
                i += 1

            self.tokens.append(
                {"type": "paragraph", "content": " ".join(paragraph_content)}
            )

        return self.tokens


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
