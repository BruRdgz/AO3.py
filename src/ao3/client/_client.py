"""
Module responsible for communicating with OTW servers.
"""

from __future__ import annotations

from typing import Any, Optional, TypeVar, ParamSpec
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from cloudscraper import CloudScraper
from requests import Response, packages

from ao3.client._throttle import throttle_dispatch

# This disables IPV6.
# Since ArchiveOfOurOwn does not support IPv6, and `requests.Session` uses it by default,
# Disabling it forces `requests` to fall back to IPv4,
# Which saves time, since we're not waiting for the request to time out.
packages.urllib3.util.connection.HAS_IPV6 = False


__all__ = ["ClientSession"]


class ArchiveError(Exception):
    """
    Base exception for all exceptions raised by this module.
    """

    pass


class ClientNotAuthorizedError(ArchiveError):
    """
    Raised when the client is not authorized to access a page.
    """

    pass


class ArchivePageNotFoundError(ArchiveError):
    """
    Raised when the page does not exist.
    """

    pass


class ClientSession:
    """
    Base class for interacting with OTW.
    This class provides methods for programmatically posting requests to `Archiveofourown.org`
    """

    BASE_URL = "https://archiveofourown.org/"
    """Base URL for Archive Of Our Own."""
    _INSTANCE: Optional[ClientSession] = None
    """Singleton instance of the class."""

    def __new__(cls, *args, **kwargs) -> ClientSession:
        """
        Singleton implementation for the `ClientSession` class.
        This ensures that only one instance of the class is commonly shared across the library,
        that the requester doesn't get blocked by the website, and that authenticated credentials are shared.
        """
        # TODO: Consider raising an Exception if the user tries to create a new instance.
        # Reasoning being that, given the object (private as it may be) is not explicitly stated as a singleton,
        # The user may not be aware, and therefore be lied to about the object's nature.

        if cls._INSTANCE is None or not isinstance(cls._INSTANCE, cls):
            cls._INSTANCE = super().__new__(cls)

        return cls._INSTANCE

    def __init__(
        self,
    ) -> None:
        # If there's already a session object, then an instance has already been created.
        # Therefore, we return as to not rewrite the object.
        if hasattr(self, "_session"):
            return

        self._session = CloudScraper()
        """Session object for making requests to the website."""
        self._is_authenticated = False
        """If the client has authenticated credentials."""

    @staticmethod
    def _assert_response_success(
        response: Response | BeautifulSoup,
    ) -> None:
        """
        Asserts that the response is successful.
        If the response is not successful, raises an exception.

        Args:
            response (Response | BeautifulSoup): The response object to check.
        """
        if isinstance(response, Response):
            response = BeautifulSoup(response.text, "lxml")

        # TODO: Implement more checks for different types of errors.
        # Albeit requests can successfully return `200`, the page can still contain an error message.
        if response.find("div", {"id": "signin"}):
            raise ClientNotAuthorizedError(
                f"Failed to fetch data; This page is restricted to registered users. \nUnfortunately, this library does not currently support logging."
            )
        elif response.find("h2", {"class": "heading"}).text == "Error 404":
            raise ArchivePageNotFoundError(
                f"Failed to fetch data; This page does not exist. \nTIP: Have you entered the correct URL?"
            )

    def _resolve_url(self, url: str) -> str:
        """
        Resolves the given URL to an absolute URL.

        Args:
            url (str): The URL to resolve.

        Returns:
            str: The resolved URL.
        """
        return (
            url
            if url.startswith(("http://", "https://"))
            else urljoin(self.BASE_URL, url)
        )

    @throttle_dispatch(1.0)
    def fetch(
        self,
        url: str,
        params: Optional[dict[str, Any]] = None,
        soup: bool = False,
    ) -> BeautifulSoup | str:
        """
        Fetches data from the given URL.

        Args:
            url (str): The URL to fetch data from.
            params (Optional[dict[str, Any]]): The parameters to send with the request.
            soup (bool): If the response should be parsed to a BeautifulSoup object.

        Returns:
            BeautifulSoup | str: The response text if `soup` is False, otherwise a BeautifulSoup object.
        """
        url = self._resolve_url(url)
        response = self._session.get(url, params=params)
        self._assert_response_success(response)
        return response.text if not soup else BeautifulSoup(response.text, "lxml")

    @throttle_dispatch(1.0)
    def post(
        self,
        url: str,
        data: dict[str, Any],
        soup: bool = False,
    ) -> BeautifulSoup | str:
        """
        Posts data to the given URL.

        Args:
            url (str): The URL to post data to.
            data (dict[str, Any]): The data to post.
            soup (bool): If the response should be parsed to a BeautifulSoup object.

        Returns:
            BeautifulSoup | str: The response text if `soup` is False, otherwise BeautifulSoup`` object.
        """
        url = self._resolve_url(url)
        response = self._session.post(url, data=data)
        self._assert_response_success(response)
        return response.text if not soup else BeautifulSoup(response.text, "lxml")

    @classmethod
    def instance(cls) -> ClientSession:
        """
        Returns the singleton instance of the class.

        Returns:
            ClientSession: The singleton instance of the class.
        """
        return cls()
