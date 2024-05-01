# Changelog

## 0.3.1 (2024-05-01)

### Changed

- Simplified and re-designed application configuration.

### Added

- Support discord notifications.
- Output current application version with `--version` flag.
- Validate application configuration based on the expected schema.

## 0.2.0 (2024-04-19)

### Added

- Enhanced `rar` support with adjustable compression and recovery.
- Do not follow symbolic links for `rar` backups.
- Configurable application logging.
- Operation reports now include backup and deployment details.

## 0.1.0 (2024-04-06)

### Features

- Initial backup and upload functionality using `rar` and AWS S3.
- Docker-compose service management.
- Comprehensive operation summary reports.
