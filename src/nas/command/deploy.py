from __future__ import annotations

from abc import abstractmethod
from datetime import datetime

from nas.command.abstract import ActionInfo, Command, PipelineInfo
from nas.core.provider import Provider, Resources
from nas.core.service import OperationResult, Service, ServiceFactory
from nas.report.writer import Writer


class Deployment(Command):
    """
    Manage service deployment.
    """

    def __init__(self, writer: Writer, provider: Provider, factory: ServiceFactory, name: str):
        super().__init__(writer, provider)
        self._factory = factory
        self._name = name

    def _build_pipeline(self, arguments: list[str]) -> PipelineInfo:
        pi = PipelineInfo("Deploy")
        pi.config = {}
        pi.pipeline = [self._build_services, self._deploy]
        pi.arguments = arguments
        pi.resources = self._provider.resolve(arguments)
        return pi

    def _build_services(self, resources: Resources) -> ServicesInfo:
        info = ServicesInfo(started=datetime.now())

        for res in resources.items:
            info.entries.extend(self._factory.services(res))

        info.completed = datetime.now()
        return info

    def _deploy(self, si: ServicesInfo) -> DeploymentInfo:
        info = DeploymentInfo(started=datetime.now())

        for service in si.entries:
            info.entries.append(self._operation(service))

        info.completed = datetime.now()
        return info

    @abstractmethod
    def _operation(self, service: Service) -> OperationResult:
        pass


class Up(Deployment):

    def __init__(self, writer: Writer, provider: Provider, factory: ServiceFactory):
        super().__init__(writer, provider, factory, "Up")

    def _operation(self, service: Service) -> OperationResult:
        return service.start()


class Down(Deployment):

    def __init__(self, writer: Writer, provider: Provider, factory: ServiceFactory):
        super().__init__(writer, provider, factory, "Down")

    def _operation(self, service: Service) -> OperationResult:
        return service.stop()


class ServicesInfo(ActionInfo[Service]):
    pass


class DeploymentInfo(ActionInfo[OperationResult]):
    pass
