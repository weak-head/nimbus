import os
from datetime import datetime as dt

import pytest
from mock import Mock, call, patch

from nimbuscli.core.archive.tar import TarArchiver
from tests.helpers import MockDateTime


class TestTarArchiver:

    @pytest.mark.parametrize(
        "compression",
        ["bz2", "gz", "xz", None],
    )
    def test_init(self, compression):
        archiver = TarArchiver(compression)
        assert archiver._compression == compression

        if compression is None:
            assert archiver.extension == "tar"
        else:
            assert archiver.extension == f"tar.{compression}"

    @pytest.mark.parametrize(
        "compression",
        ["value", "dif", "lz", "lzma", "lzop", "zstd"],
    )
    def test_init_failed_params(self, compression):
        with pytest.raises(ValueError):
            TarArchiver(compression)

    @patch("tarfile.open")
    @patch("os.walk")
    @patch("nimbuscli.core.archive.tar.datetime", MockDateTime)
    def test_archive(self, os_walk, tarfile_open):
        directory = "DIRECTORY_PATH/abc"
        archive = "archive/abc.tar.gz"
        started = dt(2024, 1, 1, 10, 00, 00)
        completed = dt(2024, 1, 1, 10, 30, 15)
        MockDateTime.now_returns(started, completed)

        tar_mock = Mock()
        tarfile_open.return_value.__enter__.return_value = tar_mock

        os_walk.return_value = [
            (directory, ["subA", "subB"], ["file1", "file2"]),
            (os.path.join(directory, "subA"), ["subAA"], ["fileA1", "fileA2"]),
            (os.path.join(directory, "subA", "subAA"), [], ["fileAA1"]),
            (os.path.join(directory, "subB"), ["subB"], ["fileB1", "fileB2"]),
        ]

        tar = TarArchiver("gz")
        res = tar.archive(directory, archive)

        assert res.started == started
        assert res.completed == completed
        assert res.directory == directory
        assert res.archive == archive

        tarfile_open.assert_called_with(archive, "w:gz")
        os_walk.assert_called_with(directory)
        tar_mock.add.assert_has_calls(
            [
                call(os.path.join(directory, "file1"), arcname="file1"),
                call(os.path.join(directory, "file2"), arcname="file2"),
                call(os.path.join(directory, "subA/fileA1"), arcname="subA/fileA1"),
                call(os.path.join(directory, "subA/fileA2"), arcname="subA/fileA2"),
                call(os.path.join(directory, "subA/subAA/fileAA1"), arcname="subA/subAA/fileAA1"),
                call(os.path.join(directory, "subB/fileB1"), arcname="subB/fileB1"),
                call(os.path.join(directory, "subB/fileB2"), arcname="subB/fileB2"),
            ]
        )
