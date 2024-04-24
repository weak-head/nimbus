from abc import ABC, abstractmethod
from datetime import datetime

import requests

import nimbus.report.format as fmt
from nimbus.cmd.abstract import ExecutionResult


class Notifier(ABC):
    """
    Defines an abstract notification sender.
    All notification senders should follow the APIs defined by this class.
    """

    @abstractmethod
    def completed(self, result: ExecutionResult) -> None:
        """
        Send a notification about the completion of a command execution.
        """


class CompositeNotifier(Notifier):

    def __init__(self, notifiers: list[Notifier]) -> None:
        self._notifiers = notifiers if notifiers else []

    def __repr__(self) -> str:
        params = [repr(r) for r in self._notifiers]
        return "CompositeNotifier(" + ", ".join(params) + ")"

    def completed(self, result: ExecutionResult) -> None:
        for notifier in self._notifiers:
            notifier.completed(result)


class DiscordNotifier(Notifier):
    """
    Sends notifications to a Discord channel.
    """

    _FAILURE = 0xFF0000
    _SUCCESS = 0x00FF00

    def __init__(self, webhook: str, username: str = None, avatar_url: str = None) -> None:
        self._webhook = webhook
        self._username = username
        self._avatar_url = avatar_url

    def __repr__(self) -> str:
        params = [
            f"webhook='{self._webhook}'",
        ]
        return "DiscordNotifier(" + ", ".join(params) + ")"

    def _send(self, json: dict) -> None:
        requests.post(
            self._webhook,
            json=json,
            timeout=3000,
        )

    def _compose_completed(self, result: ExecutionResult) -> dict:
        """
        Compose 'completed' notification request that follows the discord spec:
            - https://discord.com/developers/docs/resources/webhook
        """
        data = {}
        if self._username:
            data["username"] = self._username
        if self._avatar_url:
            data["avatar_url"] = self._avatar_url

        event = {}
        event["timestamp"] = datetime.now().astimezone().isoformat()
        event["color"] = DiscordNotifier._SUCCESS if result.success else DiscordNotifier._FAILURE
        event["title"] = result.command
        event["fields"] = [
            {"name": "Started", "value": fmt.datetime(result.started), "inline": False},
            {"name": "Completed", "value": fmt.datetime(result.completed), "inline": False},
            {"name": "Elapsed", "value": fmt.duration(result.elapsed), "inline": False},
        ]

        data["embeds"] = [event]
        return data

    def completed(self, result: ExecutionResult) -> None:
        self._send(self._compose_completed(result))
