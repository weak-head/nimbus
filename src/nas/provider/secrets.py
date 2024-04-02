from __future__ import annotations

import fnmatch
from typing import Iterator


class Secret:

    def __init__(self, selector: str, values: dict[str, str]):
        self.selector: str = selector
        self.values: dict[str, str] = values


class SecretsProvider:

    def __init__(self, secrets: list[dict[str, str]]):
        self._secrets = secrets if secrets else []

    def env(self, service: str) -> Iterator[Secret]:
        for entry in self._secrets:
            yield from self._to_env(entry, service)

    def _to_env(self, entry: dict[str, str], service: str) -> Iterator[Secret]:
        if (sel := entry.get("service")) and (env := entry.get("environment")):
            if fnmatch.filter([service], sel):
                yield Secret(sel, {k: str(v) for k, v in env.items()})


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

    def env(self, service: str) -> dict[str, str]:
        """
        Retrieve a consolidated collection of environment
        variables for a specified service chosen by the name.
        """
        secrets = {}
        for secret in self._provider.env(service):
            secrets |= secret.values
        return secrets
