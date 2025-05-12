#!/usr/bin/env python3
"""
Main entry point for resume-md package.
"""
import argparse
import os
import sys
import traceback
from importlib import resources
from string import Template

from .component_factory import tokens_to_components
from .renderer import Renderer
from .tokenizer import MarkdownTokenizer, read_markdown_file


def load_template(template_path: str | None = None) -> Template:
    """
    Load the HTML template file

    Args:
        template_path: Path to the template file. If None, use the built-in template.

    Returns:
        A string.Template object containing the template
    """
    if template_path is None:
        # Use the built-in template
        try:
            # Python 3.9+ only
            template_text = (
                resources.files("resume_md")
                .joinpath("template.html")
                .read_text(encoding="utf-8")
            )
            return Template(template_text)
        except Exception as e:
            print(f"Error loading built-in template: {e}")
            traceback.print_exc()
            sys.exit(1)
    else:
        # Load external template
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                template_content = f.read()
                return Template(template_content)
        except FileNotFoundError:
            print(f"Error: Template file {template_path} was not found.")
            sys.exit(1)
        except Exception as e:
            print(f"An error occurred while reading the template file: {e}")
            traceback.print_exc()
            sys.exit(1)


def main():

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Generate HTML resume from markdown",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    _ = parser.add_argument(
        "--input", "-i", default="resume.md", help="Path to input markdown file"
    )
    _ = parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Path to output HTML file (default: <input_name>.html)",
    )
    _ = parser.add_argument(
        "--template",
        "-t",
        default=None,
        help="Path to HTML template file (use built-in template if not specified)",
    )
    _ = parser.add_argument(
        "--version", "-v", action="store_true", help="Show version information and exit"
    )
    _ = parser.add_argument(
        "--debug", "-d", action="store_true", help="Show detailed debug information"
    )
    args = parser.parse_args()

    try:

        # Enable debug mode if requested
        debug_mode = args.debug

        # Show version and exit if requested
        if args.version:
            from . import __version__

            print(f"resume-md version {__version__}")
            sys.exit(0)

        # Set default output filename if not provided
        if args.output is None:
            input_base = os.path.splitext(os.path.basename(args.input))[0]
            args.output = f"{input_base}.html"

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
        if args.debug:
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
