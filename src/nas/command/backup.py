from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path

from nas.command.abstract import Command, CommandInfo
from nas.core.archiver import ArchivalResult, Archiver
from nas.core.provider import Provider, Resources
from nas.core.uploader import Uploader
from nas.report.writer import Writer


class Backup(Command):
    """
    Create and upload backups.
    """

    def __init__(
        self,
        writer: Writer,
        provider: Provider,
        archiver: Archiver,
        uploader: Uploader,
        destination: str,
        upload: bool,
    ):
        super().__init__(writer, provider)
        self._archiver = archiver
        self._uploader = uploader
        self._destination = destination
        self._upload = upload

    def info(self) -> CommandInfo:
        return CommandInfo(
            name="Backup",
            parameters={
                "Destination": self._destination,
                "Upload": self._upload,
            },
        )

    def _execute(self, resources: Resources) -> None:
        backups = self._execute_backup(self._destination, resources)
        self._writer.section("Backup").entry(backups)

        if not self._upload:
            return

        uploads = self._execute_upload(backups)
        self._writer.section("Upload").entry(uploads)

    def _execute_backup(self, destination: str, resources: Resources) -> BackupInfo:
        info = BackupInfo()
        info.started = datetime.now()

        for resource in resources.items:
            for artifact in resource.artifacts:
                entry = BackupEntry(resource.name, artifact)

                archive_path = self._compose_path(
                    info.started,
                    destination,
                    entry.group,
                    entry.folder,
                )

                entry.archive = self._archiver.archive(entry.folder, archive_path)
                info.entries.append(entry)

        info.completed = datetime.now()
        return info

    def _execute_upload(self, backups: BackupInfo) -> UploadInfo:
        return None

    def _compose_path(self, today: datetime, destination: str, group: str, folder: str) -> str:
        suffix = 0
        today_path = today.strftime("%Y-%m-%d")
        archive_name = Path(folder).name
        base_path = os.path.join(destination, group, today_path, archive_name)

        while True:
            archive_path = base_path + f"_{suffix:02d}.rar" if suffix > 0 else ".rar"
            if os.path.exists(archive_path):
                suffix += 1
            else:
                return archive_path


class BackupEntry:

    def __init__(self, group: str, folder: str):
        self.group: str = group
        self.folder: str = folder
        self.archive: ArchivalResult = None

    @property
    def successful(self) -> bool:
        return self.archive and self.archive.successful


class BackupInfo:

    def __init__(self):
        self.entries: list[BackupEntry] = []
        self.started: datetime = None
        self.completed: datetime = None

    @property
    def elapsed(self) -> timedelta:
        return self.completed - self.started


class UploadEntry:

    def __init__(self):
        self.backup: BackupEntry = None


class UploadInfo:

    def __init__(self):
        self.entries: list[UploadEntry] = []
        self.started: datetime = None
        self.completed: datetime = None

    @property
    def elapsed(self) -> timedelta:
        return self.completed - self.started
