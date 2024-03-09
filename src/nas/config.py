from __future__ import annotations

import os.path

import yaml


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

    @staticmethod
    def load(file_path: str = None) -> Config:
        """
        Load configuration from file.
        When the file path is omitted, the default search paths are used.
        """

        # Default search paths for the configuration location.
        # The order in the list defines the search and load priority.
        search_paths = [
            "~/.nas/config.yml",
            "~/.nas/config.yaml",
        ]

        if file_path:
            search_paths = [file_path]

        for candidate in search_paths:
            resolved_path = os.path.abspath(os.path.expanduser(candidate))

            if os.path.exists(resolved_path):
                with open(resolved_path, mode="r", encoding="utf-8") as file:
                    return Config(yaml.safe_load(file))

        return None
