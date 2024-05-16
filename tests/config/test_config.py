import pytest

from nimbuscli.config import Config


class TestConfig:

    @pytest.mark.parametrize(
        ["config", "path", "expected"],
        [
            [{}, "", None],
            [{}, "a.b.c.d", None],
            [{"foo": {"bar": {"baz": 17}}}, "foo.bar.foo", None],
            [{"foo": {"bar": {"baz": 17}}}, "foo.foo.baz", None],
            [{"foo": {"bar": {"baz": 17}}}, "baz.foo.baz", None],
            [{"foo": {"bar": {"baz": 17}}}, "foo.bar.baz", 17],
            [{"foo": {"bar": {"baz": 17, "buz": 22}}}, "foo.bar", {"baz": 17, "buz": 22}],
            [{"foo": {"bar": {"bur": {"baz": 17, "buz": 22}}}}, "foo.bar.bur", {"baz": 17, "buz": 22}],
            [{"foo": {"bar": {"bur": {"baz": 17, "buz": 22}}}}, "foo.bar.bur.biz.fix", None],
            [{"foo": {"bar": {"bur": {"baz": 17, "buz": ["a", "b", "c"]}}}}, "foo.bar.bur.buz", ["a", "b", "c"]],
            [{"foo": {"bar": {"bur": {"baz": 17, "buz": ["a", "b", "c"]}}}}, "", None],
        ],
    )
    def test_nested(self, config, path, expected):
        cfg = Config(config)
        assert cfg.nested(path) == expected

    @pytest.mark.parametrize(
        "config",
        [
            {},
            {"foo": 123},
            {"foo": 123, "bar": 233},
            {"foo": 123, "bar": {"buz": 12}},
        ],
    )
    def test_items(self, config):
        cfg = Config(config)
        assert cfg.items() == config.items()
