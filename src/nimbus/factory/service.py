import logging

from logdecorator import log_on_end, log_on_error, log_on_start

from nimbus.core.runner import Runner
from nimbus.core.service import DockerService, Service
from nimbus.provider.secrets import Secrets
from nimbus.provider.service import ServiceResource


class ServiceFactory:
    """
    Service Factory that dynamically creates new instances
    of a service based on the provided service kind.
    The type of each created service instance depends on
    the characteristics of the resource.
    """

    def __init__(self, runner: Runner, secrets: Secrets) -> None:
        self._runner = runner
        self._secrets = secrets

    def __repr__(self) -> str:
        params = [
            f"runner='{self._runner.__class__.__name__}'",
            f"secrets='{self._secrets.__class__.__name__}'",
        ]
        return "ServiceFactory(" + ", ".join(params) + ")"

    @log_on_start(logging.DEBUG, "Creating Service: {resource.name!s} [{resource.kind!s}]")
    @log_on_end(logging.DEBUG, "Created Service: {result!r}")
    @log_on_error(logging.ERROR, "Failed to create Service: {e!r}", on_exceptions=Exception)
    def create_service(self, resource: ServiceResource) -> Service:
        match resource.kind:
            case "docker-compose":
                return DockerService(
                    resource.name,
                    resource.directory,
                    self._secrets.env(resource.name),
                    self._runner,
                )

            case _:
                return None
