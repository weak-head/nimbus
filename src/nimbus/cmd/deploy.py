from __future__ import annotations

from abc import abstractmethod
from typing import Any

from nimbus.cmd.abstract import Action, ActionResult, Command
from nimbus.core.service import OperationStatus, Service
from nimbus.factory.service import ServiceFactory
from nimbus.provider.service import ServiceProvider, ServiceResource


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
        return ServiceMappingActionResult(
            self._provider.resolve(arguments),
        )

    def _create_services(self, mapping: ServiceMappingActionResult) -> CreateServicesActionResult:
        return CreateServicesActionResult(
            [self._factory.create_service(srv) for srv in mapping.entries],
        )

    def _deploy(self, services: CreateServicesActionResult) -> DeploymentActionResult:
        return DeploymentActionResult(
            self._name,
            [self._operation(service) for service in services.entries],
        )

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

    def __init__(self, operation: str, entries: list[OperationStatus] = None):
        super().__init__(entries)
        self.operation = operation

    @property
    def successful(self) -> list[OperationStatus]:
        return [srv for srv in self.entries if srv.success]

    @property
    def failed(self) -> list[OperationStatus]:
        return [srv for srv in self.entries if not srv.success]
