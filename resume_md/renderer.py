import re
from typing import cast

from resume_md.components import (
    ATSInfoComponent,
    HeadingComponent,
    ListComponent,
    PageBreakComponent,
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

    def _clean_for_html(self, text: str) -> str:
        """
        Clean text for HTML rendering
        """
        return text.replace("&", "and").replace(" ", "-")

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

        # Links - Add proper link attributes for ATS parsing
        text = re.sub(
            r"\[(.*?)\]\((.*?)\)",
            r'<a href="\2" class="hover:underline" rel="noopener" title="\1">\1</a>',
            text,
        )

        return text

    def render_banner(self, component: ResumeBanner) -> str:
        """
        Render a resume banner component to HTML using semantic header element

        Args:
            component: The banner component to render

        Returns:
            HTML string for the banner
        """
        # Use semantic header element instead of div
        inner_html = f'<section class="flex flex-col sm:flex-row items-start sm:items-center w-full">'

        # Name section with proper heading
        inner_html += f'<div class="flex-shrink-0 text-left">'
        inner_html += f'<h1 class="text-2xl font-bold" itemprop="name">{self.format_inline_markdown(component.name)}</h1>'
        inner_html += f"</div>"

        # Contact info using semantic address element
        if component.contact_info:
            inner_html += f'<div class="flex-shrink-0 mt-2 sm:mt-0 sm:ml-auto">'
            contact_html = self._build_contact_info(component.contact_info)
            inner_html += contact_html
            inner_html += f"</div>"

        inner_html += "</section>"

        # Create semantic header with microdata
        return f"""
        <header class="w-full bg-primary text-white print:px-[1cm] px-8 py-2" itemscope itemtype="https://schema.org/Person">
            {inner_html}
        </header>  
        """

    def _build_contact_info(self, contact_info: str) -> str:
        """
        Build semantic HTML for contact information using address element

        Args:
            contact_info: Contact information string

        Returns:
            HTML string for contact info with proper semantic markup
        """
        # Use semantic address element for contact info
        contact_html = [
            '<address class="contact-info text-left sm:text-right not-italic">'
        ]

        # Process all contact items with proper microdata
        # First handle linked items
        link_regex = r"\s*\**(.*?):\**\s*\[(.*?)\]\((.*?)\)"
        link_items: list[tuple[str, str, str]] = re.findall(link_regex, contact_info)
        for item_text, link_text, link_url in link_items:
            item_text = item_text.strip()
            link_text = link_text.strip()
            link_url = link_url.strip()
            item_type = self._clean_for_html(item_text)
            contact_html.append(
                f'<div class="contact-item" data-contact-type="{item_type}"><strong class="font-bold">{item_text}:</strong><span class="contact-separator"> </span><a href="{link_url}" class="hover:underline" rel="noopener">{link_text}</a></div>'
            )

        # Then handle plain text items
        plain_items: list[tuple[str, str]] = re.findall(
            r"\s*\**(.*?):\**\s*([^\[]+?)(?=\s*\*\*|$)", contact_info
        )
        for item_text, content in plain_items:
            # Skip if this item was already handled as a link
            if re.match(link_regex, f"**{item_text}:** {content}"):
                continue
            item_text = item_text.strip()
            content = content.strip()
            item_type = self._clean_for_html(item_text)
            contact_html.append(
                f'<div class="contact-item" data-contact-type="{item_type}"><strong class="font-bold">{item_text}:</strong><span class="contact-separator"> </span><span>{content}</span></div>'
            )

        contact_html.append("</address>")
        return "\n".join(contact_html)

    def render_heading(self, component: HeadingComponent) -> str:
        """
        Render a heading component to HTML with proper semantic attributes

        Args:
            component: The heading component to render

        Returns:
            HTML string for the heading
        """
        # Add semantic attributes for section identification
        if component.level == 1:
            # H1 - Main title/name
            return f'<h{component.level} class="text-2xl font-bold text-primary mb-3" itemprop="name">{self.format_inline_markdown(component.content)}</h{component.level}>'
        elif component.level == 2:
            # H2 - Main sections (Profile, Experience, Education, etc.)
            section_id = self._clean_for_html(component.content)
            return f'<h{component.level} class="text-xl font-bold text-primary mb-2 pb-1 pt-1 border-b border-gray-300" id="{section_id}" role="heading" aria-level="2">{self.format_inline_markdown(component.content)}</h{component.level}>'
        elif component.level == 3:
            # H3 - Company/organization names
            return f'<h{component.level} class="text-base font-bold text-primary mt-1 mb-1" itemprop="worksFor" itemscope itemtype="https://schema.org/Organization"><span itemprop="name">{self.format_inline_markdown(component.content)}</span></h{component.level}>'
        elif component.level == 4:
            # H4 - Job titles
            return f'<h{component.level} class="text-sm font-semibold text-gray-800 mt-1 mb-1" itemprop="jobTitle">{self.format_inline_markdown(component.content)}</h{component.level}>'
        elif component.level == 5:
            # H5 - Dates/locations
            return f'<h{component.level} class="text-xs font-semibold text-gray-800 mt-1 mb-1"><time>{self.format_inline_markdown(component.content)}</time></h{component.level}>'
        elif component.level == 6:
            # H6 - Smallest heading
            return f'<h{component.level} class="text-xs italic font-medium text-gray-700 mt-1 mb-1">{self.format_inline_markdown(component.content)}</h{component.level}>'
        else:
            # Fallback for any other level
            return f'<h{component.level} class="font-bold mt-1 mb-1">{self.format_inline_markdown(component.content)}</h{component.level}>'

    def render_paragraph(self, component: ParagraphComponent) -> str:
        """
        Render a paragraph component to HTML

        Args:
            component: The paragraph component to render

        Returns:
            HTML string for the paragraph
        """
        content = component.content
        return f'<p class="my-1">{self.format_inline_markdown(content)}</p>'

    def render_list(self, component: ListComponent) -> str:
        """
        Render a list component to HTML with proper semantic attributes

        Args:
            component: The list component to render

        Returns:
            HTML string for the list
        """
        tag = "ul" if component.list_type == "unordered" else "ol"
        # Use custom class without default bullets since we're adding our own
        list_class = (
            "pl-5 my-2 space-y-1 custom-bullet-list"
            if component.list_type == "unordered"
            else "pl-5 my-2 space-y-1 custom-number-list"
        )

        items_html = []
        for item in component.items:
            formatted_item = self.format_inline_markdown(item)
            # Add bullet symbol for better text extraction
            items_html.append(
                f'<li class="mb-1.5 list-item-with-bullet" role="listitem" data-bullet="• ">{formatted_item}</li>'
            )

        # Add semantic role and proper accessibility attributes
        joined_items = "\n".join(items_html)
        return f'<{tag} class="{list_class} mb-2" role="list">{joined_items}</{tag}>'

    def render_table(self, component: TableComponent) -> str:
        """
        Render a table component to HTML

        Args:
            component: The table component to render

        Returns:
            HTML string for the table
        """
        thead_html: list[str] = []
        thead_html.append("<thead><tr>")
        for i, header in enumerate(component.headers):
            align_class = "text-left"
            if i < len(component.alignments):
                if component.alignments[i] == "center":
                    align_class = "text-center"
                elif component.alignments[i] == "right":
                    align_class = "text-right"

            thead_html.append(
                f'<th class="bg-primary bg-opacity-10 text-primary font-semibold {align_class} p-1 print:bg-primary print:bg-opacity-10">{self.format_inline_markdown(header)}</th>'
            )
        thead_html.append("</tr></thead>")

        tbody_html: list[str] = []
        tbody_html.append("<tbody>")
        for row in component.rows:
            row_html: list[str] = []
            row_html.append("<tr>")
            for i, cell in enumerate(row):
                align_class = "text-left"
                if i < len(component.alignments):
                    if component.alignments[i] == "center":
                        align_class = "text-center"
                    elif component.alignments[i] == "right":
                        align_class = "text-right"
                header = component.headers[i]
                row_html.append(
                    f"""<td class="border border-gray-200 p-1 {align_class}" data-field="{header.lower()}" data-label="{header}">
                    <span class="ats-visible">&nbsp;{header}:&nbsp;</span>
                   {self.format_inline_markdown(cell)}
                </td>"""
                )
            row_html.append("</tr>")
            tbody_html.append("\n".join(row_html))
        tbody_html.append("</tbody>")
        joined_head = "\n".join(thead_html)
        joined_body = "\n".join(tbody_html)
        return f'<table class="w-full border-collapse my-2">{joined_head}{joined_body}</table>'

    def _strip_html(self, text: str) -> str:
        """Helper method to strip HTML tags from text"""
        import re

        clean = re.compile("<.*?>")
        return re.sub(clean, "", text)

    def render_page_break(self, component: PageBreakComponent) -> str:
        """
        Render a page break component to HTML

        Args:
            component: The page break component to render

        Returns:
            HTML string for the page break
        """
        return (
            '<div class="break-after-page" role="separator" aria-hidden="true"></div>'
        )

    def render_ats_info(self, component: ATSInfoComponent) -> str:
        """
        Render an ATS-info component to HTML that is hidden from visual display but accessible to text extraction

        Args:
            component: The ATS-info component to render

        Returns:
            HTML string for the ATS info that's hidden but extractable
        """
        # Create a hidden aside that ATS systems can read but users can't see
        # Using white text with tiny font size and line height
        content_lines: list[str] = []
        for content in component.contents:
            content_lines.append(f'<p class="p-0 m-0">{content}</p>')

        content_html = "\n".join(content_lines)

        return f"""<aside class="p-0 m-0 text-white selection:text-white" style="font-size: 1px; line-height: 0.1px;">
            {content_html}
        </aside>"""

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
        elif component_type == "page-break":
            return self.render_page_break(cast(PageBreakComponent, component))
        elif component_type == "ats-info":
            return self.render_ats_info(cast(ATSInfoComponent, component))
        else:
            raise ValueError(f"Unknown component type: {component_type}")

    def render_components(self, components: list[ResumeComponent]) -> dict[str, str]:
        """
        Render all components to HTML and separate the banner and content with semantic structure

        Args:
            components: List of resume components

        Returns:
            dictionary with 'header' and 'content' HTML strings
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

        # Wrap content in semantic sections
        current_section = []
        section_components = []

        for component in components:
            if (
                component.get_component_type() == "heading"
                and cast(HeadingComponent, component).level == 2
            ):
                # Start new section
                if current_section:
                    section_components.append(current_section)
                current_section = [component]
            else:
                current_section.append(component)

        # Add the last section
        if current_section:
            section_components.append(current_section)

        # Render sections with semantic markup
        for section in section_components:
            if section:
                section_html = []

                # Find the first heading component to use as section header
                header = None
                header_index = 0
                for i, component in enumerate(section):
                    if component.get_component_type() == "heading":
                        header = component
                        header_index = i
                        break

                if header:
                    section_id = self._clean_for_html(
                        cast(HeadingComponent, header).content
                    )
                    section_html.append(f'<section role="region" id="{section_id}">')

                    # Render any components before the heading
                    for component in section[:header_index]:
                        section_html.append(self.render_component(component))

                    # Render the heading
                    section_html.append(self.render_component(header))
                    section_html.append("<article>")

                    # Render components after the heading
                    for component in section[header_index + 1 :]:
                        section_html.append(self.render_component(component))

                    section_html.append("</article>")
                    section_html.append("</section>")
                else:
                    # No heading found, render all components without section wrapper
                    for component in section:
                        section_html.append(self.render_component(component))

                content_html.extend(section_html)

        return {"header": header_html, "content": "\n".join(content_html)}
