from . import BaseParser
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime


class WorkParser(BaseParser):
    """Parser for AO3 work pages.

    This parser extracts metadata from AO3 work/story pages.
    """

    def parse(self) -> Dict[str, Any]:
        """Parse the work page and return structured data."""
        return {
            "title": self._fetch_title(),
            "author": self._fetch_authors(),
            "summary": self._fetch_summary(),
            "language": self._fetch_language(),
            "words": self._fetch_word_count(),
            "chapters_published": self._fetch_chapters_published(),
            "chapters_expected": self._fetch_chapters_expected(),
            "is_completed": self._fetch_is_completed(),
            "kudos": self._fetch_kudos(),
            "comments": self._fetch_comments(),
            "bookmarks": self._fetch_bookmarks(),
            "hits": self._fetch_hits(),
            "published": self._fetch_published_date(),
            "updated": self._fetch_updated_date(),
            "tags": self._fetch_tags(),
            "relationships": self._fetch_relationships(),
            "characters": self._fetch_characters(),
            "fandoms": self._fetch_fandoms(),
            "categories": self._fetch_categories(),
            "ratings": self._fetch_ratings(),
            "warnings": self._fetch_warnings(),
            "series": self._fetch_series(),
            "is_restricted": self._fetch_is_restricted(),
        }

    def _fetch_title(self) -> str:
        """Extract the work title from the page."""
        return self._get_text("h2.title")

    def _fetch_authors(self) -> str:
        """Extract the work author(s) from the page."""
        authors = self._get_texts("a[rel='author']")
        return ", ".join(authors) if authors else "Anonymous"

    def _fetch_summary(self) -> Optional[str]:
        """Extract the work summary."""
        summary_div = self._soup.select_one("div.summary .userstuff")
        if not summary_div:
            return None
        return summary_div.text.strip()

    def _fetch_language(self) -> str:
        """Extract the work language."""
        language_text = self._get_text("dd.language")
        return language_text

    def _fetch_word_count(self) -> int:
        """Extract the work word count."""
        words_text = self._get_text("dd.words")
        return self._extract_count(words_text)

    def _fetch_chapters_published(self) -> int:
        """Extract the number of published chapters."""
        chapters_text = self._get_text("dd.chapters")
        if "/" in chapters_text:
            published = chapters_text.split("/")[0].strip()
            return self._extract_count(published)
        return 1

    def _fetch_chapters_expected(self) -> Optional[int]:
        """Extract the expected total number of chapters."""
        chapters_text = self._get_text("dd.chapters")
        if "/" in chapters_text:
            expected = chapters_text.split("/")[1].strip()
            if expected.lower() == "?" or expected.lower() == "∞":
                return None
            return self._extract_count(expected)
        return None

    def _fetch_is_completed(self) -> bool:
        """Determine if the work is marked as complete."""
        chapters_text = self._get_text("dd.chapters")
        if "/" in chapters_text:
            published, expected = chapters_text.split("/")
            # Work is complete if published chapters equals expected chapters
            # or if single chapter work
            if published.strip() == expected.strip() and expected.strip() != "?":
                return True
        return "complete" in self._get_text("dl.stats").lower()

    def _fetch_kudos(self) -> int:
        """Extract the number of kudos."""
        kudos_text = self._get_text("dd.kudos")
        return self._extract_count(kudos_text)

    def _fetch_comments(self) -> int:
        """Extract the number of comments."""
        comments_text = self._get_text("dd.comments")
        return self._extract_count(comments_text)

    def _fetch_bookmarks(self) -> int:
        """Extract the number of bookmarks."""
        bookmarks_text = self._get_text("dd.bookmarks")
        return self._extract_count(bookmarks_text)

    def _fetch_hits(self) -> int:
        """Extract the number of hits."""
        hits_text = self._get_text("dd.hits")
        return self._extract_count(hits_text)

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse a date string into a datetime object."""
        if not date_str:
            return None
        try:
            # AO3 date format is typically: YYYY-MM-DD
            return datetime.strptime(date_str.strip(), "%Y-%m-%d")
        except ValueError:
            return None

    def _fetch_published_date(self) -> Optional[datetime]:
        """Extract the publication date."""
        date_text = self._get_text("dd.published")
        return self._parse_date(date_text)

    def _fetch_updated_date(self) -> Optional[datetime]:
        """Extract the last updated date."""
        date_text = self._get_text("dd.status")
        return self._parse_date(date_text)

    def _fetch_tags(self) -> List[str]:
        """Extract additional/freeform tags."""
        return self._get_texts("dd.freeform ul.commas li a")

    def _fetch_relationships(self) -> List[Tuple[str, str]]:
        """Extract character relationships in the work.

        Parses relationship tags like "Character A/Character B" or "Character A & Character B".

        Returns
        --------
        List[Tuple[:class:`str`, :class:`str`]]
            List of character relationship tuples
        """
        rel_tags = self._get_texts("dd.relationship ul.commas li a")
        relationships = []

        for tag in rel_tags:
            if "/" in tag:
                parts = tag.split("/", 1)  # Split only on first occurrence
                relationships.append((parts[0].strip(), parts[1].strip()))
            # Handle platonic relationships (&)
            elif "&" in tag:
                parts = tag.split("&", 1)  # Split only on first occurrence
                relationships.append((parts[0].strip(), parts[1].strip()))
            else:
                # If no relationship separator is found, use empty string as second element
                relationships.append((tag, ""))

        return relationships

    def _fetch_characters(self) -> List[str]:
        """Extract character tags."""
        return self._get_texts("dd.character ul.commas li a")

    def _fetch_fandoms(self) -> List[str]:
        """Extract fandom tags."""
        return self._get_texts("dd.fandom ul.commas li a")

    def _fetch_categories(self) -> List[str]:
        """Extract category tags."""
        return self._get_texts("dd.category ul.commas li a")

    def _fetch_ratings(self) -> List[str]:
        """Extract rating tags."""
        return self._get_texts("dd.rating ul.commas li a")

    def _fetch_warnings(self) -> List[str]:
        """Extract warning tags."""
        return self._get_texts("dd.warning ul.commas li a")

    def _fetch_series(self) -> Optional[str]:
        """Extract series information if present."""
        position_span = self._soup.select_one("dd.series span.position")
        if position_span:
            series_link = position_span.select_one("a")
            if series_link:
                return series_link.text.strip()

        # Fallback: try other potential selectors
        series_element = self._soup.select_one("dd.series a:not(.previous):not(.next)")
        if series_element:
            return series_element.text.strip()

        return None

    def _fetch_is_restricted(self) -> bool:
        """Determine if the work has restricted access."""
        # Check for common indicators of restricted content
        warnings = self._fetch_warnings()
        restricted_indicators = ["restricted", "explicit", "mature", "not rated"]

        title_class = self._get_attribute("h2.title", "class", "")
        if "restricted" in title_class:
            return True

        for warning in warnings:
            if any(
                indicator.lower() in warning.lower()
                for indicator in restricted_indicators
            ):
                return True

        return False
