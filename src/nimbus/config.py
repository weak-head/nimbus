from __future__ import annotations

import os.path

import yaml

# Default search paths for the configuration location.
# The order in the list defines the search and load priority.
SEARCH_PATHS = (
    "~/.nimbus/config.yml",
    "~/.nimbus/config.yaml",
)


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
    search_paths = [file_path] if file_path else SEARCH_PATHS
    for candidate in search_paths:
        resolved_path = os.path.abspath(os.path.expanduser(candidate))
        if os.path.exists(resolved_path):
            return resolved_path, search_paths
    return None, search_paths


def safe_load(file_path: str) -> Config | None:
    try:
        with open(file_path, mode="r", encoding="utf-8") as file:
            return Config(yaml.safe_load(file))
    except yaml.error.YAMLError:
        return None
