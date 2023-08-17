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

html_theme = "sphinx_material"

html_theme_options = {

    'nav_title': 'PHUB',

    'color_primary': 'blue',
    'color_accent': 'light-blue',

    'repo_url': 'https://github.com/Egsagon/PHUB',
    'repo_name': 'PHUB',

    'globaltoc_depth': 3,
    'globaltoc_collapse': False,
    'globaltoc_includehidden': False,
    
    'logo_icon': '&#xe869'
}

html_sidebars = {
    "**": [
        "logo-text.html",
        "globaltoc.html",
    ]
}