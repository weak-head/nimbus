import pytest

from nimbuscli.provider.directory import DirectoryProvider


class TestDirectoryProvider:

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
        p = DirectoryProvider(groups)

        d = {}
        for r in p._resources():
            d[r.name] = list(r.directories)

        assert d == groups
