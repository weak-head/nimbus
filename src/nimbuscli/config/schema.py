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
            Optional("reports"): reports(),
            Optional("logs"): logs(),
            Optional("notifications"): notifications(),
        }
    )


def profiles() -> Map:
    return Map(
        {
            Optional("archive"): archive(),
            Optional("upload"): upload(),
        }
    )


def commands() -> Map:
    return Map(
        {
            "deploy": deploy(),
            "backup": backup(),
        }
    )


def reports() -> Map:
    return Map(
        {
            "format": Enum(
                [
                    "txt",
                ]
            ),
            "directory": Str(),
        }
    )


def logs() -> Map:
    return Map(
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
    )


def notifications() -> Map:
    return Map(
        {
            Optional("discord"): Map(
                {
                    "webhook": Str(),
                    Optional("username"): Str(),
                    Optional("avatar_url"): Str(),
                }
            ),
        }
    )


def archive() -> Map:
    return Seq(
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
                Optional("compress"): Enum(
                    [
                        "gz",
                        "xz",
                        "bz2",
                    ]
                )
                | Int(),
                Optional("recovery"): Int(),
                Optional("password"): Str(),
            }
        )
    )


def upload() -> Map:
    return Seq(
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
    )


def deploy() -> Map:
    return Map(
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
    )


def backup() -> Map:
    return Map(
        {
            "destination": Str(),
            "archive": Str(),
            Optional("upload"): Str(),
            "directories": MapPattern(
                Str(),
                Seq(Str()),
            ),
        }
    )
