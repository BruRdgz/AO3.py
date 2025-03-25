"""
Module for handling search functionality within Archive Of Our Own.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Any

from ao3.client import Session
from ao3.services.archiveWorks import ArchiveWork


class UserError(Exception):
    """
    Base exception for all exceptions raised by this module.
    """

    pass


class UserNotFoundError(UserError):
    """
    Raised when the requested user couldn't be found within AO3.
    """

    pass


@dataclass
class UserMetadata:
    name: str
    link: str
    id: Optional[str] = None

    bio: str = ""
    location: Optional[str] = None
    joined_at: Optional[str] = None
    email: Optional[str] = None

    works: list[ArchiveWork] = None
    bookmarks: list[ArchiveWork] = None
    series: dict[str, list[ArchiveWork]] = None  # TODO: Implement Series model

    collections: list[str] = (
        None  # Unsupported, could be implemented in the future as a model
    )
    fandoms: list[str] = None

    pseudonyms: list[ArchiveUser] = None
    is_pseudonym: bool = False
    parent: Optional[ArchiveUser] = None

    def __post_init__(self):
        """Initialize default values for mutable collections."""
        if self.pseudonyms is None:
            self.pseudonyms = []
        if self.works is None:
            self.works = []
        if self.bookmarks is None:
            self.bookmarks = []
        if self.series is None:
            self.series = {}
        if self.collections is None:
            self.collections = []
        if self.fandoms is None:
            self.fandoms = []

    def update(self, data: dict[str, Any]) -> None:
        for k, v in data.items():
            try:
                if hasattr(self, k):
                    setattr(self, k, v)
            except Exception as e:
                raise ValueError(
                    f"Invalid data parameter for {self.__class__.__name__}: {e}"
                )


class ArchiveUser:
    """
    Represents a user on Archive Of Our Own.

    This class provides methods for retrieving and accessing user metadata,
    including profile information, works, bookmarks, and pseudonyms.

    Args:
        name (str): The username of the AO3 user.
        parent (Optional[UserMetadata], optional): The parent user's metadata if this
            instance represents a pseudonym.
        load (bool, optional): Whether to load the user data immediately. Defaults to False.
    """

    def __init__(
        self,
        name: str,
        parent: Optional[UserMetadata] = None,
        load: bool = False,
    ) -> None:
        self._session = Session.instance()
        self._is_loaded = False
        self._data = UserMetadata(
            name=name, link=f"https://archiveofourown.org/users/{name}/profile"
        )
        if parent:
            self._build_pseudonym_relationship(name, parent)

        if load:
            self.reload()

    def _resolve_url(self, url: str) -> str:
        """
        Shortcut method from the client to resolve a URL.
        """
        return self._session._resolve_url(url)

    def _build_pseudonym_relationship(
        self,
        name: str,
        parent: UserMetadata,
    ) -> None:
        self._data.update(
            {
                "is_pseudonym": True,
                "link": f"/users/{parent.name}/pseuds/{name}",
                "parent": parent,
            }
        )
        parent.update(
            {
                "pseudonyms": parent.pseudonyms + [self],
            }
        )

    def reload(self) -> None:
        """Reload the user's metadata."""
        # data = [
        #    "/works",
        #    "/pseuds" if not self._data.is_pseudonym else None,
        #    "/bookmarks",
        #    "/series",
        #    "/collections",
        # ]

        raise NotImplementedError("User metadata retrieval is not yet implemented.")

    def _ensure_loaded(self) -> None:
        if not self._is_loaded:
            self.reload()

    @property
    def name(self) -> str:
        return self._data.name

    @property
    def link(self) -> str:
        return self._data.link

    @property
    def id(self) -> Optional[str]:
        self._ensure_loaded()
        return self._data.id

    @property
    def bio(self) -> str:
        self._ensure_loaded()
        return self._data.bio

    @property
    def location(self) -> Optional[str]:
        self._ensure_loaded()
        return self._data.location

    @property
    def joined_at(self) -> Optional[str]:
        self._ensure_loaded()
        return self._data.joined_at

    @property
    def email(self) -> Optional[str]:
        self._ensure_loaded()
        return self._data.email

    @property
    def works(self) -> list[ArchiveWork]:
        self._ensure_loaded()
        return self._data.works

    @property
    def bookmarks(self) -> list[ArchiveWork]:
        self._ensure_loaded()
        return self._data.bookmarks

    @property
    def series(self) -> dict[str, list[ArchiveWork]]:
        self._ensure_loaded()
        return self._data.series

    @property
    def collections(self) -> list[str]:
        self._ensure_loaded()
        return self._data.collections

    @property
    def fandoms(self) -> list[str]:
        self._ensure_loaded()
        return self._data.fandoms

    @property
    def pseudonyms(self) -> list[ArchiveUser]:
        self._ensure_loaded()
        return self._data.pseudonyms

    @property
    def is_pseudonym(self) -> bool:
        """Return whether this user is a pseudonym."""
        return self._data.is_pseudonym

    @property
    def parent(self) -> Optional[ArchiveUser]:
        """Return the parent user if this is a pseudonym."""
        return self._data.parent
