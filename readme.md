# NAS management utility <!-- omit from toc --> 

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