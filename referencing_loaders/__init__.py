r"""
Helpers for loading `referencing.Resource`\ s out of various places.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any
import json
import os

from referencing import Resource, Specification

if TYPE_CHECKING:
    from collections.abc import Iterable
    from importlib.resources.abc import Traversable

    from referencing.typing import URI


def from_path(root: Path) -> Iterable[tuple[URI, Resource[Any]]]:
    """
    Load some resources recursively from a given directory path.

    Subdirectories are defaulted to the first version seen (starting from
    the root) -- though it still is often a good idea to explicitly indicate
    what specification every resource is written for internally.
    """
    return _from_walked(
        each for each in _walk(root) if each.name.endswith(".json")
    )


def _walk(path: Path) -> Iterable[Path]:
    walk = getattr(path, "walk", None)
    if walk is None:
        for dir, _, files in os.walk(path):  # pragma: no cover
            for file in files:
                yield Path(dir) / file
    else:
        for dir, _, files in walk():
            for file in files:
                yield dir / file


def _walk_traversable(root: Traversable) -> Iterable[Traversable]:
    """
    .walk() for importlib resources paths, which don't have the method :/
    """  # noqa: D415
    walking = [root]
    while walking:
        path = walking.pop()
        for each in path.iterdir():
            if each.is_dir():
                walking.append(each)
            else:
                yield each


def from_traversable(root: Traversable) -> Iterable[tuple[URI, Resource[Any]]]:
    """
    Load some resources from a given `importlib.resources` traversable.

    (I.e. load schemas from data within a Python package.)
    """
    return _from_walked(
        each for each in _walk_traversable(root) if each.name.endswith(".json")
    )


def _from_walked(
    paths: Iterable[Path | Traversable],
) -> Iterable[tuple[URI, Resource[Any]]]:
    specification: Specification[Any] | None = None
    for path in paths:
        contents = json.loads(path.read_text())
        if specification is None:
            specification = Specification.detect(contents)
        resource = specification.detect(contents).create_resource(contents)
        uri = getattr(path, "as_uri", lambda: "")()  # pragma: no cover
        yield uri, resource
