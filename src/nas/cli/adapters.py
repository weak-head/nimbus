"""
Adapters that convert CLI API and application configuration
to the internal command API.
"""

from argparse import Namespace

from nas.cmd import Backup, Down, Up
from nas.core.archiver import RarArchiver
from nas.core.runner import SubprocessRunner
from nas.core.uploader import AwsUploader
from nas.utils.config import Config
from nas.utils.format import Formatter
from nas.utils.log import Log


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

        log = Log(Formatter())
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

        log = Log(Formatter())
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

        groups = args.groups

        # Backup config
        destination_path = config.commands.backup.destination.path
        overwrite = config.commands.backup.destination.overwrite
        known_folders = config.commands.backup.groups

        # Upload config
        upload_enabled = config.commands.backup.upload.enabled
        upload_provider = config.commands.backup.upload.provider

        # Rar config
        rar_password = config.integrations.rar.password

        log = Log(Formatter())
        runner = SubprocessRunner()
        archiver = RarArchiver(runner, rar_password)
        uploader = None

        match upload_provider:

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

        backup = Backup(known_folders, archiver, uploader, log)
        backup.execute(groups, destination_path, overwrite, upload_enabled)


class SnapshotAdapter:
    """
    Converts CLI API into the internal 'snapshot' command API.
    """

    @staticmethod
    def execute(args: Namespace, config: Config) -> None:
        """
        Execute `Snapshot` command.

        :param args: CLI arguments.
        :param config: Application configuration.
        """
