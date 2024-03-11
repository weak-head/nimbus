from __future__ import annotations


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
