import itertools

from nas.core.provider import Provider


class Secrets:
    """
    tbd
    """

    def __init__(self, service: Provider):
        """
        tbd
        """
        self._service = service

    def service(self, name: str) -> dict[str, str]:
        resources = self._service.resolve([name])
        if resources.empty:
            return {}

        secrets = list(itertools.chain([secret.artifacts for secret in resources.items]))
        if not secrets:
            return {}

        return {key: value for secret in secrets for key, value in secret.items()}
