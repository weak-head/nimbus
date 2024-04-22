from pathlib import Path

import pytest

from nimbus.provider.service import ServiceProvider


class TestServiceProvider:

    @pytest.mark.parametrize(
        ["files", "selectors", "discovered"],
        [
            [[], [], []],
            [
                [
                    "media/compose.yml",
                    "cloud/compose.yml",
                    "git/run.sh",
                ],
                [],
                [
                    ("media", "docker-compose"),
                    ("cloud", "docker-compose"),
                ],
            ],
            [
                [
                    "media/compose.yml",
                    "cloud/compose.yml",
                    "git/run.sh",
                ],
                ["git"],
                [],
            ],
            [
                [
                    "srv/media/compose.yml",
                    "srv/cloud/compose.yml",
                    "infra/nginx/compose.yml",
                    "infra/data/mysql/compose.yml",
                    "infra/data/redis/compose.yml",
                    "git/run.sh",
                ],
                [],
                [
                    ("media", "docker-compose"),
                    ("cloud", "docker-compose"),
                    ("nginx", "docker-compose"),
                    ("mysql", "docker-compose"),
                    ("redis", "docker-compose"),
                ],
            ],
            [
                [
                    "srv/media/compose.yml",
                    "srv/cloud/compose.yml",
                    "infra/nginx/compose.yml",
                    "infra/data/mysql/compose.yml",
                    "infra/data/redis/compose.yml",
                    "git/run.sh",
                ],
                ["cloud"],
                [
                    ("cloud", "docker-compose"),
                ],
            ],
            [
                [
                    "srv/media/compose.yml",
                    "srv/cloud/compose.yml",
                    "infra/nginx/compose.yml",
                    "infra/data/mysql/compose.yml",
                    "infra/data/redis/compose.yml",
                    "git/run.sh",
                ],
                ["*data*"],
                [],
            ],
            [
                [
                    "srv/media/compose.yml",
                    "srv/cloud/compose.yml",
                    "infra/nginx/compose.yml",
                    "infra/data/mysql/compose.yml",
                    "infra/data/redis/compose.yml",
                    "git/run.sh",
                ],
                ["media", "*oud"],
                [
                    ("media", "docker-compose"),
                    ("cloud", "docker-compose"),
                ],
            ],
            [
                [
                    "srv/media/compose.xml",
                    "srv/cloud/compose.yxmlml",
                    "infra/nginx/compose.xml",
                    "infra/data/mysql/compose.jpg",
                    "infra/data/redis/compose.ttf",
                    "git/run.sh",
                ],
                [],
                [],
            ],
        ],
    )
    def test_resolve(self, tmp_path: Path, files, selectors, discovered):
        for f in files:
            p = tmp_path / f
            p.parent.mkdir(parents=True)
            p.touch()

        s = ServiceProvider([tmp_path])
        res = [(sr.name, sr.kind) for sr in s.resolve(selectors)]

        assert len(res) == len(discovered)
        for expectation in discovered:
            assert expectation in res
