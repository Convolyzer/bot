# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Convolyzer"
copyright = '2024, Yanis Allain, Sepanta Farzollahi, Hagop Hannachian, Jean-Baptiste Hochet'
author = "Yanis Allain, Sepanta Farzollahi, Hagop Hannachian, Jean-Baptiste Hochet"
release = "1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
]

templates_path = ["_templates"]
exclude_patterns = []

sys.path.insert(0, os.path.abspath("../.."))

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "press"
html_static_path = ["_static"]

# -- Options for Latex output ------------------------------------------------
latex_engine = "xelatex"

latex_elements = {
    "fontpkg": r"""
    \setmainfont{Symbola}
    \setsansfont{Symbola}
    \setmonofont{DejaVu Sans Mono}
    """,
    "maketitle": r"""
    \title{Convolyzer}
    \author{
        Yanis Allain \\
        Sepanta Farzollahi \\
        Hagop Hannachian \\
        Jean-Baptiste Hochet
    }
    \date{\today}

    \sphinxmaketitle
    """,
}
