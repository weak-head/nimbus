from __future__ import annotations

import fnmatch
from abc import ABC, abstractmethod
from typing import Any


class Provider(ABC):
    """
    Defines an abstract resource provider.
    All providers should follow the APIs defined by this class.
    """

    def resolve(self, patterns: list[str]) -> Resources:
        """
        Resolve available resources using a set of glob patterns.

        :param patterns: A set of glob patterns used to match resources.
            Each pattern should follow the typical glob matching rules:
                *     - matches any number of any characters including none
                ?     - matches any single character
                [abc] - matches one character given in the bracket
                [a-z] - matches one character from the range given in the bracket
        """

        matches = []
        for resource in self._resources():
            if not patterns or any((resource.match(pat) for pat in patterns)):
                matches.add(resource)

        return Resources(sorted(matches, key=lambda res: res.name))

    @abstractmethod
    def _resources(self) -> list[Resource]:
        """
        Returns a complete collection of all available resources.
        """


class Resources:
    """
    A logical grouping of several resources.
    """

    def __init__(self, items: list[Resource]):
        self.items: list[Resource] = items

    @property
    def empty(self) -> bool:
        return len(self.items) == 0


class Resource:
    """
    Resource is a grouping of a unique resource name
    and a list of custom artifacts of any type.
    """

    def __init__(self, name: str, artifacts: list[Any] = None):
        self.name: str = name
        self.artifacts: list[Any] = artifacts

    def match(self, pattern: str) -> bool:
        return len(fnmatch.filter([self.name], pattern)) > 0


class FileSystemServiceProvider(Provider):
    """
    Service provider that discovers services under the
    specified location on the local file system.
    """


class GroupProvider(Provider):
    """
    Group provider that uses a given configuration
    for the group resolution.
    """
