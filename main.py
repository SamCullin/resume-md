#!/usr/bin/env python3
import argparse
import os
import sys
from string import Template
from typing import cast

from component_factory import tokens_to_components
from components import ResumeBanner
from renderer import Renderer
from tokenizer import MarkdownTokenizer, read_markdown_file


def load_template(template_path: str = "template.html") -> Template:
    """
    Load the HTML template file

    Args:
        template_path: Path to the template file

    Returns:
        A string.Template object containing the template
    """
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            template_content = f.read()
            return Template(template_content)
    except FileNotFoundError:
        print(f"Error: Template file {template_path} was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while reading the template file: {e}")
        sys.exit(1)


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate HTML resume from markdown")
    parser.add_argument("--input", "-i", help="Path to input markdown file")
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Path to output HTML file (default: <input_name>.html)",
    )
    parser.add_argument(
        "--template",
        "-t",
        default="template.html",
        help="Path to HTML template file (default: template.html)",
    )
    args = parser.parse_args()

    # Set default output filename if not provided
    if args.output is None:
        input_base = os.path.splitext(os.path.basename(args.input))[0]
        args.output = f"{input_base}.html"

    try:
        # Read the markdown content
        markdown_text = read_markdown_file(args.input)

        # Tokenize the markdown
        tokenizer = MarkdownTokenizer(markdown_text)
        tokens = tokenizer.tokenize()

        # Convert tokens to components
        components = tokens_to_components(tokens)

        # Render components to HTML
        renderer = Renderer()
        rendered = renderer.render_components(components)

        # Load template
        template = load_template(args.template)

        # Get title from file name or first component
        title = (
            os.path.splitext(os.path.basename(args.input))[0].replace("_", " ").title()
        )
        banner = next(
            (c for c in components if c.get_component_type() == "banner"), None
        )
        if banner:
            resume_banner = cast(ResumeBanner, banner)
            title = f"{resume_banner.name} Resume"

        # Fill template with rendered HTML
        html_output = template.safe_substitute(
            title=title, header=rendered["header"], content=rendered["content"]
        )

        # Save HTML file
        with open(args.output, "w", encoding="utf-8") as file:
            file.write(html_output)

        print(f"HTML resume saved as: {args.output}")
        print(
            "Open this file in a browser and use the Print button or Ctrl+P to create a PDF"
        )

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
