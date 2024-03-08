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

    def __init__(self, root_dir: str):
        self._root_dir = root_dir

    def _resources(self) -> Iterator[ServiceResource]:
        for obj in Path(self._root_dir).iterdir():
            if obj.is_dir():
                directory = obj.as_posix()
                yield ServiceResource(
                    obj.name,
                    self._get_service_kind(directory),
                    directory,
                )

    def _get_service_kind(self, directory: str) -> str:
        compose_file_names = [
            "compose.yaml",
            "compose.yml",
            "docker-compose.yaml",
            "docker-compose.yml",
        ]
        if any(exists(join(directory, file) for file in compose_file_names)):
            return "docker-compose"
        return "unknown"
