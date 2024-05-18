from __future__ import annotations

from os.path import abspath, exists, expanduser
from typing import Any, Callable

from strictyaml import load

from nimbuscli.config.schema import schema


class Config:
    """
    Application configuration, that support retrieval of
    various settings through the use of dot-notation (`.`).
    """

    def __init__(self, config: dict):
        self._config = config

    def __getattr__(self, key):
        return self[key]

    def __getitem__(self, key):
        return Config._convert(self._config.get(key))

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Config):
            return self._config == value._config
        if isinstance(value, dict):
            return self._config == value
        return False

    def items(self):
        """
        Returns a set-like object providing a view on the child settings.
        """
        return self._config.items()

    def nested(self, path: str) -> Config | Any | None:
        """
        Safely access nested fields of the configuration object.

        :param path: A sequence of keys (separated by `.`) representing the nested fields.
        :return: The value of the nested field or None if any field is None.
        """
        value = self
        for key in path.split("."):
            if value is not None and hasattr(value, key):
                value = getattr(value, key)
            else:
                return None
        return value

    def first(self, path: str, predicate: Callable[[Config], bool]) -> Config | Any | None:
        """
        Safely access a nested collection of items and retrieve
        the first item for which the predicate returns true.

        :param path: A sequence of keys (separated by `.`) representing the nested fields.
        :param predicate: A function that takes an item and returns a boolean.
        :return: The first matching item, or None if no match is found.
        """
        if entries := self.nested(path):
            for entry in entries:
                try:
                    if predicate(entry):
                        return entry
                except AttributeError:
                    return None
        return None

    @staticmethod
    def _convert(val: Any) -> Config | list | Any:
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
        return Config(load(file.read(), schema()).data)
