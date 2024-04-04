<div align="center">
  <img src="./docs/logo.png" width="450" />
  
  # nimbus <!-- omit from toc --> 
  
  Nimbus is engineered to optimize data backup processes and efficiently orchestrate service deployments.
  <br/><br/>

  [![pipeline](https://git.lothric.net/lothric/infrastructure/nimbus/badges/main/pipeline.svg)](https://git.lothric.net/lothric/infrastructure/nimbus/-/pipelines)
  [![coverage](https://git.lothric.net/lothric/infrastructure/nimbus/badges/main/coverage.svg)](https://lothric.pages.lothric.net/infrastructure/nas)
  [![release](https://git.lothric.net/lothric/infrastructure/nimbus/-/badges/release.svg)](https://git.lothric.net/lothric/infrastructure/nimbus/-/releases)
  [![py3.12](https://img.shields.io/badge/python-3.12-4584b6.svg)](https://www.python.org/downloads/release/python-3120/)
  [![MIT License](https://img.shields.io/badge/license-MIT-blue)](https://opensource.org/license/mit)

</div>


## Table of Content <!-- omit from toc -->

- [Environment setup](#environment-setup)
- [Available commands](#available-commands)

## Environment setup

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

## Available commands

```bash
nas up [services ...]
nas down [services ...]
nas backup [groups ...]
```