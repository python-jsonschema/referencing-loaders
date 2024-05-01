import json
import sys

try:
    from importlib.resources import files
except ImportError:  # pragma: no cover
    from importlib_resources import files

from referencing import Registry
from referencing.jsonschema import DRAFT202012, EMPTY_REGISTRY

import referencing_loaders as loaders


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


def test_schema_is_inherited_downwards(tmp_path):
    root_path, root = tmp_path / "schema.json", {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "http://example.com/",
    }
    son_path, son = tmp_path / "child/son.json", {
        "$id": "http://example.com/son",
    }
    daughter_path, daughter = tmp_path / "child/daughter.json", {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "http://example.com/random/daughter",
    }
    grandchild_path, grandchild = tmp_path / "child/more/gc.json", {
        "$id": "http://example.com/also/a/grandchild",
    }

    tmp_path.joinpath("child/more").mkdir(parents=True)
    root_path.write_text(json.dumps(root))
    son_path.write_text(json.dumps(son))
    daughter_path.write_text(json.dumps(daughter))
    grandchild_path.write_text(json.dumps(grandchild))

    expected = Registry().with_resources(
        (each, DRAFT202012.create_resource(contents))
        for each, contents in [
            (root_path.as_uri(), root),
            (son_path.as_uri(), son),
            (daughter_path.as_uri(), daughter),
            (grandchild_path.as_uri(), grandchild),
        ]
    )

    resources = loaders.from_path(tmp_path)
    registry = EMPTY_REGISTRY.with_resources(resources)
    assert registry.crawl() == expected.crawl()


def test_hidden_files_are_ignored(tmp_path):
    schema_path, schema = tmp_path / "schema.json", {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "http://example.com/",
    }
    hidden_path = tmp_path / ".hidden"

    schema_path.write_text(json.dumps(schema))
    hidden_path.write_text("total nonsense")

    expected = Registry().with_contents([(schema_path.as_uri(), schema)])

    resources = loaders.from_path(tmp_path)
    registry = EMPTY_REGISTRY.with_resources(resources)
    assert registry.crawl() == expected.crawl()


def test_empty(tmp_path):
    registry = EMPTY_REGISTRY.with_resources(loaders.from_path(tmp_path))
    assert registry == EMPTY_REGISTRY


def test_traversable(tmp_path):
    package = tmp_path / "foo"

    schemas = package / "schemas"
    path, schema = schemas / "schema.json", {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "http://example.com/",
    }
    subpath, subschema = schemas / "more/child.json", {"foo": "bar"}

    schemas.joinpath("more").mkdir(parents=True)
    package.joinpath("__init__.py").touch()
    path.write_text(json.dumps(schema))
    subpath.write_text(json.dumps(subschema))

    # ?!?! -- without this, importlib.resources.files fails on 3.9 and no other
    # version!?!?
    schemas.joinpath("__init__.py").touch()

    try:
        sys.path.append(str(tmp_path))
        resources = loaders.from_traversable(files("foo.schemas"))
        registry = EMPTY_REGISTRY.with_resources(resources)

        expected = Registry().with_resources(
            (each, DRAFT202012.create_resource(contents))
            for each, contents in [
                (path.as_uri(), schema),
                (subpath.as_uri(), subschema),
            ]
        )

        assert registry.crawl() == expected.crawl()
    finally:
        sys.path.pop()
