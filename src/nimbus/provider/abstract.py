from __future__ import annotations

import fnmatch
from abc import abstractmethod
from typing import Generic, Iterator, TypeVar


class Resource:
    """
    An abstract resource serves as a foundational concept.
    It represents a cohesive unit that combines a unique resource name with
    a collection of custom attributes or artifacts.
    The specific nature of the resource is further clarified by its subclasses.
    """

    def __init__(self, name: str):
        self.name: str = name

    def match(self, selector: str) -> bool:
        return fnmatch.filter([self.name], selector)


T = TypeVar("T", bound=Resource)


class Provider(Generic[T]):
    """
    An abstract resource provider serves as a foundational concept.
    It establishes the guidelines that all providers must adhere to
    by following the APIs defined in this class.
    The primary responsibility of a provider is to resolve a collection
    of available resources based on specified selectors and subsequently
    return a filtered list of these resources.
    """

    def resolve(self, selectors: list[str]) -> list[T]:
        """
        Resolve available resources using a set of selectors.

        :param selectors: A set of selectors used to match resources.
            Each selector should follow the typical glob matching rules:
                *     - matches any number of any characters including none
                ?     - matches any single character
                [abc] - matches one character given in the bracket
                [a-z] - matches one character from the range given in the bracket
        """

        matches: list[T] = []
        for resource in self._resources():
            if not selectors or any((resource.match(sel) for sel in selectors)):
                matches.append(resource)

        return sorted(matches, key=lambda res: res.name)

    @abstractmethod
    def _resources(self) -> Iterator[T]:
        """
        Returns a complete collection of all available resources.
        """
