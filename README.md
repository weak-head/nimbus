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
  - [Building and Testing](#building-and-testing)
  - [Installation](#installation)
- [Usage](#usage)
  - [Backups](#backups)
  - [Deployments](#deployments)
- [Configuration](#configuration)

## Overview

Nimbus stands as a comprehensive data backup manager and service deployment orchestrator tailored for homelabs, media centers, and local development environments. It offers a seamless, turnkey solution to streamline your data management and service orchestration needs. While Nimbus is robust for personal or developmental use, it is not intended to supplant production-level or mission-critical tools designed for commercial-scale backups and deployments.

## Getting Started

tbd

### Building and Testing

```bash
# --
# Install poetry ( https://python-poetry.org/docs/ )
pipx install poetry
pipx ensurepath

# --
# Install pyenv
curl https://pyenv.run | bash

# --
# Setup virtual environment
pyenv install 3.12
pyenv virtualenv 3.12 nas_env
pyenv local nas_env

# --
# Install project dependencies
poetry install
```

### Installation

From GitLab Package Registry

## Usage

tbd configuration

### Backups

tbd selectors

### Deployments

tbd selectors

```bash
nas up [services ...]
nas down [services ...]
nas backup [groups ...]
```

## Configuration

tbd