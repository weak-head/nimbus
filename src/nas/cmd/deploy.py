from __future__ import annotations

from abc import abstractmethod
from datetime import datetime
from typing import Any

from nas.cmd.abstract import Action, ActionResult, Command, MappingResult
from nas.core.provider import Provider
from nas.core.service import OperationResult, Service, ServiceFactory


class Deployment(Command):
    """
    Manage service deployment.
    """

    def __init__(self, name: str, provider: Provider, factory: ServiceFactory):
        super().__init__(name, provider)
        self._factory = factory

    def _config(self) -> dict[str, Any]:
        return {}

    def _pipeline(self) -> list[Action]:
        return [
            self._map_resources,
            self._create_services,
            self._deploy,
        ]

    def _create_services(self, mapping: MappingResult) -> ServiceCreationResult:
        result = ServiceCreationResult()

        for service_resource in mapping.entries:
            result.entries.extend(self._factory.services(service_resource))

        result.completed = datetime.now()
        return result

    def _deploy(self, services: ServiceCreationResult) -> DeploymentResult:
        result = DeploymentResult(self._name)

        for service in services.entries:
            result.entries.append(self._operation(service))

        result.completed = datetime.now()
        return result

    @abstractmethod
    def _operation(self, service: Service) -> OperationResult:
        pass


class Up(Deployment):

    def __init__(self, provider: Provider, factory: ServiceFactory):
        super().__init__("Up", provider, factory)

    def _operation(self, service: Service) -> OperationResult:
        return service.start()


class Down(Deployment):

    def __init__(self, provider: Provider, factory: ServiceFactory):
        super().__init__("Down", provider, factory)

    def _operation(self, service: Service) -> OperationResult:
        return service.stop()


class ServiceCreationResult(ActionResult[list[Service]]):
    pass


class DeploymentResult(ActionResult[list[OperationResult]]):

    def __init__(self, operation: str, started: datetime = None):
        super().__init__(started)
        self.operation = operation
