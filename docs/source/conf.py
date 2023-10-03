# Configuration file for the Sphinx documentation builder.

import os
import sys

sys.path.insert(0, os.path.abspath("../../src"))

# Project metadata

project = 'PHUB'
copyright = '2023, Egsagon'
author = 'Egsagon'

# Sphinx extensions & options

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx_immaterial"
]

master_doc = "index"
templates_path = ["_templates"]
exclude_patterns = []

intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

# HTML rendering options

html_static_path = ["_static"]
html_theme = "sphinx_immaterial"

html_theme_options = {
    "icon": {
        "repo": "fontawesome/brands/github",
        "edit": "material/file-edit-outline",
        "logo": "material/download-box-outline"
    },
    "site_url": "https://phub.readthedocs.io",
    "repo_url": "https://github.com/Egsagon/PHUB",
    "repo_name": "PHUB",
    "edit_uri": "blob/main/docs",
    "globaltoc_collapse": True,
    "features": [
        "navigation.expand",
        "navigation.sections",
        "navigation.top",
        "toc.follow",
        "toc.sticky",
        "content.tabs.link",
        "announce.dismiss",
    ],
    "palette": [
        {
            "media": "(prefers-color-scheme: light)",
            "scheme": "default",
            "primary": "orange",
            "accent": "orange",
            "toggle": {
                "icon": "material/lightbulb-outline",
                "name": "Switch to dark mode",
            },
        },
        {
            "media": "(prefers-color-scheme: dark)",
            "scheme": "slate",
            "primary": "orange",
            "accent": "orange",
            "toggle": {
                "icon": "material/lightbulb",
                "name": "Switch to light mode",
            },
        },
    ],
    "version_dropdown": True,
    "version_info": [
        {
            "version": "https://phub.rtfd.io",
            "title": "Read the Docs",
            "aliases": [],
        }
    ],
    "toc_title_is_page_title": True,
    "social": [
        {
            "icon": "fontawesome/brands/github",
            "link": "https://github.com/Egsagon/PHUB",
            "name": "Source on github.com",
        },
        {
            "icon": "fontawesome/brands/python",
            "link": "https://pypi.org/project/phub/",
        },
    ],
}

html_sidebars = {
    "**": [
        "logo-text.html",
        "globaltoc.html",
    ]
}
