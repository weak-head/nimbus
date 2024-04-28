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
        val = self._config.get(key)
        return Config(val) if isinstance(val, dict) else val

    def items(self):
        return self._config.items()


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
            "profiles": Int(),
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
