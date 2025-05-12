import re
from typing import Dict, List, cast

from .components import (
    HeadingComponent,
    ListComponent,
    ParagraphComponent,
    ResumeBanner,
    ResumeComponent,
    TableComponent,
)


class Renderer:
    """
    Renderer class that handles HTML generation for resume components
    """

    def __init__(self):
        pass

    def format_inline_markdown(self, text: str) -> str:
        """
        Convert simple markdown formatting within text to HTML

        Args:
            text: Text with markdown formatting

        Returns:
            Text with HTML formatting
        """
        # Bold
        text = re.sub(r"\*\*(.*?)\*\*", r'<strong class="font-bold">\1</strong>', text)
        text = re.sub(r"__(.*?)__", r'<strong class="font-bold">\1</strong>', text)

        # Italic - For job dates/websites, add special styling
        text = re.sub(
            r"\*(.*?)\*", r'<em class="italic text-gray-500 text-sm">\1</em>', text
        )
        text = re.sub(
            r"_(.*?)_", r'<em class="italic text-gray-500 text-sm">\1</em>', text
        )

        # Code
        text = re.sub(
            r"`(.*?)`",
            r'<code class="bg-gray-100 text-pink-600 px-1 py-0.5 rounded text-sm">\1</code>',
            text,
        )

        # Links
        text = re.sub(
            r"\[(.*?)\]\((.*?)\)", r'<a href="\2" class="hover:underline">\1</a>', text
        )

        return text

    def render_banner(self, component: ResumeBanner) -> str:
        """
        Render a resume banner component to HTML

        Args:
            component: The banner component to render

        Returns:
            HTML string for the banner
        """
        inner_html = f'<div class="flex flex-row items-center justify-between w-full">'

        # Left side - Name/title
        inner_html += f'<div class="flex-shrink-0">'
        inner_html += f'<h1 class="text-2xl font-bold">{self.format_inline_markdown(component.name)}</h1>'
        inner_html += f"</div>"

        # Right side - Contact info
        if component.contact_info:
            inner_html += f'<div class="flex-shrink-0 ml-auto">'
            contact_html = self._build_contact_info(component.contact_info)
            inner_html += contact_html
            inner_html += f"</div>"

        inner_html += "</div>"

        # Create consistent header for both web and print
        return f"""
        <div class="w-full bg-primary text-white print:px-[1cm] px-8 py-2">
            {inner_html}
        </div>  
        """

    def _build_contact_info(self, contact_info: str) -> str:
        """
        Build HTML for contact information

        Args:
            contact_info: Contact information string

        Returns:
            HTML string for contact info
        """
        # Format contact info in a right-aligned block with items on separate lines
        contact_html = (
            '<div class="mx-auto text-right contact-info" style="text-align: right;">'
        )

        # Process all contact items (Email, Mobile, LinkedIn, etc.)
        # Find all markdown links in the format [text](link)
        link_items = re.findall(r"\s*\**(.*?):\**\s*\[(.*?)\]\((.*?)\)", contact_info)
        for item_text, link_text, link_url in link_items:
            item_text = item_text.strip()
            link_text = link_text.strip()
            link_url = link_url.strip()
            contact_html += f'<div class="contact-item text-right" style="text-align: right;"><strong class="font-bold">{item_text}:</strong> <a href="{link_url}" class="hover:underline">{link_text}</a></div>'

        contact_html += "</div>"

        return contact_html

    def render_heading(self, component: HeadingComponent) -> str:
        """
        Render a heading component to HTML

        Args:
            component: The heading component to render

        Returns:
            HTML string for the heading
        """
        if component.level == 1:
            # H1 - Main title/name
            return f'<h{component.level} class="text-2xl font-bold text-primary mb-3">{self.format_inline_markdown(component.content)}</h{component.level}>'
        elif component.level == 2:
            return f'<h{component.level} class="text-xl font-bold text-primary mb-2 pb-1 pt-2 border-b border-gray-300">{self.format_inline_markdown(component.content)}</h{component.level}>'
        elif component.level == 3:
            # H3 - Company/organization names
            return f'<h{component.level} class="text-base font-bold text-primary mt-2 mb-1">{self.format_inline_markdown(component.content)}</h{component.level}>'
        elif component.level == 4:
            # H4 - Job titles
            return f'<h{component.level} class="text-sm font-semibold text-gray-800 mt-1 mb-1">{self.format_inline_markdown(component.content)}</h{component.level}>'
        elif component.level == 5:
            # H5 - Dates/locations
            return f'<h{component.level} class="text-xs font-semibold text-gray-800 mt-1 mb-1">{self.format_inline_markdown(component.content)}</h{component.level}>'
        elif component.level == 6:
            # H6 - Smallest heading
            return f'<h{component.level} class="text-xs italic font-medium text-gray-700 mt-1 mb-1">{self.format_inline_markdown(component.content)}</h{component.level}>'
        else:
            # Fallback for any other level (shouldn't happen with markdown's 6 levels)
            return f'<h{component.level} class="font-bold mt-4 mb-2">{self.format_inline_markdown(component.content)}</h{component.level}>'

    def render_paragraph(self, component: ParagraphComponent) -> str:
        """
        Render a paragraph component to HTML

        Args:
            component: The paragraph component to render

        Returns:
            HTML string for the paragraph
        """
        content = component.content
        return f'<p class="my-2">{self.format_inline_markdown(content)}</p>'

    def render_list(self, component: ListComponent) -> str:
        """
        Render a list component to HTML

        Args:
            component: The list component to render

        Returns:
            HTML string for the list
        """
        tag = "ul" if component.list_type == "unordered" else "ol"
        list_class = (
            "list-disc pl-5 my-2 space-y-1"
            if component.list_type == "unordered"
            else "list-decimal pl-5 my-2 space-y-1"
        )

        items_html = ""
        for item in component.items:
            formatted_item = self.format_inline_markdown(item)
            items_html += f'<li class="mb-1.5">{formatted_item}</li>'

        return f'<{tag} class="{list_class} mb-4">{items_html}</{tag}>'

    def render_table(self, component: TableComponent) -> str:
        """
        Render a table component to HTML

        Args:
            component: The table component to render

        Returns:
            HTML string for the table
        """
        thead = "<thead><tr>"
        for i, header in enumerate(component.headers):
            align_class = "text-left"
            if i < len(component.alignments):
                if component.alignments[i] == "center":
                    align_class = "text-center"
                elif component.alignments[i] == "right":
                    align_class = "text-right"

            thead += f'<th class="bg-primary bg-opacity-10 text-primary font-semibold {align_class} p-1 print:bg-primary print:bg-opacity-10">{self.format_inline_markdown(header)}</th>'
        thead += "</tr></thead>"

        tbody = "<tbody>"
        for row in component.rows:
            tbody += "<tr>"
            for i, cell in enumerate(row):
                align_class = "text-left"
                if i < len(component.alignments):
                    if component.alignments[i] == "center":
                        align_class = "text-center"
                    elif component.alignments[i] == "right":
                        align_class = "text-right"

                tbody += f'<td class="border border-gray-200 p-1 {align_class}">{self.format_inline_markdown(cell)}</td>'
            tbody += "</tr>"
        tbody += "</tbody>"

        return f'<table class="w-full border-collapse my-2 mb-4">{thead}{tbody}</table>'

    def render_component(self, component: ResumeComponent) -> str:
        """
        Render any resume component to HTML based on its type

        Args:
            component: The component to render

        Returns:
            HTML string for the component
        """
        component_type = component.get_component_type()

        if component_type == "banner":
            return self.render_banner(cast(ResumeBanner, component))
        elif component_type == "heading":
            return self.render_heading(cast(HeadingComponent, component))
        elif component_type == "paragraph":
            return self.render_paragraph(cast(ParagraphComponent, component))
        elif component_type == "list":
            return self.render_list(cast(ListComponent, component))
        elif component_type == "table":
            return self.render_table(cast(TableComponent, component))
        else:
            raise ValueError(f"Unknown component type: {component_type}")

    def render_components(self, components: List[ResumeComponent]) -> Dict[str, str]:
        """
        Render all components to HTML and separate the banner and content

        Args:
            components: List of resume components

        Returns:
            Dictionary with 'header' and 'content' HTML strings
        """
        header_html = ""
        content_html = []

        # Extract banner component if it exists
        resume_banner = next(
            (c for c in components if c.get_component_type() == "banner"), None
        )
        if resume_banner:
            header_html = self.render_banner(cast(ResumeBanner, resume_banner))
            components = [c for c in components if c != resume_banner]

        # Render remaining components
        for component in components:
            content_html.append(self.render_component(component))

        return {"header": header_html, "content": "\n".join(content_html)}
