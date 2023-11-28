r"""
Helpers for loading `referencing.Resource`\ s out of various places.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable

from referencing import Resource

if TYPE_CHECKING:
    from pathlib import Path


def from_path(path: Path) -> Iterable[Resource[Any]]:
    """
    Load some resources recursively from a given directory path.
    """
    for _, _, _ in path.walk():
        yield Resource.opaque(None)
