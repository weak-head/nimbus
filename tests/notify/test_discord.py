import pytest
from mock import Mock, call, patch

from nimbuscli.cmd import ExecutionResult
from nimbuscli.cmd.backup import BackupActionResult, UploadActionResult
from nimbuscli.cmd.deploy import DeploymentActionResult
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

    @pytest.mark.parametrize("files", [None, [], ["a"], ["a", "b", "c", "d", "e"]])
    @patch("requests.post")
    @patch("nimbuscli.notify.discord.open")
    def test_completed(self, mock_open, mock_post, files):
        effects, effects_map = [], {}
        if files:
            for f in files:
                effects_map[f] = Mock()
                effects.append(effects_map[f])

        mock_open.return_value.__enter__.side_effect = effects

        notifier = DiscordNotifier("webhook_url")
        notifier.compose_request = Mock()
        notifier.compose_request.return_value = "REQUEST"

        result = ExecutionResult("cmd")
        notifier.completed(result, files)

        notifier.compose_request.assert_called_with(result)

        calls = [call("webhook_url", json="REQUEST", timeout=3_000)]
        if files:
            calls.extend(call("webhook_url", files={"file": effects_map[f]}, timeout=10_000) for f in files)
        mock_post.assert_has_calls(calls)

    def test_compose_request(self):
        pass

    @pytest.mark.parametrize(
        "actions",
        [
            [],
            [DeploymentActionResult("")],
            [BackupActionResult("")],
            [UploadActionResult("")],
            [DeploymentActionResult(""), BackupActionResult("")],
            [DeploymentActionResult(""), BackupActionResult(""), UploadActionResult("")],
            [BackupActionResult(""), UploadActionResult("")],
        ],
    )
    def test_execution_details(self, actions):
        res = ExecutionResult("")
        res.actions = actions

        notifier = DiscordNotifier("webhook_url")
        notifier._deployment_details = Mock()
        notifier._backup_details = Mock()
        notifier._upload_details = Mock()
        details_map = {
            DeploymentActionResult: notifier._deployment_details,
            BackupActionResult: notifier._backup_details,
            UploadActionResult: notifier._upload_details,
        }

        _ = list(notifier._execution_details(res))

        for kind, mock_func in details_map.items():
            if num_calls := sum([isinstance(a, kind) for a in actions]):
                mock_func.assert_called()
                assert mock_func.call_count == num_calls
            else:
                mock_func.assert_not_called()

    def test_deployment_details(self):
        pass

    def test_backup_details(self):
        pass

    def test_upload_details(self):
        pass
