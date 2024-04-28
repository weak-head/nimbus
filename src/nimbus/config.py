from __future__ import annotations

from os.path import abspath, exists, expanduser

from strictyaml import Bool, Enum, Int, Map, Optional, Seq, Str, load


class Config:
    """
    Config with support of '.' notation.
    """

    def __init__(self, config: dict):
        self._config = config

    def __getattr__(self, key):
        return self[key]

    def __getitem__(self, key):
        return Config._convert(self._config.get(key))

    def items(self):
        return self._config.items()

    @staticmethod
    def _convert(val):
        if isinstance(val, dict):
            return Config(val)
        if isinstance(val, list):
            return [Config._convert(v) for v in val]
        return val


def resolve_config(file_path: str = None) -> tuple[str | None, list[str]]:
    # Default search paths for the configuration location.
    # The order in the list defines the search and load priority.
    search_paths = [
        "~/.nimbus/config.yml",
        "~/.nimbus/config.yaml",
    ]
    if file_path:
        search_paths = [file_path]

    for candidate in search_paths:
        resolved_path = abspath(expanduser(candidate))
        if exists(resolved_path):
            return resolved_path, search_paths

    return None, search_paths


def load_config(file_path: str) -> Config:
    with open(file_path, mode="r", encoding="utf-8") as file:
        return Config(load(file.read(), schema()))


def schema() -> Map:
    return Map(
        {
            Optional("observability"): schema_observability(),
            "profiles": schema_profiles(),
            "commands": Seq(Str()),
        }
    )


def schema_observability() -> Map:
    return Map(
        {
            Optional("reports"): Map(
                {
                    "format": Enum(["txt"]),
                    "directory": Str(),
                }
            ),
            Optional("logs"): Map(
                {
                    "level": Enum(
                        [
                            "DEBUG",
                            "INFO",
                            "WARNING",
                            "ERROR",
                            "CRITICAL",
                        ]
                    ),
                    "stdout": Bool(),
                    "directory": Str(),
                }
            ),
            Optional("notifications"): Map(
                {
                    Optional("discord"): Map(
                        {
                            "webhook": Str(),
                            Optional("username"): Str(),
                            Optional("avatar_url"): Str(),
                        }
                    ),
                }
            ),
        }
    )


def schema_profiles() -> Map:
    return Map(
        {
            "archive": Seq(
                Map(
                    {
                        "name": Str(),
                        "provider": Str(),
                        Optional("password"): Str(),
                        Optional("recovery"): Int(),
                        Optional("compression"): Int(),
                    }
                )
            ),
            "upload": Seq(
                Map(
                    {
                        "name": Str(),
                        "provider": Str(),
                        "access_key": Str(),
                        "secret_key": Str(),
                        "bucket": Str(),
                        "storage_class": Enum(
                            [
                                "STANDARD",
                                "REDUCED_REDUNDANCY",
                                "STANDARD_IA",
                                "ONEZONE_IA ",
                                "INTELLIGENT_TIERING",
                                "DEEP_ARCHIVE",
                            ]
                        ),
                    }
                )
            ),
        }
    )
