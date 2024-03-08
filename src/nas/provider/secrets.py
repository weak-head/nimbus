from __future__ import annotations

from typing import Iterator

from nas.provider.abstract import Provider, Resource


class SecretResource(Resource):

    def __init__(self, name: str, secrets: dict[str, str]):
        super().__init__(name)
        self.secrets: dict[str, str] = secrets


class SecretsProvider(Provider[SecretResource]):

    def __init__(self, service_secrets: dict[str, dict[str, str]]):
        self._service_secrets = service_secrets

    def _resources(self) -> Iterator[SecretResource]:
        for service_name, secrets in self._service_secrets.items():
            yield SecretResource(service_name, secrets)
