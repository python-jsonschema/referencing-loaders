r"""
Helpers for loading `referencing.Resource`\ s out of various places.
"""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable
import json
import os

from referencing import Resource

if TYPE_CHECKING:
    from referencing.typing import URI


def from_path(path: Path) -> Iterable[tuple[URI, Resource[Any]]]:
    """
    Load some resources recursively from a given directory path.
    """
    for root, _, files in _walk(path):
        for file in files:
            path = root / file
            contents = json.loads(path.read_text())
            yield path.as_uri(), Resource.from_contents(contents)


def _walk(path: Path) -> Iterable[tuple[Path, Iterable[str], Iterable[str]]]:
    walk = getattr(path, "walk", None)
    if walk is not None:
        yield from walk()
        return
    for root, dirs, files in os.walk(path):  # pragma: no cover
        yield Path(root), dirs, files
