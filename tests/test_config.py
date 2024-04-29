import pytest
from strictyaml import YAMLError, load

from nimbus.config import (
    Config,
    commands_schema,
    config_schema,
    observability_schema,
    profiles_schema,
)


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


def validate_schema(schema, yaml_snippet, expected_cfg):
    if expected_cfg is None:
        with pytest.raises(YAMLError):
            load(yaml_snippet, schema)
    else:
        parsed_cfg = load(yaml_snippet, schema)
        assert parsed_cfg == expected_cfg


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
def test_observability_schema(yaml_snippet, cfg):
    validate_schema(observability_schema(), yaml_snippet, cfg)


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
            archive:
            """,
            None,
        ],
        [
            """
            upload:
            """,
            None,
        ],
        [
            """
            archive:
            upload:
              - name: aws_store
                provider: aws
                access_key: XX
                secret_key: XXX
                bucket: aws.storage.bucket
                storage_class: STANDARD
              - name: aws_archival
                provider: aws
                access_key: XX
                secret_key: XXX
                bucket: aws.archival.bucket
                storage_class: DEEP_ARCHIVE
            """,
            None,
        ],
        [
            """
            archive:
              - name: rar_default
                provider: rar
              - name: rar_protected
                provider: rar
                password: SecretPwd
                recovery: 3
                compression: 1
            upload:
            """,
            None,
        ],
        [
            """
            archive:
              - name: rar_default
                provider: rar
            upload:
              - name: aws_store
                provider: aws
                access_key: XX
                secret_key: XXX
                bucket: aws.storage.bucket
                storage_class: STANDARD
            """,
            {
                "archive": [
                    {
                        "name": "rar_default",
                        "provider": "rar",
                    },
                ],
                "upload": [
                    {
                        "name": "aws_store",
                        "provider": "aws",
                        "access_key": "XX",
                        "secret_key": "XXX",
                        "bucket": "aws.storage.bucket",
                        "storage_class": "STANDARD",
                    },
                ],
            },
        ],
        [
            """
            archive:
              - name: rar_default
                provider: rar
              - name: rar_protected
                provider: rar
                password: SecretPwd
                recovery: 3
                compression: 1
            upload:
              - name: aws_store
                provider: aws
                access_key: XX
                secret_key: XXX
                bucket: aws.storage.bucket
                storage_class: STANDARD
              - name: aws_archival
                provider: aws
                access_key: XX
                secret_key: XXX
                bucket: aws.archival.bucket
                storage_class: DEEP_ARCHIVE
            """,
            {
                "archive": [
                    {
                        "name": "rar_default",
                        "provider": "rar",
                    },
                    {
                        "name": "rar_protected",
                        "provider": "rar",
                        "password": "SecretPwd",
                        "recovery": 3,
                        "compression": 1,
                    },
                ],
                "upload": [
                    {
                        "name": "aws_store",
                        "provider": "aws",
                        "access_key": "XX",
                        "secret_key": "XXX",
                        "bucket": "aws.storage.bucket",
                        "storage_class": "STANDARD",
                    },
                    {
                        "name": "aws_archival",
                        "provider": "aws",
                        "access_key": "XX",
                        "secret_key": "XXX",
                        "bucket": "aws.archival.bucket",
                        "storage_class": "DEEP_ARCHIVE",
                    },
                ],
            },
        ],
        [
            """
            archive:
              - name: rar_default
                provider: rar
              - name: rar_protected
                provider: rar
                password: SecretPwd
                recovery: 3
                compression: 1
                some_other_field: value
            upload:
              - name: aws_store
                provider: aws
                access_key: XX
                secret_key: XXX
                bucket: aws.storage.bucket
                storage_class: STANDARD
              - name: aws_archival
                provider: aws
                access_key: XX
                secret_key: XXX
                bucket: aws.archival.bucket
                storage_class: DEEP_ARCHIVE
            """,
            None,
        ],
        [
            """
            archive:
              - name: rar_default
                provider: rar
              - name: rar_protected
                provider: rar
                password: SecretPwd
                recovery: 3
                compression: 1
            upload:
              - name: aws_store
                provider: aws
                access_key: XX
                secret_key: XXX
                bucket: aws.storage.bucket
                storage_class: STANDARD
                some_other_field: value
              - name: aws_archival
                provider: aws
                access_key: XX
                secret_key: XXX
                bucket: aws.archival.bucket
                storage_class: DEEP_ARCHIVE
            """,
            None,
        ],
    ],
)
def test_profiles_schema(yaml_snippet, cfg):
    validate_schema(profiles_schema(), yaml_snippet, cfg)


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
            deploy:
            backup:
            """,
            None,
        ],
        [
            """
            deploy:
            backup:
              destination: /mnt/backups
              archive: rar_protected
              upload: aws_archival
              directories:
                apps:
                  - /mnt/ssd/apps/gitlab
                  - /mnt/ssd/apps/nextcloud
                  - /mnt/ssd/apps/plex
                media:
                  - ~/Music
                  - ~/Videos
                  - /mnt/hdd/music
                  - /mnt/hdd/books
                photos:
                  - ~/Photos
                  - /mnt/hdd/photos
                docs:
                  - ~/Documents
            """,
            None,
        ],
        [
            """
            deploy:
              services:
                - ~/services
                - /mnt/ssd/services
              secrets:
              - service: "*"
                environment:
                  UID: 1001
                  GID: 1001
                  TZ: America/New_York
                  SMTP_SERVER: smtp.server.com
                  SMTP_PORT: 587
                  SMTP_USERNAME: username
                  SMTP_PASSWORD: password
                  SMTP_DOMAIN: domain.com
              - service: "git*"
                environment:
                  UID: 1002
                  GID: 1002
              - service: "gitlab"
                environment:
                  GITLAB_HTTP_PORT: 8080
                  GITLAB_SSH_PORT: 8022
            backup:
            """,
            None,
        ],
        [
            """
            deploy:
              services:
                - ~/services
            backup:
              destination: /mnt/backups
              archive: rar_protected
              directories:
                apps:
                  - /mnt/ssd/apps/gitlab
            """,
            {
                "deploy": {"services": ["~/services"]},
                "backup": {
                    "destination": "/mnt/backups",
                    "archive": "rar_protected",
                    "directories": {"apps": ["/mnt/ssd/apps/gitlab"]},
                },
            },
        ],
        [
            """
            deploy:
              services:
                - ~/services
            backup:
              destination: /mnt/backups
              archive: rar_protected
              upload: aws_archival
              directories:
                apps:
                  - /mnt/ssd/apps/gitlab
            """,
            {
                "deploy": {"services": ["~/services"]},
                "backup": {
                    "destination": "/mnt/backups",
                    "archive": "rar_protected",
                    "upload": "aws_archival",
                    "directories": {"apps": ["/mnt/ssd/apps/gitlab"]},
                },
            },
        ],
        [
            """
            deploy:
              services:
                - ~/services
            backup:
              destination: /mnt/backups
              upload: aws_archival
              directories:
                apps:
                  - /mnt/ssd/apps/gitlab
            """,
            None,
        ],
        [
            """
            deploy:
              services:
                - ~/services
                - /mnt/ssd/services
              secrets:
              - service: "*"
                environment:
                  UID: 1001
                  GID: 1001
                  TZ: America/New_York
                  SMTP_SERVER: smtp.server.com
                  SMTP_PORT: 587
                  SMTP_USERNAME: username
                  SMTP_PASSWORD: password
                  SMTP_DOMAIN: domain.com
              - service: "git*"
                environment:
                  UID: 1002
                  GID: 1002
              - service: "gitlab"
                environment:
                  GITLAB_HTTP_PORT: 8080
                  GITLAB_SSH_PORT: 8022
            backup:
              destination: /mnt/backups
              archive: rar_protected
              upload: aws_archival
              directories:
                apps:
                  - /mnt/ssd/apps/gitlab
                  - /mnt/ssd/apps/nextcloud
                  - /mnt/ssd/apps/plex
                media:
                  - ~/Music
                  - ~/Videos
                  - /mnt/hdd/music
                  - /mnt/hdd/books
                photos:
                  - ~/Photos
                  - /mnt/hdd/photos
                docs:
                  - ~/Documents
            """,
            {
                "deploy": {
                    "services": [
                        "~/services",
                        "/mnt/ssd/services",
                    ],
                    "secrets": [
                        {
                            "service": "*",
                            "environment": {
                                "UID": "1001",
                                "GID": "1001",
                                "TZ": "America/New_York",
                                "SMTP_SERVER": "smtp.server.com",
                                "SMTP_PORT": "587",
                                "SMTP_USERNAME": "username",
                                "SMTP_PASSWORD": "password",
                                "SMTP_DOMAIN": "domain.com",
                            },
                        },
                        {
                            "service": "git*",
                            "environment": {
                                "UID": "1002",
                                "GID": "1002",
                            },
                        },
                        {
                            "service": "gitlab",
                            "environment": {
                                "GITLAB_HTTP_PORT": "8080",
                                "GITLAB_SSH_PORT": "8022",
                            },
                        },
                    ],
                },
                "backup": {
                    "destination": "/mnt/backups",
                    "archive": "rar_protected",
                    "upload": "aws_archival",
                    "directories": {
                        "apps": [
                            "/mnt/ssd/apps/gitlab",
                            "/mnt/ssd/apps/nextcloud",
                            "/mnt/ssd/apps/plex",
                        ],
                        "media": [
                            "~/Music",
                            "~/Videos",
                            "/mnt/hdd/music",
                            "/mnt/hdd/books",
                        ],
                        "photos": [
                            "~/Photos",
                            "/mnt/hdd/photos",
                        ],
                        "docs": [
                            "~/Documents",
                        ],
                    },
                },
            },
        ],
    ],
)
def test_commands_schema(yaml_snippet, cfg):
    validate_schema(commands_schema(), yaml_snippet, cfg)


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
            profiles:
              archive:
                - name: rar_default
                  provider: rar
              upload:
                - name: aws_store
                  provider: aws
                  access_key: XX
                  secret_key: XXX
                  bucket: aws.storage.bucket
                  storage_class: STANDARD
            commands:
              deploy:
                services:
                  - ~/services
              backup:
                destination: /mnt/backups
                archive: rar_protected
                upload: aws_archival
                directories:
                  apps:
                    - /mnt/ssd/apps/gitlab
            """,
            {
                "profiles": {
                    "archive": [
                        {
                            "name": "rar_default",
                            "provider": "rar",
                        },
                    ],
                    "upload": [
                        {
                            "name": "aws_store",
                            "provider": "aws",
                            "access_key": "XX",
                            "secret_key": "XXX",
                            "bucket": "aws.storage.bucket",
                            "storage_class": "STANDARD",
                        },
                    ],
                },
                "commands": {
                    "deploy": {"services": ["~/services"]},
                    "backup": {
                        "destination": "/mnt/backups",
                        "archive": "rar_protected",
                        "upload": "aws_archival",
                        "directories": {"apps": ["/mnt/ssd/apps/gitlab"]},
                    },
                },
            },
        ],
        [
            """
            observability:
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
            profiles:
              archive:
                - name: rar_default
                  provider: rar
              upload:
                - name: aws_store
                  provider: aws
                  access_key: XX
                  secret_key: XXX
                  bucket: aws.storage.bucket
                  storage_class: STANDARD
            commands:
              deploy:
                services:
                  - ~/services
              backup:
                destination: /mnt/backups
                archive: rar_protected
                upload: aws_archival
                directories:
                  apps:
                    - /mnt/ssd/apps/gitlab
            """,
            {
                "observability": {
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
                "profiles": {
                    "archive": [
                        {
                            "name": "rar_default",
                            "provider": "rar",
                        },
                    ],
                    "upload": [
                        {
                            "name": "aws_store",
                            "provider": "aws",
                            "access_key": "XX",
                            "secret_key": "XXX",
                            "bucket": "aws.storage.bucket",
                            "storage_class": "STANDARD",
                        },
                    ],
                },
                "commands": {
                    "deploy": {"services": ["~/services"]},
                    "backup": {
                        "destination": "/mnt/backups",
                        "archive": "rar_protected",
                        "upload": "aws_archival",
                        "directories": {"apps": ["/mnt/ssd/apps/gitlab"]},
                    },
                },
            },
        ],
    ],
)
def test_config_schema(yaml_snippet, cfg):
    validate_schema(config_schema(), yaml_snippet, cfg)
