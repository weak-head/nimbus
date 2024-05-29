from mock import Mock, PropertyMock

from nimbuscli.notify.discord import DiscordNotifier
from nimbuscli.notify.factory import CfgNotifierFactory
from nimbuscli.notify.notifier import CompositeNotifier


class TestCfgNotifierFactory:

    def test_create_notifier(self):
        mock_config = Mock()
        factory = CfgNotifierFactory(mock_config)

        # -- None
        mock_config.nested.return_value = None

        notifier = factory.create_notifier()

        assert isinstance(notifier, CompositeNotifier)
        assert len(notifier._notifiers) == 0
        mock_config.nested.assert_called_with("observability.notifications.discord")

        # -- Discord
        mock_discord_cfg = Mock()
        type(mock_discord_cfg).webhook = PropertyMock(return_value="hook")
        type(mock_discord_cfg).username = PropertyMock(return_value="user")
        type(mock_discord_cfg).avatar_url = PropertyMock(return_value="url")
        mock_config.nested.return_value = mock_discord_cfg

        notifier = factory.create_notifier()

        assert isinstance(notifier, CompositeNotifier)
        assert len(notifier._notifiers) == 1
        assert isinstance(notifier._notifiers[0], DiscordNotifier)

        discord_notifier: DiscordNotifier = notifier._notifiers[0]
        assert discord_notifier._webhook == "hook"
        assert discord_notifier._username == "user"
        assert discord_notifier._avatar_url == "url"
        mock_config.nested.assert_called_with("observability.notifications.discord")
