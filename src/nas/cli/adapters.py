"""
Adapters that convert CLI API and application configuration
to the internal command API.
"""

from argparse import Namespace

from nas.command import Backup, Down, Up
from nas.config import Config
from nas.core.archiver import RarArchiver
from nas.core.provider import DictionaryProvider
from nas.core.runner import SubprocessRunner
from nas.core.uploader import AwsUploader
from nas.report.format import Formatter
from nas.report.writer import LogWriter


class UpAdapter:
    """
    Converts CLI API into the internal 'up' command API.
    """

    @staticmethod
    def execute(args: Namespace, config: Config) -> None:
        """
        Execute `Up` command.

        :param args: CLI arguments.
        :param config: Application configuration.
        """

        services = args.services
        root_folder = config.services.path

        log = LogWriter(Formatter())
        runner = SubprocessRunner()
        up = Up(root_folder, runner, log)

        up.execute(services)


class DownAdapter:
    """
    Converts CLI API into the internal 'down' command API.
    """

    @staticmethod
    def execute(args: Namespace, config: Config) -> None:
        """
        Execute `Down` command.

        :param args: CLI arguments.
        :param config: Application configuration.
        """

        services = args.services
        root_folder = config.services.path

        log = LogWriter(Formatter())
        runner = SubprocessRunner()
        down = Down(root_folder, runner, log)

        down.execute(services)


class BackupAdapter:
    """
    Converts CLI API into the internal 'backup' command API.
    """

    @staticmethod
    def execute(args: Namespace, config: Config) -> None:
        """
        Execute `Backup` command.

        :param args: CLI arguments.
        :param config: Application configuration.
        """

        patterns = args.patterns

        # Backup config
        destination = config.commands.backup.destination
        known_folders = config.commands.backup.groups

        # Upload config
        upload_enabled = config.commands.backup.upload.enabled

        # Rar config
        rar_password = config.integrations.rar.password

        writer = LogWriter(Formatter())
        provider = DictionaryProvider(known_folders)
        runner = SubprocessRunner()
        archiver = RarArchiver(runner, rar_password)
        uploader = None

        if upload_enabled:
            match config.commands.backup.upload.provider:

                # AWS S3 uploader
                case "aws":
                    aws_access_key = config.integrations.aws.access_key
                    aws_secret_key = config.integrations.aws.secret_key
                    aws_bucket = config.commands.backup.upload.aws.bucket
                    aws_storage = config.commands.backup.upload.aws.storage_class

                    uploader = AwsUploader(aws_access_key, aws_secret_key, aws_bucket, aws_storage)

                # Any other provider
                case _:
                    uploader = None

        backup = Backup(destination, writer, provider, archiver, uploader)
        backup.execute(patterns)
