from nas.core.runner import Runner
from nas.core.service import DockerService, Service
from nas.provider.secrets import Secrets
from nas.provider.service import ServiceResource


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

    def create_service(self, resource: ServiceResource) -> Service:
        match resource.kind:
            case "docker-compose":
                return DockerService(
                    resource.name,
                    resource.directory,
                    self._secrets.environment(resource.name),
                    self._runner,
                )

            case _:
                return None
