<div align="center">
  <img src="./docs/logo.png" width="450" />
  
  # nimbus <!-- omit from toc --> 
  
  Nimbus is engineered to optimize data backup processes and efficiently orchestrate service deployments for homelabs and dev environments.
  <br/><br/>

  [![pipeline](https://git.lothric.net/lothric/infrastructure/nimbus/badges/main/pipeline.svg)](https://git.lothric.net/lothric/infrastructure/nimbus/-/pipelines)
  [![coverage](https://git.lothric.net/lothric/infrastructure/nimbus/badges/main/coverage.svg)](https://lothric.pages.lothric.net/infrastructure/nimbus)
  [![release](https://git.lothric.net/lothric/infrastructure/nimbus/-/badges/release.svg)](https://git.lothric.net/lothric/infrastructure/nimbus/-/releases)
  [![py3.12](https://img.shields.io/badge/python-3.12-4584b6.svg)](https://www.python.org/downloads/release/python-3120/)
  [![MIT License](https://img.shields.io/badge/license-MIT-blue)](https://opensource.org/license/mit)

</div>


## Table of Contents <!-- omit from toc -->

- [Overview](#overview)
- [Getting Started](#getting-started)
  - [Build from Source](#build-from-source)
  - [Package Installation](#package-installation)
- [Usage](#usage)
  - [Backups](#backups)
  - [Deployments](#deployments)

## Overview

Nimbus stands as a comprehensive data backup manager and service deployment orchestrator tailored for homelabs, media centers, and local development environments. It offers a seamless, turnkey solution to streamline your data management and service orchestration needs. While Nimbus is robust for personal or developmental use, it is not intended to supplant production-level or mission-critical tools designed for commercial-scale backups and deployments.

## Getting Started

To begin using Nimbus, you have two primary options:
- Build from Source: Compile and run Nimbus directly from the source code.  
  This method is ideal for those who wish to customize or contribute to the project.
- Package Installation: Conveniently install Nimbus via a package registry.  
  This option is best for users looking for a quick and straightforward setup.

### Build from Source

Nimbus uses [poetry](https://python-poetry.org/) for dependency management and packaging.  
Poetry could be installed using `pipx`. For any other installation options consult the documentation.

```bash
pipx ensurepath
pipx install poetry
```

Python versions and environments are managed using `pyenv`.

```bash
curl https://pyenv.run | bash

pyenv install 3.12
pyenv virtualenv 3.12 ni_env
pyenv local ni_env
```

Once you have set up `poetry` and `pyenv` you can install Nimbus and access it using `ni` shortcut.

```bash
poetry install
```

### Package Installation

Create a [Personal Access Token](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html) with `read_api` scope.

```bash
pyenv install 3.12
pyenv global 3.12
pip install nimbus \
  --index-url https://__token__:{PERSONAL_ACCESS_TOKEN}@git.lothric.net/api/v4/projects/112/packages/pypi/simple
```

## Usage

By default, Nimbus searches for its configuration file at the `~/.nimbus/config.yaml` path.  
It is anticipated that all configurations for the application will be centralized within this file.  
For guidance and examples on setting up your configuration, please refer to the [config example](./docs/config.example.yaml).  

> **Important Note on Glob Patterns in bash/sh**  
> When using the `ni` command, it’s essential to use `\*` in place of `*`.  
> This is because `bash` or `sh` interprets `*` as a glob pattern and attempts to expand it before passing it to `ni`.  
> By escaping the asterisk (`\*`), you ensure that `ni` receives the character literally, allowing it to process the glob pattern as intended.

### Backups

The `backup` command facilitates the creation of backups and enables their optional upload to a remote destination, such as an AWS S3 bucket.  
The command accepts optional selectors, that filter the configured backup groups using specified [glob patterns](https://en.wikipedia.org/wiki/Glob_(programming)).

```bash
ni backup [selectors]
```

Lets assume we have the following Nimbus configuration:

```yaml
archivers:
  rar-protected:
    provider: rar
    password: SecretPassword

uploaders:
  aws-archive:
    provider: aws
    access_key: XXXXXXXXXXXXX
    secret_key: XXXXXXXXXXXXXXXXXXXXXXXXX
    bucket: backups.bucket.aws
    storage_class: STANDARD

backup:
  destination: ~/.nimbus/backups
  archiver: rar-protected
  uploader: aws-archive
  directories: 
    photos:
      - ~/Pictures
      - /mnt/photos
    cloud:
      - /mnt/nextcloud
    docs:
      - ~/Documents
```

With this configuration, the following `backup` commands would result in:

| Command | Selected Backup groups |
| --- | --- |
| `ni backup` | photos cloud docs |
| `ni backup nx\*` | |
| `ni backup photos` | photos |
| `ni backup ph\* \*cloud\*` | photos cloud |
| `ni backup \*o\?\?` | cloud docs |

### Deployments

The `up` and `down` commands manage deployments of services. Nimbus supports services structured as [Docker Compose](https://docs.docker.com/compose/) stacks and performs recursive service discovery for the configured directories.  
The command accepts optional selectors, that filter the discovered services using specified [glob patterns](https://en.wikipedia.org/wiki/Glob_(programming)).

```bash
ni up [selectors]
ni down [selectors]
```

Lets assume we have the following Nimbus configuration:

```yaml
services:
  directories:
    - ~/.nimbus/services
```

And under the `~/.nimbus/services` we have the following directory structure:

```
|- services
    |- media
        |- .env
        |- compose.yaml
    |- cloud
        |- .env
        |- compose.yaml
    |- git
        |- some_file.txt 
        |- start.sh
```

With this configuration and directory structure, the following deployment commands would result in:

| Command | Selected Services |
| --- | --- |
| `ni up` | media cloud |
| `ni up media` | media |
| `ni down g\*` | |
| `ni down git` | |
| `ni down cl\*` | cloud |
