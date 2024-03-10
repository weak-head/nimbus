from __future__ import annotations

from abc import abstractmethod
from datetime import datetime
from typing import Any

from nas.cmd.abstract import Action, ActionResult, Command
from nas.core.service import OperationStatus, Service
from nas.factory.service import ServiceFactory
from nas.provider.service import ServiceProvider, ServiceResource


class Deployment(Command):
    """
    Manage service deployment.
    """

    def __init__(self, name: str, provider: ServiceProvider, factory: ServiceFactory):
        super().__init__(name)
        self._provider = provider
        self._factory = factory

    def _config(self) -> dict[str, Any]:
        return {}

    def _pipeline(self) -> list[Action]:
        return [
            Action(self._map_services),
            Action(self._create_services),
            Action(self._deploy),
        ]

    def _map_services(self, arguments: list[str]) -> ServiceMappingActionResult:
        result = ServiceMappingActionResult()
        result.entries = self._provider.resolve(arguments)
        result.completed = datetime.now()
        return result

    def _create_services(self, mapping: ServiceMappingActionResult) -> CreateServicesActionResult:
        result = CreateServicesActionResult()

        for service_resource in mapping.entries:
            result.entries.append(self._factory.create_service(service_resource))

        result.completed = datetime.now()
        return result

    def _deploy(self, services: CreateServicesActionResult) -> DeploymentActionResult:
        result = DeploymentActionResult(self._name)

        for service in services.entries:
            result.entries.append(self._operation(service))

        result.completed = datetime.now()
        return result

    @abstractmethod
    def _operation(self, service: Service) -> OperationStatus:
        pass


class Up(Deployment):

    def __init__(self, provider: ServiceProvider, factory: ServiceFactory):
        super().__init__("Up", provider, factory)

    def _operation(self, service: Service) -> OperationStatus:
        return service.start()


class Down(Deployment):

    def __init__(self, provider: ServiceProvider, factory: ServiceFactory):
        super().__init__("Down", provider, factory)

    def _operation(self, service: Service) -> OperationStatus:
        return service.stop()


class ServiceMappingActionResult(ActionResult[list[ServiceResource]]):
    pass


class CreateServicesActionResult(ActionResult[list[Service]]):
    pass


class DeploymentActionResult(ActionResult[list[OperationStatus]]):

    def __init__(self, operation: str, started: datetime = None):
        super().__init__(started)
        self.operation = operation
