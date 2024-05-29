from datetime import datetime, timedelta

import pytest
from mock import Mock, call, patch

from nimbuscli.cmd import ExecutionResult
from nimbuscli.cmd.backup import (
    BackupActionResult,
    BackupEntry,
    UploadActionResult,
    UploadEntry,
)
from nimbuscli.cmd.deploy import DeploymentActionResult
from nimbuscli.core.deploy import OperationStatus
from nimbuscli.core.upload.uploader import UploadStatus
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
        notifier = DiscordNotifier("webhook_url")
        notifier._execution_details = Mock()
        notifier._execution_details.return_value = iter([])

        res = Mock(ExecutionResult("cmd"))
        res.success = True
        res.started = datetime(2000, 1, 1, 10, 30, 00)
        res.completed = datetime(2000, 1, 1, 10, 35, 00)
        res.elapsed = timedelta(minutes=5)

        d = notifier.compose_request(res)

        assert "username" not in d
        assert "avatar_url" not in d
        assert len(d["embeds"]) == 1
        event = d["embeds"][0]
        assert event["color"] == DiscordNotifier._SUCCESS
        notifier._execution_details.assert_called_once()

        res.success = False
        notifier._username = "username"
        notifier._avatar_url = "avatar"
        d = notifier.compose_request(res)

        assert d["username"] == "username"
        assert d["avatar_url"] == "avatar"
        assert len(d["embeds"]) == 1
        event = d["embeds"][0]
        assert event["color"] == DiscordNotifier._FAILURE

    @pytest.mark.parametrize(
        "actions",
        [
            [],
            ["value"],
            [DeploymentActionResult("")],
            [BackupActionResult("")],
            [UploadActionResult("")],
            [DeploymentActionResult(""), BackupActionResult("")],
            [DeploymentActionResult(""), BackupActionResult(""), UploadActionResult("")],
            [BackupActionResult(""), UploadActionResult("")],
            [UploadActionResult(""), UploadActionResult(""), UploadActionResult()],
            [BackupActionResult(""), BackupActionResult(""), BackupActionResult("")],
            [DeploymentActionResult(""), DeploymentActionResult(""), DeploymentActionResult("")],
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
        notifier = DiscordNotifier("webhook")
        dar = DeploymentActionResult("op", [])

        result = notifier._deployment_details(dar)
        assert result["value"] == ""

        dar.entries = [OperationStatus("srv", "op", "knd")]
        result = notifier._deployment_details(dar)
        assert result["value"] == "00. 👍 knd srv"

        dar.entries = [
            OperationStatus("srv1", "op1", "knd1"),
            OperationStatus("srv2", "op2", "knd2"),
        ]
        result = notifier._deployment_details(dar)
        assert result["value"] == "00. 👍 knd1 srv1\n01. 👍 knd2 srv2"

    def test_backup_details(self):
        notifier = DiscordNotifier("webhook")
        bar = BackupActionResult([])

        result = notifier._backup_details(bar)
        assert result["value"] == ""

        bar.entries = [BackupEntry("grp", "dir")]
        result = notifier._backup_details(bar)
        assert result["value"] == "00. ❌ 📁 dir"

        bar.entries = [
            BackupEntry("grp", "dir"),
            BackupEntry("grp2", "dir2"),
        ]
        result = notifier._backup_details(bar)
        assert result["value"] == "00. ❌ 📁 dir\n01. ❌ 📁 dir2"

    def test_upload_details(self):
        notifier = DiscordNotifier("webhook")
        uar = UploadActionResult([])

        result = notifier._upload_details(uar)
        assert result["value"] == ""

        ue = UploadEntry(BackupEntry("grp", "dir"))
        ue.upload = UploadStatus("file", "key")
        uar.entries = [ue]
        result = notifier._upload_details(uar)
        assert result["value"] == "00. ❌ 📦 key"
