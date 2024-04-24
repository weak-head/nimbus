from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterator

import requests

import nimbus.report.format as fmt
from nimbus.cmd.abstract import ExecutionResult
from nimbus.cmd.deploy import DeploymentActionResult


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
            f"username='{self._username}'",
            f"avatar_url='{self._avatar_url}'",
        ]
        return "DiscordNotifier(" + ", ".join(params) + ")"

    def _send_message(self, json: dict) -> None:
        requests.post(
            self._webhook,
            json=json,
            timeout=3_000,
        )

    def _send_attachment(self, filepath: str) -> None:
        with open(filepath, "rb") as file:
            requests.post(
                self._webhook,
                files={"file": file},
                timeout=10_000,
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
        event["title"] = f"{fmt.ch('success') if result.success else fmt.ch('failure')} {result.command}"
        event["color"] = DiscordNotifier._SUCCESS if result.success else DiscordNotifier._FAILURE
        event["timestamp"] = datetime.now().astimezone().isoformat()
        event["fields"] = [
            {"name": f"{fmt.ch('duration')} Elapsed", "value": f"{fmt.duration(result.elapsed)}", "inline": True},
            {"name": f"{fmt.ch('time')} Started", "value": f"{fmt.datetime(result.started)}", "inline": True},
            {"name": f"{fmt.ch('time')} Completed", "value": f"{fmt.datetime(result.completed)}", "inline": True},
            *self._details(result),
        ]

        data["embeds"] = [event]
        return data

    def _details(self, result: ExecutionResult) -> Iterator[dict]:
        for action in result.actions:
            match action:
                case DeploymentActionResult():
                    yield {
                        "name": f"{fmt.ch('service')} Services",
                        "value": "\n".join(
                            [
                                f"{ix:02d}. "
                                f"{fmt.ch('success') if entry.success else fmt.ch('failure')} "
                                f"{fmt.ch(entry.kind)} {entry.service}"
                                for ix, entry in enumerate(action.entries)
                            ]
                        ),
                        "inline": False,
                    }

    def completed(self, result: ExecutionResult, attachments: list[str] = None) -> None:
        self._send_message(self._compose_completed(result))

        if attachments is not None:
            for attachment in attachments:
                self._send_attachment(attachment)
