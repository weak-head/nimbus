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
- [Configuration](#configuration)

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

TODO: Steps to install from GitLab Package Registry

## Usage

By default, Nimbus searches for its configuration file at the `~/.nimbus/config.yaml` path.  
It is anticipated that all configurations for the application will be centralized within this file.  
For guidance and examples on setting up your configuration, please refer to the [documentation section](#configuration).  

### Backups

Creating backups and uploading them to AWS S3 bucket.

```sh
ni backup [selectors ...]
```

Examples:
- `ni backup`
- `ni backup photos`
- `ni backup ph* *cloud*`

### Deployments

Managing deployments of docker compose stacks.

```sh
ni up [selectors ...]
ni down [selectors ...]
```

Examples:
- `ni up`
- `ni up m* *cloud*`
- `ni down media git`


## Configuration

tbd