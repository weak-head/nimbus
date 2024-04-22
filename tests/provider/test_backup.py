import pytest

from nimbus.provider.backup import BackupProvider


class TestBackupProvider:

    @pytest.mark.parametrize(
        "groups",
        [
            {},
            {
                "apps": [],
                "cloud": [],
            },
            {
                "apps": [
                    "/mnt/app1",
                    "/mnt/app2",
                ]
            },
            {
                "photos": ["/mnt/photos"],
                "apps": ["/mnt/app"],
            },
        ],
    )
    def test_resources(self, groups):
        p = BackupProvider(groups)

        d = {}
        for r in p._resources():
            d[r.name] = list(r.directories)

        assert d == groups
