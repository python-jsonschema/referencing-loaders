import importlib.metadata
import re

from url import URL

GITHUB = URL.parse("https://github.com/")
HOMEPAGE = GITHUB / "python-jsonschema/referencing-loaders"

project = "referencing-loaders"
author = "Julian Berman"
copyright = f"2023, {author}"

release = importlib.metadata.version("referencing-loaders")
version = release.partition("-")[0]

language = "en"
default_role = "any"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "sphinxcontrib.spelling",
    "sphinxext.opengraph",
]

pygments_style = "lovelace"
pygments_dark_style = "one-dark"

html_theme = "furo"

# See sphinx-doc/sphinx#10785
_TYPE_ALIASES = dict(
    AnchorType=("class", "Anchor"),
    D=("data", "D"),
    ObjectSchema=("data", "ObjectSchema"),
    Schema=("data", "Schema"),
    URI=("attr", "URI"),  # ?!?!?! Sphinx...
)


def _resolve_broken_refs(app, env, node, contnode):
    if node["refdomain"] != "py":
        return

    if node["reftarget"].startswith("referencing.typing."):
        kind, target = "data", node["reftarget"]
    else:
        kind, target = _TYPE_ALIASES.get(node["reftarget"], (None, None))
    if kind is not None:
        return app.env.get_domain("py").resolve_xref(
            env,
            node["refdoc"],
            app.builder,
            kind,
            target,
            node,
            contnode,
        )


def setup(app):
    app.connect("missing-reference", _resolve_broken_refs)


def entire_domain(host):
    return r"http.?://" + re.escape(host) + r"($|/.*)"


linkcheck_ignore = [
    entire_domain("img.shields.io"),
    f"{GITHUB}.*#.*",
    str(HOMEPAGE / "actions"),
    str(HOMEPAGE / "workflows/CI/badge.svg"),
]

# = Extensions =

# -- autodoc --

autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
}

# -- autosectionlabel --

autosectionlabel_prefix_document = True

# -- intersphinx --

intersphinx_mapping = {
    "python": ("https://docs.python.org/", None),
    "referencing": ("https://referencing.readthedocs.io/en/stable/", None),
}

# -- extlinks --

extlinks = {
    "gh": (str(HOMEPAGE) + "/%s", None),
    "github": (str(GITHUB) + "/%s", None),
}
extlinks_detect_hardcoded_links = True

# -- sphinxcontrib-spelling --

spelling_word_list_filename = "spelling-wordlist.txt"
spelling_show_suggestions = True
