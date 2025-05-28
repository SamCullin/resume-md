"""
Integration tests for ATS-info functionality
"""

from resume_md.component_factory import tokens_to_components
from resume_md.components import ATSInfoComponent
from resume_md.renderer import Renderer
from resume_md.tokenizer import MarkdownTokenizer


def test_ats_info_end_to_end():
    """Test complete ATS-info processing from markdown to HTML"""
    # Arrange
    markdown = """# John Doe
Email: john@example.com

[ats-info]: # Skills: Python, JavaScript
[ats-info]: # Tools: Git, Docker

## Experience
Some experience content."""

    # Act
    tokenizer = MarkdownTokenizer(markdown)
    tokens = tokenizer.tokenize()
    components = tokens_to_components(tokens)
    renderer = Renderer()
    rendered = renderer.render_components(components)

    # Assert
    # Check that ATS-info components were created
    ats_components = [c for c in components if isinstance(c, ATSInfoComponent)]
    assert len(ats_components) == 1
    assert ats_components[0].contents == [
        "Skills: Python, JavaScript",
        "Tools: Git, Docker",
    ]

    # Check that ATS-info is rendered in the HTML content
    content_html = rendered["content"]
    assert "Skills: Python, JavaScript" in content_html
    assert "Tools: Git, Docker" in content_html


def test_ats_info_component_rendering():
    """Test that ATS-info components render correctly"""
    # Arrange
    component = ATSInfoComponent(["Skills: Python, JavaScript, TypeScript"])
    renderer = Renderer()

    # Act
    html = renderer.render_ats_info(component)

    # Assert
    assert "Skills: Python, JavaScript, TypeScript" in html


def test_mixed_comments():
    """Test that ATS-info and page-break comments work together"""
    # Arrange
    markdown = """# Resume

[ats-info]: # Skills: Python
[page-break]: # 
[ats-info]: # Tools: Git

## Section 1
Content here."""

    # Act
    tokenizer = MarkdownTokenizer(markdown)
    tokens = tokenizer.tokenize()

    # Assert
    assert (
        len(tokens) == 6
    )  # heading, ats-info, page-break, ats-info, heading, paragraph
    assert tokens[1]["type"] == "ats-info"
    assert tokens[1]["contents"] == ["Skills: Python"]
    assert tokens[2]["type"] == "page-break"
    assert tokens[3]["type"] == "ats-info"
    assert tokens[3]["contents"] == ["Tools: Git"]


def test_ats_info_multiline_continuation():
    """Test that ATS-info supports multiline continuation with + syntax"""
    # Arrange
    markdown = """# Resume

[ats-info]: # Skills: Python, JavaScript
[ats-info]: # + React, Node.js
[ats-info]: # + Django, Flask

## Section 1
Content here."""

    # Act
    tokenizer = MarkdownTokenizer(markdown)
    tokens = tokenizer.tokenize()
    components = tokens_to_components(tokens)

    # Assert
    ats_components = [c for c in components if isinstance(c, ATSInfoComponent)]
    assert len(ats_components) == 1
    assert ats_components[0].contents == [
        "Skills: Python, JavaScript",
        "+ React, Node.js",
        "+ Django, Flask",
    ]
