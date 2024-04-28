import pytest
from strictyaml import YAMLError, load

from nimbus.config import schema_observability


@pytest.mark.parametrize(
    ["yaml_snippet", "cfg"],
    [
        [
            """
            """,
            None,
        ],
        [
            """
            reports:
            """,
            None,
        ],
        [
            """
            reports:
                format: other
                directory: ~/reports
            """,
            None,
        ],
        [
            """
            reports:
                format: txt
                directory: ~/reports
            """,
            {"reports": {"format": "txt", "directory": "~/reports"}},
        ],
        [
            """
            reports:
                format: txt
                directory: ~/reports
                some_other_field: value
            """,
            None,
        ],
        [
            """
            logs:
                level: DEBUG
                stdout: true
                directory: ~/logs
            """,
            {
                "logs": {"level": "DEBUG", "stdout": True, "directory": "~/logs"},
            },
        ],
        [
            """
            reports:
                format: txt
                directory: ~/reports
            logs:
                level: DEBUG
                stdout: true
                directory: ~/logs
            """,
            {
                "reports": {"format": "txt", "directory": "~/reports"},
                "logs": {"level": "DEBUG", "stdout": True, "directory": "~/logs"},
            },
        ],
        [
            """
            reports:
                format: txt
                directory: ~/reports
            logs:
                level: DEBUG
                directory: ~/logs
            """,
            None,
        ],
        [
            """
            reports:
                format: txt
                directory: ~/reports
            logs:
                level: value
                stdout: true
                directory: ~/logs
            """,
            None,
        ],
        [
            """
            logs:
                level: DEBUG
                stdout: true
                directory: ~/logs
            notifications:
                discord:
                    webhook: http://hook.url
            """,
            {
                "logs": {"level": "DEBUG", "stdout": True, "directory": "~/logs"},
                "notifications": {"discord": {"webhook": "http://hook.url"}},
            },
        ],
        [
            """
            reports:
                format: txt
                directory: ~/reports
            logs:
                level: DEBUG
                stdout: true
                directory: ~/logs
            notifications:
                discord:
                    webhook: http://hook.url
            """,
            {
                "reports": {"format": "txt", "directory": "~/reports"},
                "logs": {"level": "DEBUG", "stdout": True, "directory": "~/logs"},
                "notifications": {"discord": {"webhook": "http://hook.url"}},
            },
        ],
        [
            """
            reports:
                format: txt
                directory: ~/reports
            logs:
                level: DEBUG
                stdout: true
                directory: ~/logs
            notifications:
                discord:
            """,
            None,
        ],
        [
            """
            reports:
                format: txt
                directory: ~/reports
            logs:
                level: DEBUG
                stdout: true
                directory: ~/logs
            notifications:
            """,
            None,
        ],
        [
            """
            reports:
                format: txt
                directory: ~/reports
            logs:
                level: DEBUG
                stdout: true
                directory: ~/logs
            notifications:
                discord:
                    webhook: http://hook.url
                    username: name
                    avatar_url: http://avatar.url
            """,
            {
                "reports": {"format": "txt", "directory": "~/reports"},
                "logs": {"level": "DEBUG", "stdout": True, "directory": "~/logs"},
                "notifications": {
                    "discord": {
                        "webhook": "http://hook.url",
                        "username": "name",
                        "avatar_url": "http://avatar.url",
                    }
                },
            },
        ],
        [
            """
            reports:
                format: txt
                directory: ~/reports
            logs:
                level: DEBUG
                stdout: true
                directory: ~/logs
            notifications:
                discord:
                    username: name
                    avatar_url: http://avatar.url
            """,
            None,
        ],
    ],
)
def test_schema_observability(yaml_snippet, cfg):
    try:
        validated_data = load(yaml_snippet, schema_observability())
        assert validated_data == cfg
    except YAMLError:
        assert cfg is None
