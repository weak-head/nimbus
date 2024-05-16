import glob
import json
import os

import pytest
from strictyaml import Map, YAMLError, load

from nimbuscli.config.schema import commands, observability, profiles, schema


def validate(config_schema, yaml_snippet, expected_cfg):
    if expected_cfg is None:
        with pytest.raises(YAMLError):
            load(yaml_snippet, config_schema)
    else:
        parsed_cfg = load(yaml_snippet, config_schema)
        assert parsed_cfg == expected_cfg


def validatef(config_schema: Map, file_path: str):
    with open(file_path) as yaml_file:
        yaml_snippet = yaml_file.read().strip()
        expected_cfg = None

        # Search for the '.json' pair.
        # If the corresponding '.json' pair doesn't exist,
        # we expect the yaml to be invalid and a
        # YAMLError exception to be generated.
        # Otherwise the json file contains the valid config.
        json_path = os.path.splitext(file_path)[0] + ".json"
        if os.path.exists(json_path):
            with open(json_path) as json_file:
                expected_cfg = json_file.read().strip()

            parsed_cfg = load(yaml_snippet, config_schema)

            # Validate parsed YAML matches the expected config
            assert parsed_cfg.data == json.loads(expected_cfg)
        else:
            with pytest.raises(YAMLError):
                load(yaml_snippet, config_schema)


def discover(directory: str) -> list[str]:
    test_dir = os.path.splitext(__file__)[0]
    root_dir = os.path.join(test_dir, directory)
    return [
        os.path.join(root_dir, p)
        for p in glob.glob(
            "**/*.yaml",
            root_dir=root_dir,
            recursive=True,
        )
    ]


def pytest_generate_tests(metafunc):
    if "observability_filename" in metafunc.fixturenames:
        metafunc.parametrize(
            "observability_filename",
            discover("sections/observability"),
        )
    if "profiles_filename" in metafunc.fixturenames:
        metafunc.parametrize(
            "profiles_filename",
            discover("sections/profiles"),
        )


def test_observability(observability_filename):
    validatef(observability(), observability_filename)


def test_profiles(profiles_filename):
    validatef(profiles(), profiles_filename)


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
    validate(commands(), yaml_snippet, cfg)


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
                  storage: STANDARD
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
                            "storage": "STANDARD",
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
                  storage: STANDARD
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
                            "storage": "STANDARD",
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
    validate(schema(), yaml_snippet, cfg)
