from datetime import datetime

import pytest
from mock import patch

from nimbuscli.core.archive.archiver import ArchivalStatus


class TestArchivalStatus:

    @pytest.mark.parametrize("directory", [True, False])
    @pytest.mark.parametrize("archive", [True, False])
    @pytest.mark.parametrize("exists", [True, False])
    @pytest.mark.parametrize("started", [datetime(2024, 1, 1, 10, 30, 00), None])
    @pytest.mark.parametrize("completed", [datetime(2024, 1, 1, 10, 35, 10), None])
    def test_success(self, directory, archive, exists, started, completed):
        patcher = patch("os.path.exists")
        mock_exists = patcher.start()
        mock_exists.return_value = exists

        fdr = "directory" if directory else None
        arc = "archive" if archive else None

        a = ArchivalStatus(fdr, arc, started, completed)

        assert a.success == all([directory, archive, exists, started, completed])
