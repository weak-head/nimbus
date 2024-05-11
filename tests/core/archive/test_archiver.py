import pytest
from mock import Mock, PropertyMock, patch

from nimbuscli.core.archive import ArchivalStatus


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
