from __future__ import annotations

import logging
from abc import abstractmethod
from typing import Any

from logdecorator import log_on_end

from nimbuscli.cmd.command import Action, ActionResult, Command
from nimbuscli.core.deploy import OperationStatus, Service
from nimbuscli.provider import ServiceFactory, ServiceProvider, ServiceResource


class Deployment(Command):
    """
    Manage service deployment.
    """

    def __init__(
        self,
        name: str,
        selectors: list[str],
        provider: ServiceProvider,
        factory: ServiceFactory,
    ):
        super().__init__(name, selectors)
        self._provider = provider
        self._factory = factory

    def _config(self) -> dict[str, Any]:
        return {}

    @log_on_end(logging.DEBUG, "Pipeline: {result!r}")
    def _pipeline(self) -> list[Action]:
        return [
            Action(self._map_services),
            Action(self._create_services),
            Action(self._deploy),
        ]

    @log_on_end(logging.DEBUG, "Mapped {selectors!r} to {result!s}")
    def _map_services(self, selectors: list[str]) -> ServiceMappingActionResult:
        return ServiceMappingActionResult(
            self._provider.resolve(selectors),
        )

    @log_on_end(logging.DEBUG, "Services: {result!s}")
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

    def __init__(self, arguments: list[str], provider: ServiceProvider, factory: ServiceFactory):
        super().__init__("Up", arguments, provider, factory)

    def _operation(self, service: Service) -> OperationStatus:
        return service.start()


class Down(Deployment):

    def __init__(self, arguments: list[str], provider: ServiceProvider, factory: ServiceFactory):
        super().__init__("Down", arguments, provider, factory)

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
    def success(self) -> bool:
        return all(e.success for e in self.entries)

    @property
    def successful(self) -> list[OperationStatus]:
        return [srv for srv in self.entries if srv.success]

    @property
    def failed(self) -> list[OperationStatus]:
        return [srv for srv in self.entries if not srv.success]
