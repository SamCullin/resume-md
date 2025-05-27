from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


class ResumeComponent(ABC):
    """Base class for all resume components"""

    @abstractmethod
    def get_component_type(self) -> str:
        """Returns the type of the component"""


@dataclass
class ResumeBanner(ResumeComponent):
    """Header component for resume with name and contact information"""

    name: str
    contact_info: Optional[str] = None

    def get_component_type(self) -> str:
        return "banner"


@dataclass
class HeadingComponent(ResumeComponent):
    """Component for section and subsection headings"""

    level: int
    content: str

    def get_component_type(self) -> str:
        return "heading"


@dataclass
class ParagraphComponent(ResumeComponent):
    """Component for paragraph text"""

    content: str

    def get_component_type(self) -> str:
        return "paragraph"


@dataclass
class ListComponent(ResumeComponent):
    """Component for bullet points or numbered lists"""

    list_type: str  # 'ordered' or 'unordered'
    items: list[str]

    def get_component_type(self) -> str:
        return "list"


@dataclass
class TableComponent(ResumeComponent):
    """Component for structured tabular data"""

    headers: list[str]
    alignments: list[str]
    rows: list[list[str]]

    def get_component_type(self) -> str:
        return "table"


@dataclass
class PageBreakComponent(ResumeComponent):
    """Component for forcing a page break in the document"""

    def get_component_type(self) -> str:
        return "page-break"


@dataclass
class ATSInfoComponent(ResumeComponent):
    """Component for ATS-specific information that will be hidden from visual display but accessible to text extraction"""

    info_type: str  # e.g., "Skills", "Tools", etc.
    content: str  # The actual content/list

    def get_component_type(self) -> str:
        return "ats-info"
