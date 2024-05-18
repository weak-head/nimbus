import pytest
from mock import Mock, PropertyMock, call, patch

from nimbuscli.config import Config, load_config, resolve_config


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
        ["config", "path", "name", "expected"],
        [
            [{}, "", "abc", None],
            [{}, "a.b.c.d", "d", None],
            [{"foo": {"bar": {"baz": 17, "buz": 22}}}, "foo.bar", "buz", None],
            [
                {
                    "foo": {
                        "bar": {
                            "bur": {
                                "baz": 17,
                                "buz": [
                                    {"name": "a", "val": 1},
                                    {"name": "b", "val": 3},
                                    {"name": "b", "val": 4},
                                ],
                            }
                        }
                    }
                },
                "foo.bar.bur.buz",
                "b",
                {"name": "b", "val": 3},
            ],
            [
                {
                    "foo": {
                        "bar": {
                            "bur": {
                                "baz": 17,
                                "buz": [
                                    {"name": "a", "val": 1},
                                    {"name": "b", "val": 3},
                                    {"name": "b", "val": 4},
                                ],
                            }
                        }
                    }
                },
                "foo.bar.bur.buz",
                "c",
                None,
            ],
        ],
    )
    def test_first(self, config, path, name, expected):
        cfg = Config(config)
        assert cfg.first(path, lambda x: x.name == name) == expected

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

    @pytest.mark.parametrize(
        "config",
        [
            {},
            {"foo": 123},
            {"foo": 123, "bar": 233},
            {"foo": 123, "bar": {"buz": 12}},
        ],
    )
    def test_eq(self, config):
        cfg = Config(config)

        assert cfg == config
        assert cfg == Config(config)
        assert cfg != 123


@pytest.mark.parametrize(
    ["file", "exists", "expected"],
    [
        [None, False, (None, ["~/.nimbus/config.yml", "~/.nimbus/config.yaml"])],
        ["/mnt/filepath", False, (None, ["/mnt/filepath"])],
        ["/mnt/filepath", True, ("/mnt/filepath", ["/mnt/filepath"])],
    ],
)
@patch("nimbuscli.config.config.expanduser")
@patch("nimbuscli.config.config.abspath")
@patch("nimbuscli.config.config.exists")
def test_resolve_config(mock_exists, mock_abspath, mock_expand, file, exists, expected):

    def _id(args):
        return args

    mock_exists.return_value = exists
    mock_abspath.side_effect = _id
    mock_expand.side_effect = _id

    assert resolve_config(file) == expected

    if file is None:
        mock_exists.assert_has_calls(
            [
                call("~/.nimbus/config.yml"),
                call("~/.nimbus/config.yaml"),
            ]
        )
        mock_abspath.assert_has_calls(
            [
                call("~/.nimbus/config.yml"),
                call("~/.nimbus/config.yaml"),
            ]
        )
        mock_expand.assert_has_calls(
            [
                call("~/.nimbus/config.yml"),
                call("~/.nimbus/config.yaml"),
            ]
        )
    else:
        mock_exists.assert_called_with(file)
        mock_abspath.assert_called_with(file)
        mock_expand.assert_called_with(file)


@patch("nimbuscli.config.config.open")
@patch("nimbuscli.config.config.load")
@patch("nimbuscli.config.config.schema")
def test_load_config(mock_schema, mock_load, mock_open):
    mock_open.__enter__.return_value = Mock()

    data = {"key": "value", "parent": {"child": "val1", "another": 13}}
    yaml_mock = Mock()
    type(yaml_mock).data = PropertyMock(return_value=data)
    mock_load.return_value = yaml_mock

    cfg = load_config("/mnt/file")
    assert cfg._config == data

    mock_open.assert_called_with("/mnt/file", mode="r", encoding="utf-8")
    mock_schema.assert_called_once()
