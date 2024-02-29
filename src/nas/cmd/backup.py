"""
Provides functionality related to managing backups.
Backups could be created using `Archiver` and uploaded via `Uploader`.
"""

from __future__ import annotations

import bisect
import os
from datetime import datetime

from nas.core.archiver import ArchivalResult, Archiver
from nas.core.uploader import Uploader
from nas.report.writer import Writer
from nas.utils.timer import Timer


class Backup:
    """Create and upload backups."""

    def __init__(self, known_folders: dict[str, list], archiver: Archiver, uploader: Uploader, log: Writer):
        """
        Creates a new instance of `Backup`.

        :param known_folders: Dictionary with known folders, organized by groups.
        :param archiver: Archiver for archival creation.
        :param uploader: Uploader for data upload.
        :param log: Log writer.
        """

        self._known_folders = known_folders
        self._archiver = archiver
        self._uploader = uploader
        self._log = log

    def execute(self, groups: list[str], destination: str, overwrite: bool, upload: bool):
        """
        Backup the requested groups and save backups to the specified destination.

        :param groups: The list of groups to backup.
        :param destination: tbd
        :param overwrite: tbd
        :param upload: tbd
        """

        # Informational section with the general
        # overview of the backup execution plan.
        self._log_info(groups, destination, overwrite, upload)

        # Try to map the requested set of groups,
        # to the verified and known set of groups.
        group_mapping = self._map_groups(groups)

        # Folders section with information about
        # the mapped and unmapped folders and groups.
        self._log_groups(group_mapping)

        # If nothing has been mapped, there is no reason to continue
        if not group_mapping.successful:
            return

        # Backup all mapped groups
        archives = self._backup(destination, group_mapping.mapped, overwrite)

        # Upload all created archives
        if upload and self._uploader:
            self._upload(archives)

    def _log_info(self, groups: list[str], destination: str, overwrite: bool, upload: bool) -> None:
        """
        Write to log 'Information' section.

        :param groups: List of requested groups.
        :param destination: Path to destination folder.
        :param overwrite: True, if archives should be overwritten.
        :param upload: True, if backups should be uploaded.
        """
        log = self._log.section("Information:")
        log.out("destination:", destination)
        log.out("overwrite:", overwrite)
        log.out("upload:", upload)

        if not groups:
            log.out("groups:", "*")
        else:
            log.section("groups:").multiline(groups, as_list=True)

        log.out()

    def _log_groups(self, group_mapping: GroupMapping) -> None:
        """
        Write to log 'Folders:' section.

        :param group_mapping: Group mapping information.
        """
        log = self._log.section("Folders:")
        log.out("status:", group_mapping.status)
        log.out("mapped groups:", len(group_mapping.mapped))
        log.out("unmapped groups:", len(group_mapping.unmapped))

        log_mapping = log.section("group mapping:")
        for group in group_mapping.groups:
            log_grp = log_mapping.section(group.name)
            log_grp.multiline(group.folders if group.mapped else ["[Not Mapped]"], as_list=True)

        log.out()

    def _map_groups(self, groups: list[str]) -> GroupMapping:
        """
        Intersect the requested groups with the known groups.

        :param groups: Collection of requested groups to backup.
        :return: Result of group mapping.
        """

        # Create a distinct set of non-empty groups.
        groups = {grp for grp in groups if not grp.isspace()}
        mapped_groups = []

        # If no groups are explicitly specified,
        # it means that the backup should be executed
        # for all groups that are defined.
        if not groups:
            for group_name, folders in self._known_folders.items():
                group = Group(group_name)
                group.folders.extend(sorted(folders))
                bisect.insort(mapped_groups, group, key=lambda g: (not g.mapped, g.name))

        # Map each requested group to a known group.
        else:
            for requested_group in groups:
                group = Group(requested_group)

                # Search for a known group that matches the requested one.
                for group_name, folders in self._known_folders.items():
                    if group_name == requested_group:
                        group.folders.extend(sorted(folders))
                        break

                bisect.insort(mapped_groups, group, key=lambda g: (not g.mapped, g.name))

        return GroupMapping(mapped_groups)

    def _backup(self, destination: str, groups: list[Group], overwrite: bool) -> list[BackupResult]:
        """
        Backup several folder groups to the specified destination.

        :param destination: Path to destination folder.
        :param groups: List of folder groups to backup.
        :param overwrite: True, if existing archives should be overwritten.
        :return: List of successfully created archives.
        """

        # Capture the date before starting the backup,
        # because the backup process could run for several days
        # and we want to re-use the same start date for all
        # backup categories and folders.
        today = datetime.today()
        timer = Timer()
        created, failed, skipped = [], [], []

        log = self._log.section("Backup:")
        for group_ix, group in enumerate(groups):
            log_group = log.section(f"[{group_ix+1}/{len(groups)}] {group.name}")

            # Skip groups that are not mapped
            if not group.mapped:
                log_group.out("status:", "failed (not mapped)")
                log_group.out()
                continue

            # Backup each folder in the group, one by one
            for folder_ix, folder in enumerate(group.folders):
                log_folder = log_group.section(f"[{folder_ix+1}/{len(group.folders)}] {folder}")

                # Compose the full path of the destination backup file
                archive_path = self._compose_path(today, destination, group, folder)

                # If the backup under the prepared path exists,
                # it should either be skipped or removed.
                if os.path.exists(archive_path):
                    if overwrite:
                        log_folder.out("warning:", "overwriting existing backup")
                        os.remove(archive_path)
                    else:
                        bisect.insort(skipped, archive_path)
                        log_folder.out("destination:", archive_path)
                        log_folder.out("status:", "skipped (already exist)")
                        log_folder.out()
                        continue

                # Create backup archive
                archive_result = self._archiver.archive(folder, archive_path)
                backup_result = BackupResult(group, archive_result)
                log_folder.pretty.archive(archive_result)

                if backup_result.created:
                    bisect.insort(created, backup_result, key=lambda a: a.archive_path)
                else:
                    bisect.insort(failed, backup_result, key=lambda a: a.archive_path)

        # Output the summary of the backup operation,
        # with the list of created, failed and skipped archives.
        self._log_backup_summary(timer, created, failed, skipped)

        return created

    def _compose_path(self, today: datetime, destination: str, group: Group, folder: str) -> str:
        """
        Constructs a path to the backup archive file.

        :param today: Today's date and time, represented as `datetime`.
        :param destination: Path to the destination folder.
        :param group: Folder group name.
        :param folder: Path to the folder, that should be archived.
        :return: Full path to the backup archive file.
        """

        today_path = today.strftime("%Y-%m-%d")
        archive_name = os.path.basename(folder.strip("/"))

        # Backup path template, that is used to
        # construct the full path to the archive file.
        archive_path = f"{group.name}/{today_path}/{archive_name}.rar"

        return os.path.join(destination, archive_path)

    def _log_backup_summary(
        self,
        timer: Timer,
        created: list[BackupResult],
        failed: list[BackupResult],
        skipped: list[str],
    ):
        """
        Write to log 'Backup Summary' section.

        :param timer: Timer that has been used to measure duration of backup.
        :param created: Successfully created backup archives.
        :param failed: Backups that have failed and were not processed.
        :param skipped: Folders that were skipped from backup.
        """
        log = self._log.section("Backup Summary:")
        log.out("started:", timer.started, format_as="datetime")
        log.out("completed:", timer.now, format_as="datetime")
        log.out("duration:", timer.elapsed, format_as="duration")

        if created:
            total_size = sum(br.size for br in created)
            avg_speed = int(total_size // timer.elapsed.total_seconds())
            log.out("total size:", total_size, format_as="size")
            log.out("average speed:", avg_speed, format_as="speed")
            log.section("created:").multiline([br.archive_path for br in created], as_list=True)

        if failed:
            log.section("failed:").multiline([br.archive_path for br in failed], as_list=True)

        if skipped:
            log.section("skipped:").multiline(skipped, as_list=True)

        log.out()

    def _upload(self, backups: list[BackupResult]) -> None:
        """
        tbd

        :param archives: tbd
        """


class GroupMapping:
    """Result of mapping requested groups to known groups."""

    def __init__(self, groups: list[Group]):
        """
        Creates a new instance of `GroupMapping`.

        :param groups: Collection of both mapped and not mapped groups.
        """
        self.groups = groups

    @property
    def status(self) -> str:
        """Status of the group mapping."""
        return "success" if self.successful else "failed"

    @property
    def successful(self) -> bool:
        """Return `True` if the mapping is successful."""
        return len(self.mapped) > 0

    @property
    def mapped(self) -> list[Group]:
        """List of groups that were mapped successfully."""
        return [group for group in self.groups if group.mapped]

    @property
    def unmapped(self) -> list[Group]:
        """List of groups that were not mapped."""
        return [group for group in self.groups if not group.mapped]


class Group:
    """Represents a grouping of several folders."""

    def __init__(self, name: str):
        """Creates a new instance of `Group`."""

        self.name = name
        """The name of the group."""

        self.folders = []
        """The list of folders that belong to this group."""

    @property
    def mapped(self) -> bool:
        """True, if the group is mapped."""
        return bool(self.folders)


class BackupResult:
    """A result of creating a single backup."""

    def __init__(self, group: str, archival_result: ArchivalResult):
        """
        Creates a new instance of `BackupResult`.

        :param group: The name of the group.
        :param archival_result: Result of creating a backup archive.
        """

        self.group = group
        """The name of the group."""

        self.archival_result = archival_result
        """Result of creating a backup archive."""

    @property
    def archive_path(self) -> str:
        """Full path to the created backup."""
        return self.archival_result.archive_path

    @property
    def size(self) -> int:
        """Backup size, in bytes."""
        return self.archival_result.archive_size if self.created else 0

    @property
    def speed(self) -> int:
        """Backup speed, in bytes per second."""
        return self.archival_result.archival_speed if self.created else 0

    @property
    def created(self) -> bool:
        """True, if the backup has been successfully created."""
        return self.archival_result.successful
