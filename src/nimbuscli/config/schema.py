from __future__ import annotations

from strictyaml import Bool, Enum, Int, Map, MapPattern, Optional, Seq, Str


def schema() -> Map:
    """
    YAML schema of the application configuration file.
    """
    return Map(
        {
            Optional("observability"): observability(),
            Optional("profiles"): profiles(),
            "commands": commands(),
        }
    )


def observability() -> Map:
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


def profiles() -> Map:
    return Map(
        {
            Optional("archive"): Seq(
                Map(
                    {
                        "name": Str(),
                        "provider": Enum(
                            [
                                "rar",
                                "tar",
                                "zip",
                            ]
                        ),
                        Optional("compress"): Int() | Str(),
                        Optional("recovery"): Int(),
                        Optional("password"): Str(),
                    }
                )
            ),
            Optional("upload"): Seq(
                Map(
                    {
                        "name": Str(),
                        "provider": Enum(
                            [
                                "aws",
                            ]
                        ),
                        "access_key": Str(),
                        "secret_key": Str(),
                        "bucket": Str(),
                        "storage": Enum(
                            [
                                "STANDARD",
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


def commands() -> Map:
    return Map(
        {
            "deploy": Map(
                {
                    "services": Seq(Str()),
                    Optional("secrets"): Seq(
                        Map(
                            {
                                "service": Str(),
                                "environment": MapPattern(
                                    Str(),
                                    Str(),
                                ),
                            }
                        )
                    ),
                },
            ),
            "backup": Map(
                {
                    "destination": Str(),
                    "archive": Str(),
                    Optional("upload"): Str(),
                    "directories": MapPattern(
                        Str(),
                        Seq(Str()),
                    ),
                }
            ),
        }
    )
