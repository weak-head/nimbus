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


class Secrets:
    """
    The `Secrets` class encapsulates a small amount of sensitive data, such as a password, token, or key.
    It provides methods to query and manage this sensitive information based on the associated resource.
    This abstraction ensures secure handling of confidential data within your application.
    """

    def __init__(self, service_secrets: SecretsProvider):
        self._service_secrets = service_secrets

    def service(self, selector: str) -> dict[str, str]:
        """
        Retrieve a consolidated collection of secrets for a
        specified set of services chosen by the selector.
        """
        secrets = {}
        for service in self._service_secrets.resolve([selector]):
            secrets = secrets | service.secrets
        return secrets
