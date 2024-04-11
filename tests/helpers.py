from datetime import datetime


class MockDateTime(datetime):
    """
    Because we cannot monkeypatch and mock
    the native C calls, we can substitute the
    implementation of the entire class in the module.
    """

    @staticmethod
    def now_returns(*values):
        MockDateTime.__values = list(values)
        MockDateTime.__next = 0

    @classmethod
    def now(cls, tz=None):
        if MockDateTime.__next >= len(MockDateTime.__values):
            raise ValueError("No more returns left")
        v = MockDateTime.__values[MockDateTime.__next]
        MockDateTime.__next += 1
        return v
