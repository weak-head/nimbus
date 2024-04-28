from __future__ import annotations

from pathlib import Path
from typing import Iterator

from nimbus.provider.resource import Provider, Resource


class DirectoryResource(Resource):

    def __init__(self, name: str, directories: list[str]):
        super().__init__(name)
        self.directories: list[str] = directories


class DirectoryProvider(Provider[DirectoryResource]):

    def __init__(self, directory_groups: dict[str, list[str]]):
        self._groups = directory_groups

    def _resources(self) -> Iterator[DirectoryResource]:
        for group_name, directories in self._groups.items():
            yield DirectoryResource(
                group_name,
                [Path(d).expanduser().as_posix() for d in directories],
            )
