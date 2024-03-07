from nas.core.provider import Provider


class Secrets:
    """
    The `Secrets` class encapsulates a small amount of sensitive data, such as a password, token, or key.
    It provides methods to query and manage this sensitive information based on the associated resource.
    This abstraction ensures secure handling of confidential data within your application.
    """

    def __init__(self, service_secrets: Provider):
        self._service_secrets = service_secrets

    def service(self, name_pattern: str) -> dict[str, str]:
        """
        Retrieve a consolidated collection of secrets for a specified service.
        """
        secrets = {}
        for service in self._service_secrets.resolve([name_pattern]):
            if isinstance(service.artifacts, dict):
                secrets = secrets | service.artifacts
        return secrets
