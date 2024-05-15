import os
import zipfile
from datetime import datetime as dt

import pytest
from mock import Mock, call, patch

from nimbuscli.core.archive.zip import ZipArchiver
from tests.helpers import MockDateTime


class TestZipArchiver:

    @pytest.mark.parametrize(
        ["compression", "expected"],
        [
            ("bz2", zipfile.ZIP_BZIP2),
            ("gz", zipfile.ZIP_DEFLATED),
            ("xz", zipfile.ZIP_LZMA),
            (None, zipfile.ZIP_STORED),
        ],
    )
    def test_init(self, compression, expected):
        archiver = ZipArchiver(compression)
        assert archiver.extension == "zip"
        assert archiver._compression == expected

    @pytest.mark.parametrize(
        "compression",
        ["value", "dif", "lz", "lzma", "lzop", "zstd"],
    )
    def test_init_failed_params(self, compression):
        with pytest.raises(ValueError):
            ZipArchiver(compression)

    @patch("zipfile.ZipFile")
    @patch("os.walk")
    @patch("nimbuscli.core.archive.archiver.datetime", MockDateTime)
    def test_archive(self, os_walk, zipfile_mock):
        directory = "DIRECTORY_PATH/abc"
        archive = "archive/abc.zip"
        started = dt(2024, 1, 1, 10, 00, 00)
        completed = dt(2024, 1, 1, 10, 30, 15)
        MockDateTime.now_returns(started, completed)

        zip_mock = Mock()
        zipfile_mock.return_value.__enter__.return_value = zip_mock

        os_walk.return_value = [
            (directory, ["subA", "subB"], ["file1", "file2"]),
            (os.path.join(directory, "subA"), ["subAA"], ["fileA1", "fileA2"]),
            (os.path.join(directory, "subA", "subAA"), [], ["fileAA1"]),
            (os.path.join(directory, "subB"), ["subB"], ["fileB1", "fileB2"]),
        ]

        zipf = ZipArchiver("gz")
        res = zipf.archive(directory, archive)

        assert res.started == started
        assert res.completed == completed
        assert res.directory == directory
        assert res.archive == archive
        assert res.exception is None

        zipfile_mock.assert_called_with(archive, "w", zipfile.ZIP_DEFLATED)
        os_walk.assert_called_with(directory)
        zip_mock.write.assert_has_calls(
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
