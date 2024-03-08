from __future__ import annotations

import fnmatch
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class Provider(ABC):
    """
    Defines an abstract resource provider.
    All providers should follow the APIs defined by this class.
    """

    def resolve(self, patterns: list[str]) -> list[Resource]:
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
                matches.append(resource)

        return sorted(matches, key=lambda res: res.name)

    @abstractmethod
    def _resources(self) -> list[Resource]:
        """
        Returns a complete collection of all available resources.
        """


class DirectoryProvider(Provider):
    """
    Provider that maps all directories under the specified path to
    a list of resources, where a directory name is mapped to the resource name.
    """

    def __init__(self, root_dir: str):
        self._root_dir = root_dir

    def _resources(self) -> list[DirectoryResource]:
        resources = []
        for obj in Path(self._root_dir).iterdir():
            if obj.is_dir():
                resources.append(DirectoryResource(obj.name, [obj.as_posix()]))

        return resources


class DictionaryProvider(Provider):
    """
    Provider that uses a given dictionary for the resource resolution.
    Each key in the dictionary is mapped to the resource name.
    """

    def __init__(self, groups: dict[str, Any]):
        self._groups = groups

    def _resources(self) -> list[Resource]:
        return [Resource(key, value) for key, value in self._groups.items()]


class Resource[T](Generic[T]):
    """
    Resource is a grouping of a unique resource name
    and one or many custom artifacts of any type.
    """

    def __init__(self, name: str, artifacts: T = None):
        self.name: str = name
        self.artifacts = artifacts

    def match(self, pattern: str) -> bool:
        return len(fnmatch.filter([self.name], pattern)) > 0


class DirectoryResource(Resource[list[str]]):
    pass
