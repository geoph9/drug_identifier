"""Sphinx configuration."""
project = "Drug Discoverer"
author = "Georgios Karakasidis"
copyright = "2024, Georgios Karakasidis"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
