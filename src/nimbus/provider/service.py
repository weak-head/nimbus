from __future__ import annotations

from pathlib import Path
from typing import Iterator

from nimbus.provider.abstract import Provider, Resource


class ServiceResource(Resource):

    def __init__(self, name: str, kind: str, directory: str):
        super().__init__(name)
        self.kind: str = kind
        self.directory: str = directory


class ServiceProvider(Provider[ServiceResource]):
    """
    This class provides a recursive mechanism for
    discovering services within all parent folders.
    By traversing through parent folders, it facilitates
    the identification and interaction with services,
    """

    def __init__(self, directories: list[str]):
        self._directories: list[str] = directories
        self._compose_files = [
            "compose.yml",
            "compose.yaml",
            "docker-compose.yml",
            "docker-compose.yaml",
        ]

    def __repr__(self) -> str:
        params = [
            f"dirs={self._directories!r}",
        ]
        return "ServiceProvider(" + ", ".join(params) + ")"

    def _resources(self) -> Iterator[ServiceResource]:
        for directory in self._directories:
            yield from self._discover(Path(directory).expanduser())

    def _discover(self, path: Path) -> Iterator[ServiceResource]:
        if not path.is_dir():
            return

        match kind := self._get_kind(path):
            case "docker-compose":
                yield ServiceResource(
                    path.name,
                    kind,
                    path.as_posix(),
                )

            case None:
                for obj in path.iterdir():
                    yield from self._discover(obj)

    def _get_kind(self, path: Path) -> str:
        if any(path.joinpath(file).exists() for file in self._compose_files):
            return "docker-compose"
        return None
