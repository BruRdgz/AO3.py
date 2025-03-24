"""
Module for classes representing works on ArchiveOfOurOwn.org.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any

from requests import HTTPError

from ao3.client import Client
from ao3.parsers import WorkParser


__all__ = ["ArchiveWork"]


@dataclass
class _ArchiveData:
    ID: str
    title: str = ""
    author: str = "Anonymous"
    link: str = ""

    summary: Optional[str] = None
    language: str = ""
    words: int = 0
    chapters_published: int = 0
    chapters_expected: Optional[int] = None
    is_completed: bool = False

    kudos: int = 0
    comments: int = 0
    bookmarks: int = 0
    hits: int = 0

    published: Optional[datetime] = None
    updated: Optional[datetime] = None

    tags: list[str] = None
    relationships: list[tuple[str, str]] = None
    characters: list[str] = None
    fandoms: list[str] = None
    categories: list[str] = None
    ratings: list[str] = None
    warnings: list[str] = None

    series: Optional[str] = None
    is_restricted: bool = False

    def __post_init__(self):
        """Initialize default values for the dataclass."""
        if self.tags is None:
            self.tags = []
        if self.relationships is None:
            self.relationships = []
        if self.characters is None:
            self.characters = []
        if self.fandoms is None:
            self.fandoms = []
        if self.categories is None:
            self.categories = []
        if self.ratings is None:
            self.ratings = []
        if self.warnings is None:
            self.warnings = []

    @classmethod
    def from_dictionary(cls, data: dict[str, Any]) -> _ArchiveData:
        return cls(**data)


class ArchiveWork:
    """
    A work within ArchiveOfOurOwn.org.
    """

    def __init__(
        self,
        work_id: str,
        session: Optional[Client] = None,
        lazy: bool = True,
    ) -> None:
        self._id = work_id
        self._session = session if session else Client()
        self._data: Optional[_ArchiveData] = None
        self._is_loaded = False
        if not lazy:
            self.reload()

    def reload(self) -> None:
        """Fetch and load work data from AO3."""
        try:
            response = self._session.fetch(f"/works/{self._id}", soup=True)
        except HTTPError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Failed to load work {self._id}: {str(e)}") from e
            raise  # Re-raise other HTTP errors

        parsed_data = WorkParser(response).parse()
        parsed_data["ID"] = self._id
        parsed_data["link"] = f"https://archiveofourown.org/works/{self._id}"

        self._data = _ArchiveData.from_dictionary(parsed_data)
        self._is_loaded = True

    def _ensure_loaded(self) -> None:
        """Ensure the work data is loaded."""
        if not self._is_loaded:
            self.reload()

    @property
    def title(self) -> str:
        """The title of the work."""
        return self._data.title

    @property
    def id(self) -> str:
        """Get the work ID."""
        return self._id

    @property
    def author(self) -> str:
        """Get the work author(s)."""
        self._ensure_loaded()
        return self._data.author

    @property
    def link(self) -> str:
        """Get the work link."""
        self._ensure_loaded()
        return self._data.link

    @property
    def summary(self) -> Optional[str]:
        """Get the work summary."""
        self._ensure_loaded()
        return self._data.summary

    @property
    def language(self) -> str:
        """Get the work language."""
        self._ensure_loaded()
        return self._data.language

    @property
    def words(self) -> int:
        """Get the work word count."""
        self._ensure_loaded()
        return self._data.words

    @property
    def chapters_published(self) -> int:
        """Get the number of published chapters."""
        self._ensure_loaded()
        return self._data.chapters_published

    @property
    def chapters_expected(self) -> Optional[int]:
        """Get the expected number of chapters."""
        self._ensure_loaded()
        return self._data.chapters_expected

    @property
    def is_completed(self) -> bool:
        """Check if the work is completed."""
        self._ensure_loaded()
        return self._data.is_completed

    @property
    def kudos(self) -> int:
        """Get the number of kudos."""
        self._ensure_loaded()
        return self._data.kudos

    @property
    def comments(self) -> int:
        """Get the number of comments."""
        self._ensure_loaded()
        return self._data.comments

    @property
    def bookmarks(self) -> int:
        """Get the number of bookmarks."""
        self._ensure_loaded()
        return self._data.bookmarks

    @property
    def hits(self) -> int:
        """Get the number of hits."""
        self._ensure_loaded()
        return self._data.hits

    @property
    def published(self) -> Optional[datetime]:
        """Get the publication date."""
        self._ensure_loaded()
        return self._data.published

    @property
    def updated(self) -> Optional[datetime]:
        """Get the last updated date."""
        self._ensure_loaded()
        return self._data.updated

    @property
    def tags(self) -> list[str]:
        """Get the work tags."""
        self._ensure_loaded()
        return self._data.tags

    @property
    def relationships(self) -> list[tuple[str, str]]:
        """Get the character relationships."""
        self._ensure_loaded()
        return self._data.relationships

    @property
    def characters(self) -> list[str]:
        """Get the characters."""
        self._ensure_loaded()
        return self._data.characters

    @property
    def fandoms(self) -> list[str]:
        """Get the fandoms."""
        self._ensure_loaded()
        return self._data.fandoms

    @property
    def categories(self) -> list[str]:
        """Get the categories."""
        self._ensure_loaded()
        return self._data.categories

    @property
    def ratings(self) -> list[str]:
        """Get the ratings."""
        self._ensure_loaded()
        return self._data.ratings

    @property
    def warnings(self) -> list[str]:
        """Get the content warnings."""
        self._ensure_loaded()
        return self._data.warnings

    @property
    def series(self) -> Optional[str]:
        """Get the series information."""
        self._ensure_loaded()
        return self._data.series

    @property
    def is_restricted(self) -> bool:
        """Check if the work has restricted access."""
        self._ensure_loaded()
        return self._data.is_restricted

    def __repr__(self) -> str:
        """Return a string representation of the work."""
        if self._is_loaded:
            return f"ArchiveWork(id={self._id}, title='{self._data.title}')"
        return f"ArchiveWork(id={self._id}, not loaded)"
