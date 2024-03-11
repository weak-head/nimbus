from abc import ABC, abstractmethod

from nas.config import Config
from nas.factory.command import CfgCommandFactory, CommandFactory
from nas.factory.component import CfgComponentFactory


class Builder(ABC):

    @abstractmethod
    def build_factory(self, config: Config) -> CommandFactory:
        pass


class CfgFactoryBuilder(Builder):

    def build_factory(self, config: Config) -> CommandFactory:
        return CfgCommandFactory(config, CfgComponentFactory(config))
