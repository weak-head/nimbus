from __future__ import annotations

import fnmatch
from typing import Iterator


class Secret:

    ENVIRONMENT = "service-env"

    def __init__(self, kind: str, selector: str, values: dict[str, str]):
        self.kind: str = kind
        self.selector: str = selector
        self.values: dict[str, str] = values

    def match(self, name: str) -> bool:
        return fnmatch.filter([name], self.selector)


class SecretsProvider:

    def __init__(self, secrets: list[dict[str, str]]):
        self._secrets = secrets

    def all(self) -> Iterator[Secret]:
        for secret in self._secrets:
            yield Secret(
                Secret.ENVIRONMENT,
                secret["service"],
                secret["environment"],
            )

    def environment(self, service: str) -> Iterator[Secret]:
        for secret in self.all():
            if secret.kind == Secret.ENVIRONMENT and secret.match(service):
                yield secret


class Secrets:
    """
    The `Secrets` class encapsulates a small amount of sensitive data,
    such as a password, token, or key. It provides methods to query and
    manage this sensitive information based on the associated resource.
    This abstraction ensures secure handling of confidential data
    within your application.
    """

    def __init__(self, provider: SecretsProvider):
        self._provider = provider

    def environment(self, service: str) -> dict[str, str]:
        """
        Retrieve a consolidated collection of environment
        variables for a specified service chosen by the name.
        """
        secrets = {}
        for secret in self._provider.environment(service):
            secrets = secrets | secret.values
        return secrets
