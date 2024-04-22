from typing import Iterator

import pytest

from nimbus.provider.secrets import Secret, Secrets, SecretsProvider


class TestSecretsProvider:

    @pytest.mark.parametrize(
        ["secrets", "service", "matches"],
        [
            [[], "srv", {}],
            [
                [
                    {
                        "service": "*",
                        "environment": {
                            "UID": 1000,
                            "GID": 1000,
                        },
                    },
                    {
                        "service": "cloud",
                        "environment": {
                            "HTTP_PORT_1": 80,
                            "HTTP_PORT_2": 443,
                        },
                    },
                ],
                "cloud",
                {
                    "*": {
                        "UID": "1000",
                        "GID": "1000",
                    },
                    "cloud": {
                        "HTTP_PORT_1": "80",
                        "HTTP_PORT_2": "443",
                    },
                },
            ],
            [
                [
                    {
                        "service": "*",
                        "environment": {
                            "UID": 1000,
                            "GID": 1000,
                        },
                    },
                    {
                        "service": "cloud",
                        "environment": {
                            "HTTP_PORT_1": 80,
                            "HTTP_PORT_2": 443,
                        },
                    },
                ],
                "apps",
                {
                    "*": {
                        "UID": "1000",
                        "GID": "1000",
                    },
                },
            ],
            [
                [
                    {
                        "service": "apps",
                        "environment": {
                            "UID": 1000,
                            "GID": 1000,
                        },
                    },
                    {
                        "service": "cloud",
                        "environment": {
                            "HTTP_PORT_1": 80,
                            "HTTP_PORT_2": 443,
                        },
                    },
                ],
                "apps",
                {
                    "apps": {
                        "UID": "1000",
                        "GID": "1000",
                    },
                },
            ],
            [
                [
                    {
                        "service": "apps",
                        "environment": {
                            "UID": 1000,
                            "GID": 1000,
                        },
                    },
                    {
                        "service": "cloud",
                        "environment": {
                            "HTTP_PORT_1": 80,
                            "HTTP_PORT_2": 443,
                        },
                    },
                ],
                "other",
                {},
            ],
        ],
    )
    def test_env(self, secrets, service, matches):
        p = SecretsProvider(secrets)
        matched = list(p.env(service))
        result = {s.selector: s.values for s in matched}

        assert len(result) == len(matches)

        for selector, env in matches.items():
            assert selector in result

            for env_name, env_value in env.items():
                assert result[selector][env_name] == env_value


class FakeProvider:

    def __init__(self, secrets):
        self._secrets = secrets

    def env(self, service: str) -> Iterator[Secret]:
        self._env_called_with = service
        for selector, env in self._secrets.items():
            yield Secret(selector, env)


class TestSecrets:

    @pytest.mark.parametrize(
        ["secrets", "expected"],
        [
            [{}, {}],
            [
                {
                    "*": {"PORT": "80", "UID": "1001"},
                },
                {
                    "PORT": "80",
                    "UID": "1001",
                },
            ],
            [
                {
                    "*": {"PORT": "80", "UID": "1001"},
                    "s": {"PORT": "77", "GID": "1001"},
                },
                {
                    "PORT": "77",
                    "UID": "1001",
                    "GID": "1001",
                },
            ],
            [
                {
                    "*": {"PORT": "80", "UID": "1001"},
                    "s": {"PORT": "77", "GID": "1001"},
                    "d": {"PORT": "443", "UID": "1002"},
                },
                {
                    "PORT": "443",
                    "UID": "1002",
                    "GID": "1001",
                },
            ],
            [
                {
                    "*": {"PORT": "80", "UID": "1001"},
                    "s": {"PORT": "77", "GID": "1001"},
                    "d": {"PORT": "443", "UID": "1002"},
                    "f": {"NAME": "adf", "URL": "http"},
                },
                {
                    "PORT": "443",
                    "UID": "1002",
                    "GID": "1001",
                    "NAME": "adf",
                    "URL": "http",
                },
            ],
        ],
    )
    def test_env(self, secrets, expected):
        p = FakeProvider(secrets)
        s = Secrets(p)

        env = s.env("SERVICE_NAME")

        assert p._env_called_with == "SERVICE_NAME"
        assert len(env) == len(expected)
        assert env == expected
