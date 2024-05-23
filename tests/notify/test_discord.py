import pytest

from nimbuscli.notify.discord import DiscordNotifier


class TestDiscordNotifier:

    @pytest.mark.parametrize("webhook", ["abc", "bcd"])
    @pytest.mark.parametrize("username", [None, "a", "b"])
    @pytest.mark.parametrize("avatar", [None, "a", "b"])
    def test_init(self, webhook, username, avatar):
        notifier = DiscordNotifier(webhook, username, avatar)
        assert notifier._webhook == webhook
        assert notifier._username == username
        assert notifier._avatar_url == avatar

    @pytest.mark.parametrize("webhook", [None, ""])
    def test_init_failed_runner(self, webhook):
        with pytest.raises(ValueError):
            DiscordNotifier(webhook)
