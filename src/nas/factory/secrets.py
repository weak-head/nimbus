from nas.provider.secrets import SecretsProvider


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
