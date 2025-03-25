"""
Module for models representing works within Archive Of Our Own.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any

from ao3.client import Session
from ao3.parsers import WorkParser

__all__ = ["ArchiveWork"]


class WorkError(Exception):
    """
    Base exception for all exceptions raised by this module.
    """

    pass


class WorkNotFoundError(Exception):
    """
    Raised when the requested work couldn't be found within AO3.
    """

    pass


class WorkRestrictedError(Exception):
    """
    Raised when the work is restricted, but no credentials are provided by the client.
    """

    pass


@dataclass
class WorkMetadata:
    """
    Model representing the metadata of a work within AO3.
    """

    ID: str
    title: str = ""
    author: str = ""
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

    def update(self, data: dict[str, Any]) -> None:
        for k, v in data.items():
            try:
                if hasattr(self, k):
                    setattr(self, k, v)
            except Exception as e:
                raise ValueError(
                    f"Invalid data parameter for {self.__class__.__name__}: {e}"
                )


class ArchiveWork:
    """
    Represents a work (story) on Archive Of Our Own.

    This class provides methods for retrieving and accessing work metadata,
    including title, author, statistics, and tags.

    Args:
        work_id (str): The ID of the work.
        load (bool, optional): If the work metadata should be loaded upon initialization. Defaults to False.
    """

    def __init__(
        self,
        work_id: str,
        load: bool = False,
    ) -> None:
        self._session = Session.instance()
        self._id = work_id
        self._data = WorkMetadata(
            ID=work_id, link=f"https://archiveofourown.org/works/{work_id}"
        )
        self._loaded = False

        if load:
            self.reload()

    def reload(self) -> None:
        """Reload the work metadata."""
        self._loaded = True
        response = self._session.fetch(self._data.link, soup=True)
        parser = WorkParser(response)
        self._data.update(parser.parse())

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self.reload()

    @property
    def title(self) -> str:
        """Return the title of the work."""
        self._ensure_loaded()
        return self._data.title

    @property
    def author(self) -> str:
        """Return the author of the work."""
        self._ensure_loaded()
        return self._data.author

    @property
    def link(self) -> str:
        """Return the link to the work."""
        self._ensure_loaded()
        return self._data.link

    @property
    def summary(self) -> Optional[str]:
        """Return the summary of the work."""
        self._ensure_loaded()
        return self._data.summary

    @property
    def language(self) -> str:
        """Return the language of the work."""
        self._ensure_loaded()
        return self._data.language

    @property
    def words(self) -> int:
        """Return the word count of the work."""
        self._ensure_loaded()
        return self._data.words

    @property
    def chapters_published(self) -> int:
        """Return the number of chapters published."""
        self._ensure_loaded()
        return self._data.chapters_published

    @property
    def chapters_expected(self) -> Optional[int]:
        """Return the expected number of chapters."""
        self._ensure_loaded()
        return self._data.chapters_expected

    @property
    def is_completed(self) -> bool:
        """Return whether the work is completed."""
        self._ensure_loaded()
        return self._data.is_completed

    @property
    def kudos(self) -> int:
        """Return the number of kudos."""
        self._ensure_loaded()
        return self._data.kudos

    @property
    def comments(self) -> int:
        """Return the number of comments."""
        self._ensure_loaded()
        return self._data.comments

    @property
    def bookmarks(self) -> int:
        """Return the number of bookmarks."""
        self._ensure_loaded()
        return self._data.bookmarks

    @property
    def hits(self) -> int:
        """Return the number of hits."""
        self._ensure_loaded()
        return self._data.hits

    @property
    def published(self) -> Optional[datetime]:
        """Return the date the work was published."""
        self._ensure_loaded()
        return self._data.published

    @property
    def updated(self) -> Optional[datetime]:
        """Return the date the work was updated."""
        self._ensure_loaded()
        return self._data.updated

    @property
    def tags(self) -> list[str]:
        """Return the tags of the work."""
        self._ensure_loaded()
        return self._data.tags

    @property
    def relationships(self) -> list[tuple[str, str]]:
        """Return the relationships of the work."""
        self._ensure_loaded()
        return self._data.relationships

    @property
    def characters(self) -> list[str]:
        """Return the characters of the work."""
        self._ensure_loaded()
        return self._data.characters

    @property
    def fandoms(self) -> list[str]:
        """Return the fandoms of the work."""
        self._ensure_loaded()
        return self._data.fandoms

    @property
    def ratings(self) -> list[str]:
        """Return the ratings of the work."""
        self._ensure_loaded()
        return self._data.ratings
