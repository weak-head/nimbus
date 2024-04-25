import logging
from abc import ABC, abstractmethod

from logdecorator import log_on_end, log_on_error, log_on_start

from nimbus.config import Config
from nimbus.notification.abstract import CompositeNotifier, Notifier
from nimbus.notification.discord import DiscordNotifier


class NotifierFactory(ABC):
    """
    Abstract notifier factory.
    """

    @abstractmethod
    def create_notifier(self) -> Notifier:
        pass


class CfgNotifierFactory(NotifierFactory):

    def __init__(self, config: Config) -> None:
        self._config = config

    @log_on_start(logging.DEBUG, "Creating Notifier")
    @log_on_end(logging.DEBUG, "Created Notifier: {result!r}")
    @log_on_error(logging.ERROR, "Failed to create Notifier: {e!r}", on_exceptions=Exception)
    def create_notifier(self) -> Notifier:
        notifiers = []

        if discord := self._config.observability.notifications.discord:
            notifiers.append(
                DiscordNotifier(
                    discord.webhook,
                    discord.username,
                    discord.avatar_url,
                )
            )

        return CompositeNotifier(notifiers)
