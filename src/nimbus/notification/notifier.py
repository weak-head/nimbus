from abc import ABC, abstractmethod

import requests


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

    def __init__(self, webhook: str, username: str = None, avatar_url: str = None) -> None:
        self._webhook = webhook
        self._username = username
        self._avatar_url = avatar_url

    def __repr__(self) -> str:
        params = [
            f"webhook='{self._webhook}'",
        ]
        return "DiscordNotifier(" + ", ".join(params) + ")"

    def notify(self) -> None:

        # https://discord.com/developers/docs/resources/webhook
        data = {
            "content": "Hello, world!",
            # "username": "nimbus",
            # "avatar_url": "https://example.com/avatar.png",
            "embeds": [
                {
                    "title": "New Message",
                    "description": "There's a new message in the chat room!",
                    "color": 16711680,  # Colors are in decimal format
                }
            ],
        }

        response = requests.post(self._webhook, json=data, timeout=3000)

        print(response.status_code)
        print(response.content)
