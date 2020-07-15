from hypothesis import given, settings

from converter.config import Config
from converter.mapping import MappingSpec
from converter.mapping.base import TransformationEntry
from converter.runner.base import NotSet

from ..connector.fakes import FakeConnector
from ..mapping.fakes import FakeMapping
from .stategies import runners


@given(runner_class=runners())
@settings(deadline=None)
def test_transform_contains_replace(runner_class):
    input_data = [
        {"a": "foo a", "b": "foo b"},
        {"a": "far a", "b": "far b"},
        {"a": "boo a", "b": "boo b"},
        {"a": "bar a", "b": "bar b"},
    ]

    mapping = FakeMapping(
        "A",
        "B",
        [
            MappingSpec(
                "A",
                "B",
                forward_transform={
                    "c": [
                        TransformationEntry(
                            transformation="replace(a, 'oo', 'aa')",
                        )
                    ],
                    "d": [
                        TransformationEntry(
                            transformation=(
                                r"replace(a + ' ' + b, re'oo (.)', '\1\1')"
                            ),
                        )
                    ],
                },
            )
        ],
    )

    extractor = FakeConnector(data=input_data)
    loader = FakeConnector()

    runner_class(Config()).run(extractor, mapping, loader)

    assert list(loader.data) == [
        {"c": "faa a", "d": "faa fbb"},
        {"c": "far a", "d": "far a far b"},
        {"c": "baa a", "d": "baa bbb"},
        {"c": "bar a", "d": "bar a bar b"},
    ]


@given(runner_class=runners())
@settings(deadline=None)
def test_transform_contains_replace_on_non_lookup(runner_class):
    input_data = [
        {"a": "foo a", "b": "foo b"},
        {"a": "far a", "b": "far b"},
        {"a": "boo a", "b": "boo b"},
        {"a": "bar a", "b": "bar b"},
    ]

    mapping = FakeMapping(
        "A",
        "B",
        [
            MappingSpec(
                "A",
                "B",
                forward_transform={
                    "c": [
                        TransformationEntry(
                            transformation="replace('foo', 'oo', 'aa')",
                        )
                    ],
                    "d": [
                        TransformationEntry(
                            transformation=(
                                r"replace('foo, bee', re'o{2}', 'aa')"
                            ),
                        )
                    ],
                },
            )
        ],
    )

    extractor = FakeConnector(data=input_data)
    loader = FakeConnector()

    runner_class(Config()).run(extractor, mapping, loader)

    assert list(loader.data) == [
        {"c": "faa", "d": "faa, bee"},
        {"c": "faa", "d": "faa, bee"},
        {"c": "faa", "d": "faa, bee"},
        {"c": "faa", "d": "faa, bee"},
    ]


@given(runner_class=runners())
@settings(deadline=None)
def test_when_contains_match(runner_class):
    input_data = [
        {"a": "foo a", "b": "foo b"},
        {"a": "far a", "b": "far b"},
        {"a": "oo a", "b": "oo b"},
        {"a": "bar a", "b": "bar b"},
    ]

    mapping = FakeMapping(
        "A",
        "B",
        [
            MappingSpec(
                "A",
                "B",
                forward_transform={
                    "c": [
                        TransformationEntry(
                            transformation="a", when="match(a, 'foo a')",
                        )
                    ],
                    "d": [
                        TransformationEntry(
                            transformation="a + ' ' + b",
                            when="match(a, re'oo.*')",
                        )
                    ],
                },
            )
        ],
    )

    extractor = FakeConnector(data=input_data)
    loader = FakeConnector()

    runner_class(Config()).run(extractor, mapping, loader)

    assert list(loader.data) == [
        {"c": "foo a", "d": NotSet},
        {"c": NotSet, "d": "oo a oo b"},
    ]


@given(runner_class=runners())
@settings(deadline=None)
def test_when_contains_match_on_non_lookup(runner_class):
    input_data = [
        {"a": "foo a", "b": "foo b"},
        {"a": "far a", "b": "far b"},
        {"a": "boo a", "b": "boo b"},
        {"a": "bar a", "b": "bar b"},
    ]

    mapping = FakeMapping(
        "A",
        "B",
        [
            MappingSpec(
                "A",
                "B",
                forward_transform={
                    "c": [
                        TransformationEntry(
                            transformation="a", when="match('foo', 'foo')",
                        )
                    ],
                    "d": [
                        TransformationEntry(
                            transformation="a + ' ' + b",
                            when="match('foo a', re'.*oo.*')",
                        )
                    ],
                },
            )
        ],
    )

    extractor = FakeConnector(data=input_data)
    loader = FakeConnector()

    runner_class(Config()).run(extractor, mapping, loader)

    assert list(loader.data) == [
        {"c": "foo a", "d": "foo a foo b"},
        {"c": "far a", "d": "far a far b"},
        {"c": "boo a", "d": "boo a boo b"},
        {"c": "bar a", "d": "bar a bar b"},
    ]


@given(runner_class=runners())
@settings(deadline=None)
def test_when_contains_search(runner_class):
    input_data = [
        {"a": "foo a", "b": "foo b"},
        {"a": "far a", "b": "far b"},
        {"a": "boo a", "b": "boo b"},
        {"a": "bar a", "b": "bar b"},
    ]

    mapping = FakeMapping(
        "A",
        "B",
        [
            MappingSpec(
                "A",
                "B",
                forward_transform={
                    "c": [
                        TransformationEntry(
                            transformation="a", when="search(a, 'far')",
                        )
                    ],
                    "d": [
                        TransformationEntry(
                            transformation="a + ' ' + b",
                            when=r"search(a + ' ' + b, re'a\s\w+oo')",
                        )
                    ],
                },
            )
        ],
    )

    extractor = FakeConnector(data=input_data)
    loader = FakeConnector()

    runner_class(Config()).run(extractor, mapping, loader)

    assert list(loader.data) == [
        {"c": NotSet, "d": "foo a foo b"},
        {"c": "far a", "d": NotSet},
        {"c": NotSet, "d": "boo a boo b"},
    ]


@given(runner_class=runners())
@settings(deadline=None)
def test_when_contains_search_on_non_lookup(runner_class):
    input_data = [
        {"a": "foo a", "b": "foo b"},
        {"a": "far a", "b": "far b"},
        {"a": "boo a", "b": "boo b"},
        {"a": "bar a", "b": "bar b"},
    ]

    mapping = FakeMapping(
        "A",
        "B",
        [
            MappingSpec(
                "A",
                "B",
                forward_transform={
                    "c": [
                        TransformationEntry(
                            transformation="a",
                            when="search('a foo b', 'foo')",
                        )
                    ],
                    "d": [
                        TransformationEntry(
                            transformation="a + ' ' + b",
                            when=r"search('foo a bar', re'oo.\w')",
                        )
                    ],
                },
            )
        ],
    )

    extractor = FakeConnector(data=input_data)
    loader = FakeConnector()

    runner_class(Config()).run(extractor, mapping, loader)

    assert list(loader.data) == [
        {"c": "foo a", "d": "foo a foo b"},
        {"c": "far a", "d": "far a far b"},
        {"c": "boo a", "d": "boo a boo b"},
        {"c": "bar a", "d": "bar a bar b"},
    ]


@given(runner_class=runners())
@settings(deadline=None)
def test_transform_contains_join_of_lookups_str_and_non_str(runner_class):
    input_data = [
        {"a": "foo a", "b": 1},
        {"a": "far a", "b": 2},
        {"a": "boo a", "b": 3},
        {"a": "bar a", "b": 4},
    ]

    mapping = FakeMapping(
        "A",
        "B",
        [
            MappingSpec(
                "A",
                "B",
                forward_transform={
                    "c": [
                        TransformationEntry(
                            transformation="join(', ', 'bar', a, 5, b, 0)",
                        )
                    ],
                },
            )
        ],
    )

    extractor = FakeConnector(data=input_data)
    loader = FakeConnector()

    runner_class(Config()).run(extractor, mapping, loader)

    assert list(loader.data) == [
        {"c": "bar, foo a, 5, 1, 0"},
        {"c": "bar, far a, 5, 2, 0"},
        {"c": "bar, boo a, 5, 3, 0"},
        {"c": "bar, bar a, 5, 4, 0"},
    ]


@given(runner_class=runners())
@settings(deadline=None)
def test_transform_contains_join_of_nothing(runner_class):
    input_data = [
        {"a": "foo a", "b": 1},
        {"a": "far a", "b": 2},
        {"a": "boo a", "b": 3},
        {"a": "bar a", "b": 4},
    ]

    mapping = FakeMapping(
        "A",
        "B",
        [
            MappingSpec(
                "A",
                "B",
                forward_transform={
                    "c": [TransformationEntry(transformation="join(', ')",)],
                },
            )
        ],
    )

    extractor = FakeConnector(data=input_data)
    loader = FakeConnector()

    runner_class(Config()).run(extractor, mapping, loader)

    assert list(loader.data) == [
        {"c": ""},
        {"c": ""},
        {"c": ""},
        {"c": ""},
    ]


@given(runner_class=runners())
@settings(deadline=None)
def test_transform_contains_join_of_single_element(runner_class):
    input_data = [
        {"a": "foo a", "b": 1},
        {"a": "far a", "b": 2},
        {"a": "boo a", "b": 3},
        {"a": "bar a", "b": 4},
    ]

    mapping = FakeMapping(
        "A",
        "B",
        [
            MappingSpec(
                "A",
                "B",
                forward_transform={
                    "c": [
                        TransformationEntry(transformation="join(', ', a)",)
                    ],
                },
            )
        ],
    )

    extractor = FakeConnector(data=input_data)
    loader = FakeConnector()

    runner_class(Config()).run(extractor, mapping, loader)

    assert list(loader.data) == [
        {"c": "foo a"},
        {"c": "far a"},
        {"c": "boo a"},
        {"c": "bar a"},
    ]