r"""
Helpers for loading `referencing.Resource`\ s out of various places.
"""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable
import json
import os

from referencing import Resource, Specification

if TYPE_CHECKING:
    from referencing.typing import URI


def from_path(root: Path) -> Iterable[tuple[URI, Resource[Any]]]:
    """
    Load some resources recursively from a given directory path.

    Subdirectories are defaulted to the first version seen (starting from
    the root) -- though it still is often a good idea to explicitly indicate
    what specification every resource is written for internally.
    """
    specification: Specification[Any] | None = None
    for dir, _, files in _walk(root):
        for file in files:
            path = dir / file
            contents = json.loads(path.read_text())
            if specification is None:
                specification = Specification.detect(contents)  # type: ignore[reportUnknownMemberType]
            resource = specification.detect(contents).create_resource(contents)
            yield path.as_uri(), resource


def _walk(path: Path) -> Iterable[tuple[Path, Iterable[str], Iterable[str]]]:
    walk = getattr(path, "walk", None)
    if walk is not None:
        yield from walk()
        return
    for root, dirs, files in os.walk(path):  # pragma: no cover
        yield Path(root), dirs, files
