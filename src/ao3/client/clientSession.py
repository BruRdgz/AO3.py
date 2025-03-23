"""
Module responsible for communicating with ArchiveOfOurOwn.org.
"""

from __future__ import annotations

from typing import Any, Optional, Final
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from cloudscraper import CloudScraper

__all = [
    "Client",
]


class Client:
    """
    Base class for interacting with ArchiveOfOurOwn.org.
    Provides methods for making requests to the website.
    """

    BASE_URL: Final[str] = "https://archiveofourown.org"
    """The base URL for the ArchiveOfOurOwn.org"""

    def __init__(self) -> None:
        self._session = CloudScraper()
        """Session object for making requests to the website."""

    def _resolve_url(
        self,
        url: str,
    ) -> str:
        """
        Resolves a relative URL to an absolute URL.

        Args:
            url (str): The URL to resolve.

        Returns:
            str: The resolved URL.
        """
        if url.startswith(("http://", "https://")):
            return url
        return urljoin(self.BASE_URL, url)

    def fetch(
        self,
        url: str,
        params: Optional[dict[str, Any]] = None,
        soup: bool = False,
    ) -> str | BeautifulSoup:
        """
        Fetches a webpage from the ArchiveOfOurOwn.org.

        Args:
            url (str): The URL to fetch.
            params (Optional[dict[str, Any]]): The parameters to include in the request.
            soup (bool): Whether to parse the response as BeautifulSoup. Defaults to `True`.

        Returns:
            str | BeautifulSoup: The response from the website.
        """
        url = self._resolve_url(url)
        response = self._session.get(url, params=params)
        return BeautifulSoup(response.text, "lxml") if soup else response.text

    def post(
        self,
        url: str,
        data: dict[str, Any],
        soup: bool = False,
    ) -> str | BeautifulSoup:
        """
        Sends a POST request to the ArchiveOfOurOwn.org.

        Args:
            url (str): The URL to fetch.
            data (dict[str, Any]): The data to include in the request.
            soup (bool): Whether to parse the response as BeautifulSoup. Defaults to `True`.

        Returns:
            str | BeautifulSoup: The response from the website.
        """
        url = self._resolve_url(url)
        response = self._session.post(url, data=data)
        return BeautifulSoup(response.text, "lxml") if soup else response.text

    def close(self) -> None:
        """
        Closes the session.
        """
        self._session.close()
