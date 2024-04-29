import logging
from abc import ABC, abstractmethod

from logdecorator import log_on_end, log_on_error, log_on_start

from nimbus.config import Config
from nimbus.notify.discord import DiscordNotifier
from nimbus.notify.notifier import CompositeNotifier, Notifier


class NotifierFactory(ABC):
    """
    Abstract notifier factory.
    """

    @abstractmethod
    def create_notifier(self) -> Notifier:
        pass


class CfgNotifierFactory(NotifierFactory):

    def __init__(self, config: Config) -> None:
        self._cfg = config

    @log_on_start(logging.DEBUG, "Creating Notifier")
    @log_on_end(logging.DEBUG, "Created Notifier: {result!r}")
    @log_on_error(logging.ERROR, "Failed to create Notifier: {e!r}", on_exceptions=Exception)
    def create_notifier(self) -> Notifier:
        notifiers = []

        # If 'observability' section is omitted,
        # or 'observability.notifications' is not specified
        # the notifications would be disabled.
        if cfg := self._cfg.nested("observability.notifications.discord"):
            notifiers.append(DiscordNotifier(cfg.webhook, cfg.username, cfg.avatar_url))

        return CompositeNotifier(notifiers)
