# Configuration file for the Sphinx documentation builder.

import os
import sys

sys.path.insert(0, os.path.abspath("../../src"))

# Project metadata

project = "PHUB"
copyright = "2023, Egsagon"
author = "Egsagon"

# Sphinx extensions & options

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
]

master_doc = "index"
templates_path = ["_templates"]
exclude_patterns = []

intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

# HTML rendering options

html_static_path = ["_static"]

html_theme = "furo"
