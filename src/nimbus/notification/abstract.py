from abc import ABC, abstractmethod

from nimbus.cmd.abstract import ExecutionResult


class Notifier(ABC):
    """
    Defines an abstract notification sender.
    All notification senders should follow the APIs defined by this class.
    """

    @abstractmethod
    def completed(self, result: ExecutionResult, attachments: list[str] = None) -> None:
        """
        Send a completion notification, with optional attachments.

        :param result: Command execution result.
        :param attachments: Notification attachments, such as reports.
        """


class CompositeNotifier(Notifier):

    def __init__(self, notifiers: list[Notifier]) -> None:
        self._notifiers = notifiers if notifiers else []

    def __repr__(self) -> str:
        params = [repr(r) for r in self._notifiers]
        return "CompositeNotifier(" + ", ".join(params) + ")"

    def completed(self, result: ExecutionResult, attachments: list[str] = None) -> None:
        for notifier in self._notifiers:
            notifier.completed(result, attachments)
