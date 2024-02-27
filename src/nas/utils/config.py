"""
Exposes all functionality related to application configuration,
such as getting a default configuration or loading a custom configuration.
"""

from os.path import abspath, exists, expanduser

import yaml


class Config(dict):
    """
    Configuration is implemented as custom dictionary
    with support of dot.notation access to all configuration values.
    """

    def __getattr__(self, *args):
        """
        Support of dot.notation to get configuration values.
        """
        val = dict.get(self, *args)
        return Config(val) if isinstance(val, dict) else val

    __setattr__ = dict.__setitem__
    """Support of dot.notation to set configuration values."""

    __delattr__ = dict.__delitem__
    """Support of dot.notation to delete configuration values."""


def load_config(file_path: str = None) -> Config:
    """
    Load configuration and create dictionary with dot notation out of it.

    :param file_path: Path to the configuration file, optional.
    :return: Dictionary with configuration and dot notation support.
    """

    # Default search paths for configuration location.
    # The order in the list defines the search and load priority.
    search_paths = [
        "~/.nas/config.yml",
        "~/.nas/config.yaml",
    ]

    # If path to the configuration file is explicitly specified,
    # we ignore all default locations and use only the specified one.
    if file_path is not None:
        search_paths = [file_path]

    for candidate in search_paths:
        resolved_path = abspath(expanduser(candidate))

        # Try to load configuration only if the file exists
        if exists(resolved_path):
            with open(resolved_path, mode="r", encoding="utf-8") as file:
                return Config(yaml.safe_load(file))

    return None
