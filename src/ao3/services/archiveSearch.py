"""
Module for handling search functionality within Archive Of Our Own.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar, Any, Literal

from ao3.client import Session

T = TypeVar("T")


@dataclass
class Result(Generic[T]):
    """
    Model representing the results of a search query within AO3.

    Args:
        type (Literal["works", "users",]): The type of the search results.
        parameters (dict[str, Any]): The parameters used in the search query.
        results (list[T]): The results of the search
    """

    type: Literal[
        "works",
        "users",
    ]  # TODO: Support more types of searches
    parameters: dict[str, Any]
    results: list[T]

    def update(self, data: dict[str, Any]) -> None:
        for k, v in data.items():
            try:
                if hasattr(self, k):
                    setattr(self, k, v)
            except Exception as e:
                raise ValueError(
                    f"Invalid data parameter for {self.__class__.__name__}: {e}"
                )


class ArchiveSearch:
    """
    Represents a search query on Archive Of Our Own.

    This class provides methods for constructing, executing, and retrieving results
    from search queries on AO3, supporting different search types like works and users.

    Args:
        params (dict[str, Any]): The parameters used in the search query.
        search_type (Literal["works", "users"], optional): The type of the search results.
            Defaults to "works".
    """

    def __init__(
        self,
        params: dict[str, Any],
        search_type: Literal["works", "users"] = "works",
    ) -> None:
        self._params = params
        self._session = Session.instance()
        self.type = search_type.lower()

        if self.type not in ("works", "users"):
            raise ValueError(
                f"Invalid search type '{self.type}'; must be either 'works' or 'users'."
            )

        raise NotImplementedError("The search functionality is not yet implemented.")

    # TODO: Implement the search functionality
