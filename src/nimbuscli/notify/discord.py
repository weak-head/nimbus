from datetime import datetime
from typing import Iterator

import requests

import nimbuscli.report.format as fmt
from nimbuscli.cmd import ExecutionResult
from nimbuscli.cmd.backup import BackupActionResult, UploadActionResult
from nimbuscli.cmd.deploy import DeploymentActionResult
from nimbuscli.notify.notifier import Notifier


class DiscordNotifier(Notifier):
    """
    Sends notifications to a Discord channel.
    """

    _FAILURE = 0xFF0000
    _SUCCESS = 0x00FF00

    def __init__(self, webhook: str, username: str = None, avatar_url: str = None) -> None:
        """
        Creates a new instance of the DiscordNotifier.

        :param webhook: Discord webhook url.
        :param username: Overwrite username (optional).
        :param avatar_url: Overwrite avatar (optional).
        """
        if not webhook:
            raise ValueError("The webhook cannot be None or empty.")

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

    def completed(self, result: ExecutionResult, attachments: list[str] = None) -> None:
        requests.post(self._webhook, json=self.compose_request(result), timeout=3_000)

        if not attachments:
            return

        for attachment in attachments:
            with open(attachment, "rb") as file:
                requests.post(self._webhook, files={"file": file}, timeout=10_000)

    def compose_request(self, result: ExecutionResult) -> dict:
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
            *self._execution_details(result),
        ]

        data["embeds"] = [event]
        return data

    def _execution_details(self, result: ExecutionResult) -> Iterator[dict]:
        for action in result.actions:
            match action:
                case DeploymentActionResult():
                    yield self._deployment_details(action)
                case BackupActionResult():
                    yield self._backup_details(action)
                case UploadActionResult():
                    yield self._upload_details(action)

    def _deployment_details(self, action: DeploymentActionResult) -> dict:
        return {
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

    def _backup_details(self, action: BackupActionResult) -> dict:
        return {
            "name": f"{fmt.ch('backup')} Backups",
            "value": "\n".join(
                [
                    f"{ix:02d}. "
                    f"{fmt.ch('success') if entry.success else fmt.ch('failure')} "
                    f"{fmt.ch('directory')} {entry.directory}"
                    for ix, entry in enumerate(action.entries)
                ]
            ),
            "inline": False,
        }

    def _upload_details(self, action: UploadActionResult) -> dict:
        return {
            "name": f"{fmt.ch('upload')} Uploads",
            "value": "\n".join(
                [
                    f"{ix:02d}. "
                    f"{fmt.ch('success') if entry.success else fmt.ch('failure')} "
                    f"{fmt.ch('archive')} {entry.upload.key}"
                    for ix, entry in enumerate(action.entries)
                ]
            ),
            "inline": False,
        }
