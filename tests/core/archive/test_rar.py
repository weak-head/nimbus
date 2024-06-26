from datetime import datetime

import pytest
from mock import Mock, PropertyMock, call, patch

from nimbuscli.core.archive.rar import RarArchivalStatus, RarArchiver


class TestRarArchivalStatus:

    @pytest.mark.parametrize("directory", [True, False])
    @pytest.mark.parametrize("archive", [True, False])
    @pytest.mark.parametrize("success", [True, False])
    @pytest.mark.parametrize("exists", [True, False])
    @patch("os.path.exists")
    def test_success(self, mock_exists, directory, archive, success, exists):
        mock_exists.return_value = exists

        mock_proc = Mock()
        success_mock = PropertyMock(return_value=success)
        type(mock_proc).success = success_mock

        started_mock = PropertyMock(return_value=datetime(2024, 1, 1, 10, 30, 00))
        type(mock_proc).started = started_mock

        completed_mock = PropertyMock(return_value=datetime(2024, 1, 1, 10, 35, 10))
        type(mock_proc).completed = completed_mock

        fdr = "directory" if directory else None
        arc = "archive" if archive else None

        a = RarArchivalStatus(mock_proc, fdr, arc)

        assert a.success == all([directory, archive, success, exists])
        success_mock.assert_called_once()


class TestRarArchiver:

    @pytest.mark.parametrize("password", [None, "abc"])
    @pytest.mark.parametrize("compression", [None, 0, 1, 2, 3, 4, 5])
    @pytest.mark.parametrize("recovery", [None, 1, 3, 5, 100, 300])
    def test_init(self, password, compression, recovery):
        mock_runner = Mock()

        archiver = RarArchiver(
            mock_runner,
            password,
            compression,
            recovery,
        )

        assert archiver._runner == mock_runner
        assert archiver._password == password
        assert archiver._recovery == recovery
        assert archiver._compression == compression
        assert archiver.extension == "rar"

    def test_init_failed_runner(self):
        with pytest.raises(ValueError):
            RarArchiver(None, "abc", 3, 3)

    @pytest.mark.parametrize(
        ["password", "compression", "recovery"],
        [
            ["", 3, 3],
            [None, -1, 3],
            [None, 6, 3],
            [None, 3, -1],
            [None, 3, 1001],
        ],
    )
    def test_init_failed_params(self, password, compression, recovery):
        with pytest.raises(ValueError):
            RarArchiver(
                Mock(),
                password,
                compression,
                recovery,
            )

    @patch("os.path.exists")
    def test_archive(self, mock_exists):
        mock_exists.side_effect = [
            True,  # @log_on_end
            True,  # assert result.success
        ]

        mock_proc = Mock()
        mock_proc.success.return_value = True

        mock_runner = Mock()
        mock_runner.execute.return_value = mock_proc

        archiver = RarArchiver(mock_runner, "pwd")
        directory = "directory_path"
        archive = "archive_path"
        result = archiver.archive(directory, archive)

        mock_exists.assert_has_calls(
            [
                call(archive),  # called by @log_on_end
            ]
        )
        mock_runner.execute.assert_called_once()

        assert result.directory == directory
        assert result.archive == archive
        assert result.proc == mock_proc
        assert result.success

    @pytest.mark.parametrize("password", [None, "abc", "bbc3"])
    @pytest.mark.parametrize("compression", [None, 0, 1, 3, 5])
    @pytest.mark.parametrize("recovery", [None, 0, 1, 3, 33])
    def test__generate_cmd(self, password, compression, recovery):
        archiver = RarArchiver(
            Mock(),
            password,
            compression,
            recovery,
        )
        cmd = archiver._generate_cmd("directory123", "archive123.rar")

        assert "archive123.rar" == cmd[-2]
        assert "directory123" == cmd[-1]

        if password is None:
            assert f"-hp{password}" not in cmd
        else:
            assert f"-hp{password}" in cmd

        if compression is None:
            assert f"-m{compression}" not in cmd
        else:
            assert f"-m{compression}" in cmd

        if recovery is None:
            assert f"-rr{recovery}" not in cmd
        else:
            assert f"-rr{recovery}" in cmd
