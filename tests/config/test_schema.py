import glob
import json
import os

import pytest
from strictyaml import Map, YAMLError, load

from nimbuscli.config.schema import (
    backup,
    commands,
    deploy,
    observability,
    profiles,
    schema,
)


def validate(config_schema: Map, file_path: str):
    with open(file_path) as yaml_file:
        yaml_snippet = yaml_file.read().strip()
        expected_cfg = None

        # Search for the '.json' pair.
        # If the corresponding '.json' pair doesn't exist,
        # we expect the yaml to be invalid and a
        # YAMLError exception to be generated.
        # Otherwise the json file contains the valid config.
        json_path = os.path.splitext(file_path)[0] + ".json"
        if os.path.exists(json_path):
            with open(json_path) as json_file:
                expected_cfg = json_file.read().strip()

            parsed_cfg = load(yaml_snippet, config_schema)

            # Validate parsed YAML matches the expected config
            assert parsed_cfg.data == json.loads(expected_cfg)
        else:
            with pytest.raises(YAMLError):
                load(yaml_snippet, config_schema)


def discover(directory: str) -> list[str]:
    """
    Discover all configurations under the specified directory.
    If a directory path ends with '/', it will be processed recursively.
    """
    test_dir = os.path.splitext(__file__)[0]
    root_dir = os.path.join(test_dir, directory)
    return [
        os.path.join(root_dir, p)
        for p in glob.glob(
            "**/*.yaml" if directory.endswith("/") else "*.yaml",
            root_dir=root_dir,
            recursive=directory.endswith("/"),
        )
    ]


def pytest_generate_tests(metafunc):
    # The directories that ends with '/'
    # are processed recursively.
    directories = {
        # --
        "schema_filename": "",
        # --
        "observability_filename": "observability/",
        # --
        "profiles_filename": "profiles/",
        # --
        "commands_filename": "commands",
        "backup_filename": "commands/backup/",
        "deploy_filename": "commands/deploy/",
    }
    for param_name, root_dir in directories.items():
        if param_name in metafunc.fixturenames:
            metafunc.parametrize(param_name, discover(root_dir))


def test_schema(schema_filename):
    validate(schema(), schema_filename)


def test_observability(observability_filename):
    validate(observability(), observability_filename)


def test_profiles(profiles_filename):
    validate(profiles(), profiles_filename)


def test_commands(commands_filename):
    validate(commands(), commands_filename)


def test_backup(backup_filename):
    validate(backup(), backup_filename)


def test_deploy(deploy_filename):
    validate(deploy(), deploy_filename)
