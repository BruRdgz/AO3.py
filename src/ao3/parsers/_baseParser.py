from bs4 import BeautifulSoup, Tag
from typing import List, Dict, Optional, Any, Union
import re


class BaseParser:
    """
    Base class for AO3 HTML parsers.
    """

    def __init__(self, page: Union[BeautifulSoup, str]) -> None:
        self._soup = (
            page if isinstance(page, BeautifulSoup) else BeautifulSoup(page, "lxml")
        )

    def parse(self) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement parse()")

    def _get_text(self, selector: str, default: str = "") -> str:
        element = self._soup.select_one(selector)
        return element.text.strip() if element else default

    def _get_attribute(self, selector: str, attribute: str, default: str = "") -> str:
        element = self._soup.select_one(selector)
        return element.get(attribute, default) if element else default

    def _get_texts(self, selector: str) -> List[str]:
        elements = self._soup.select(selector)
        return [element.text.strip() for element in elements]

    def _extract_id_from_url(self, url: str, pattern: str) -> Optional[str]:
        match = re.search(pattern, url)
        return match.group(1) if match else None

    def _extract_count(self, text: str) -> int:
        if not text:
            return 0
        try:
            return int("".join(c for c in text if c.isdigit()))
        except ValueError:
            return 0
