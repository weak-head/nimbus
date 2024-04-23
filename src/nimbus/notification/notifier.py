from abc import ABC, abstractmethod


class Notifier(ABC):
    """
    Defines an abstract notification sender.
    All notification senders should follow the APIs defined by this class.
    """

    @abstractmethod
    def notify(self) -> None:
        """
        Send a notification.

        tbd
        """


class CompositeNotifier(Notifier):

    def __init__(self, notifiers: list[Notifier]) -> None:
        self._notifiers = notifiers if notifiers else []

    def __repr__(self) -> str:
        params = [repr(r) for r in self._notifiers]
        return "CompositeNotifier(" + ", ".join(params) + ")"

    def notify(self) -> None:
        for notifier in self._notifiers:
            notifier.notify()


class DiscordNotifier(Notifier):
    """
    Sends notifications to a Discord channel.
    """

    def __init__(self, hook_id: str, hook_token: str) -> None:
        self._hid = hook_id
        self._htoken = hook_token

    def __repr__(self) -> str:
        params = [
            f"hid='{self._hid}'",
            f"htoken='{self._htoken}'",
        ]
        return "DiscordNotifier(" + ", ".join(params) + ")"

    def notify(self) -> None:
        pass
