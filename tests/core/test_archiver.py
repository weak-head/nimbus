import pytest
from mock import Mock, PropertyMock, call, patch

from nimbus.core.archiver import ArchivalStatus, RarArchiver


class TestRarArchiver:

    def test_init(self):
        mock_runner = Mock()
        password = "pwd"

        archiver = RarArchiver(
            mock_runner,
            password,
        )

        assert archiver._runner == mock_runner
        assert archiver._password == password

    def test_init_failed(self):
        with pytest.raises(ValueError):
            RarArchiver(
                None,
                "abc",
            )

    @patch("os.path.dirname")
    @patch("os.path.exists")
    @patch("os.makedirs")
    def test_archive(
        self,
        mock_makedirs,
        mock_exists,
        mock_dirname,
    ):
        mock_dirname.return_value = "DIRNAME"
        mock_exists.side_effect = [
            False,  # DIRNAME
            True,  # @log_on_end
            True,  # assert result.success
        ]
        mock_makedirs.return_value = True

        mock_proc = Mock()
        mock_proc.success.return_value = True
        mock_runner = Mock()
        mock_runner.execute.return_value = mock_proc
        password = "pwd"

        archiver = RarArchiver(mock_runner, password)

        folder = "folder_path"
        archive = "archive_path"

        result = archiver.archive(folder, archive)

        mock_dirname.assert_called_with(archive)
        mock_exists.assert_has_calls(
            [
                # called by directory check condition
                call("DIRNAME"),
                # called by @log_on_end(logging.INFO, "Archived [{result.success!s}]: {archive!s}")
                call(archive),
            ]
        )
        mock_makedirs.assert_called_with("DIRNAME", exist_ok=True)
        mock_runner.execute.assert_called_once()

        assert result.folder == folder
        assert result.archive == archive
        assert result.proc == mock_proc
        assert result.success


class TestArchivalStatus:

    @pytest.mark.parametrize("folder", [True, False])
    @pytest.mark.parametrize("archive", [True, False])
    @pytest.mark.parametrize("success", [True, False])
    @pytest.mark.parametrize("exists", [True, False])
    def test_success(self, folder, archive, success, exists):
        patcher = patch("os.path.exists")
        mock_exists = patcher.start()
        mock_exists.return_value = exists

        mock_proc = Mock()
        success_mock = PropertyMock(return_value=success)
        type(mock_proc).success = success_mock

        fdr = "folder" if folder else None
        arc = "archive" if archive else None

        a = ArchivalStatus(mock_proc, fdr, arc)

        assert a.success == all([folder, archive, success, exists])
        success_mock.assert_called_once()
