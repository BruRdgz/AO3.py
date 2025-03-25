"""
Base parser class for all parsers
"""

from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup


class BaseParser:
    def __init__(
        self,
        page: str | BeautifulSoup,
    ) -> None:
        self.soup = (
            page if isinstance(page, BeautifulSoup) else BeautifulSoup(page, "lxml")
        )

    def parse(self) -> dict[str, Any]:
        raise NotImplementedError(
            "The 'parse' method must be implemented by the subclass."
        )

    def _get_text(self, selector: str, default: str = "") -> str:
        element = self.soup.select_one(selector)
        return element.text.strip() if element else default

    def _get_texts(self, selector: str, default: list[str] = []) -> list[str]:
        elements = self.soup.select(selector)
        return [element.text.strip() for element in elements] if elements else default

    def _get_attribute(self, selector: str, attribute: str, default: str = "") -> str:
        element = self.soup.select_one(selector)
        return element.get(attribute) if element else default

    def _extract_count(self, text: str) -> int:
        if not text:
            return 0
        try:
            return int("".join(c for c in text if c.isdigit()))
        except ValueError:
            return 0
