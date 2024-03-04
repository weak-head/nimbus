from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from nas.command.abstract import ActionInfo, Command, PipelineInfo
from nas.core.archiver import ArchivalResult, Archiver
from nas.core.provider import Provider, Resources
from nas.core.uploader import Uploader
from nas.report.writer import Writer


class Backup(Command):
    """
    Create and upload backups.
    """

    def __init__(self, path: str, writer: Writer, provider: Provider, archiver: Archiver, uploader: Uploader = None):
        super().__init__(writer, provider)
        self._destination = path
        self._archiver = archiver
        self._uploader = uploader

    def _build_pipeline(self, arguments: list[str]) -> PipelineInfo:
        pi = PipelineInfo("Backup")
        pi.config = {"Destination": self._destination, "Upload": bool(self._uploader)}
        pi.pipeline = [self._backup, self._upload] if self._uploader else [self._backup]
        pi.arguments = arguments
        pi.resources = self._provider.resolve(arguments)
        return pi

    def _backup(self, resources: Resources) -> BackupInfo:
        info = BackupInfo(started=datetime.now())

        for resource in resources.items:
            for artifact in resource.artifacts:
                entry = BackupEntry(resource.name, artifact)

                archive_path = self._compose_path(
                    self._destination,
                    entry.group,
                    entry.folder,
                    info.started,
                )

                entry.archive = self._archiver.archive(entry.folder, archive_path)
                info.entries.append(entry)

        info.completed = datetime.now()
        return info

    def _upload(self, backups: BackupInfo) -> UploadInfo:
        info = UploadInfo(started=datetime.now())

        # TODO: implement me

        info.completed = datetime.now()
        return info

    def _compose_path(self, destination: str, group: str, folder: str, today: datetime) -> str:
        suffix = 0
        today_path = today.strftime("%Y-%m-%d")
        archive_name = Path(folder).name
        base_path = os.path.join(destination, group, today_path, archive_name)

        # Don't overwrite the existing backups under the same path.
        # Find the next available name that matches the pattern.
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


class UploadEntry:

    def __init__(self):
        self.backup: BackupEntry = None


class BackupInfo(ActionInfo[BackupEntry]):
    pass


class UploadInfo(ActionInfo[UploadEntry]):
    pass
