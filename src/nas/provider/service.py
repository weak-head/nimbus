from __future__ import annotations

from os.path import exists, join
from pathlib import Path
from typing import Iterator

from nas.provider.abstract import Provider, Resource


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

    def __init__(self, root_directories: list[str]):
        self._root_dirs: list[str] = root_directories

    def _resources(self) -> Iterator[ServiceResource]:
        for root_dir in self._root_dirs:
            yield from self._discover_services(root_dir)

    def _discover_services(self, root_path: str) -> Iterator[ServiceResource]:
        path = Path(root_path).expanduser()
        service_kind = self._get_service_kind(path.as_posix())

        if service_kind != "unknown":
            yield ServiceResource(path.name, service_kind, path.as_posix())
        else:
            for obj in path.iterdir():
                if obj.is_dir():
                    yield from self._discover_services(obj.as_posix())

    def _get_service_kind(self, directory: str) -> str:
        compose_file_names = [
            "compose.yaml",
            "compose.yml",
            "docker-compose.yaml",
            "docker-compose.yml",
        ]
        if any(exists(join(directory, file)) for file in compose_file_names):
            return "docker-compose"
        return "unknown"
