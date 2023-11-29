import json

from referencing import Registry, loaders
from referencing.jsonschema import EMPTY_REGISTRY


def test_absolute_internally_identified(tmp_path):
    root_path, root = tmp_path / "schema.json", {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "http://example.com/",
    }
    son_path, son = tmp_path / "child/son.json", {
        "$schema": "https://json-schema.org/draft/2019-09/schema",
        "$id": "http://example.com/son",
    }
    daughter_path, daughter = tmp_path / "child/daughter.json", {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "http://example.com/random/daughter",
    }
    grandchild_path, grandchild = tmp_path / "child/more/gc.json", {
        "$schema": "https://json-schema.org/draft/2019-09/schema",
        "$id": "http://example.com/also/a/grandchild",
    }

    tmp_path.joinpath("child/more").mkdir(parents=True)
    root_path.write_text(json.dumps(root))
    son_path.write_text(json.dumps(son))
    daughter_path.write_text(json.dumps(daughter))
    grandchild_path.write_text(json.dumps(grandchild))

    expected = Registry().with_contents(
        [
            (root_path.as_uri(), root),
            (son_path.as_uri(), son),
            (daughter_path.as_uri(), daughter),
            (grandchild_path.as_uri(), grandchild),
        ],
    )

    resources = loaders.from_path(tmp_path)
    registry = EMPTY_REGISTRY.with_resources(resources)
    assert registry.crawl() == expected.crawl()


def test_empty(tmp_path):
    registry = EMPTY_REGISTRY.with_resources(loaders.from_path(tmp_path))
    assert registry == EMPTY_REGISTRY
