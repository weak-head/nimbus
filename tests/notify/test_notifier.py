import pytest
from mock import Mock

from nimbuscli.notify.notifier import CompositeNotifier


class TestCompositeNotifier:

    def test_init(self):
        notifier = CompositeNotifier(None)
        assert notifier._notifiers == []

        notifier = CompositeNotifier([])
        assert notifier._notifiers == []

        mock_notifiers = [Mock()]
        notifier = CompositeNotifier(mock_notifiers)
        assert notifier._notifiers == mock_notifiers

    @pytest.mark.parametrize("num_mocks", [0, 1, 3, 10, 100])
    def test_completed(self, num_mocks):
        mock_result = Mock()
        mock_attachements = [Mock()]
        mocks = []
        for _ in range(num_mocks):
            mocks.append(Mock())

        notifier = CompositeNotifier(mocks)
        notifier.completed(mock_result, mock_attachements)

        assert len(notifier._notifiers) == len(mocks)
        for mock in mocks:
            mock.completed.assert_called_with(mock_result, mock_attachements)
