from typing import Iterator
import pytest

from nimbus.provider.abstract import Resource, Provider


class TestResource:

    @pytest.mark.parametrize(
        ["name", "selector", "match"],
        [
            ["abc", "", False],
            ["abc", "a", False],
            ["abc", "abc", True],
            ["abc", "abcd", False],
            ["abc", "a*", True],
            ["abc", "ab?", True],
            ["abc", "abc?", False],
            ["abc", "*b*", True],
            ["abc", "*abc*", True],
            ["abc", "*ab*c", True],
            ["abc", "[adf]?c", True],
            ["abc", "a[a-c]c", True],
            ["abc", "[a-c][b-d][c-e]", True],
            ["abc", "[bdf]?c", False],
            ["abc", "[b-c][b-d][c-e]", False],
        ],
    )
    def test_match(self, name, selector, match):
        r = Resource(name)
        assert r.match(selector) == match


class FakeProvider(Provider):

    def __init__(self, res: list[str]):
        self._res = res

    def _resources(self) -> Iterator:
        return (Resource(name) for name in self._res)


class TestProvider:

    @pytest.mark.parametrize(
        ["resources", "selectors", "matched"],
        [
            [
                ["nginx", "cloud", "media", "books"],
                [],
                ["nginx", "cloud", "media", "books"],
            ],
            [
                ["nginx", "cloud", "media", "books"],
                ["*"],
                ["nginx", "cloud", "media", "books"],
            ],
            [
                ["nginx", "cloud", "media", "books"],
                ["*", "nginx"],
                ["nginx", "cloud", "media", "books"],
            ],
            [
                ["nginx", "cloud", "nextcloud", "media"],
                ["*cloud"],
                ["cloud", "nextcloud"],
            ],
            [
                ["nginx", "cloud", "nextcloud", "media"],
                ["*cloud", "*in*"],
                ["nginx", "cloud", "nextcloud"],
            ],
            [
                ["nginx", "cloud", "nextcloud", "media"],
                ["*in*"],
                ["nginx"],
            ],
            [
                ["nginx", "cloud", "nextcloud", "media"],
                ["nginx"],
                ["nginx"],
            ],
            [
                ["nginx", "nginx2", "nginx3", "nginx22"],
                ["nginx"],
                ["nginx"],
            ],
            [
                ["nginx", "nginx2", "nginx3", "nginx22"],
                ["nginx2"],
                ["nginx2"],
            ],
            [
                ["nginx", "nginx2", "nginx3", "nginx22"],
                ["nginx?"],
                ["nginx2", "nginx3"],
            ],
            [
                ["nginx", "nginx2", "nginx3", "nginx22"],
                ["nginx??"],
                ["nginx22"],
            ],
            [
                ["nginx", "nginx2", "nginx3", "nginx22"],
                ["nginx*"],
                ["nginx", "nginx2", "nginx3", "nginx22"],
            ],
        ],
    )
    def test_match(self, resources, selectors, matched):
        p = FakeProvider(resources)
        assert set([r.name for r in p.resolve(selectors)]) == set(matched)
