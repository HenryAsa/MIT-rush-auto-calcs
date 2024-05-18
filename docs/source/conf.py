# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'MIT Rush Auto Analysis'
copyright = '2024, Henry Asa'
author = 'Henry Asa'
release = '0.0.0'

import os
import sys
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../..'))


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# extensions = [
#     'sphinx.ext.autodoc',
#     'sphinx.ext.coverage',
#     'sphinx.ext.napoleon',
# ]

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.autosummary',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.graphviz',
    'sphinx.ext.ifconfig',
    'numpydoc',
    'sphinx_design',
]

templates_path = ['_templates']
exclude_patterns = []


# -----------------------------------------------------------------------------
# Intersphinx configuration
# -----------------------------------------------------------------------------
intersphinx_mapping = {
    'neps': ('https://numpy.org/neps', None),
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable', None),
    'scipy': ('https://docs.scipy.org/doc/scipy', None),
    'matplotlib': ('https://matplotlib.org/stable', None),
    'imageio': ('https://imageio.readthedocs.io/en/stable', None),
    'skimage': ('https://scikit-image.org/docs/stable', None),
    'pandas': ('https://pandas.pydata.org/pandas-docs/stable', None),
    'scipy-lecture-notes': ('https://scipy-lectures.org', None),
    'pytest': ('https://docs.pytest.org/en/stable', None),
    'numpy-tutorials': ('https://numpy.org/numpy-tutorials', None),
    'numpydoc': ('https://numpydoc.readthedocs.io/en/latest', None),
    'dlpack': ('https://dmlc.github.io/dlpack/latest', None),
    'pint': ('https://pint.readthedocs.io/en/stable', None),
    'cartopy': ('https://scitools.org.uk/cartopy/docs/latest', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master', None),
    # 'pint_pandas': ('https://pint.readthedocs.io/en/0.18/pint-pandas.html', None),
}

# -----------------------------------------------------------------------------
# Autosummary
# -----------------------------------------------------------------------------
autosummary_generate = True             # Turn on sphinx.ext.autosummary
autoclass_content = "both"              # Add __init__ doc (ie. params) to class summaries
html_show_sourcelink = False            # Remove 'view source code' from top of page (for html, not python)
autodoc_inherit_docstrings = True       # If no docstring, inherit from base class
set_type_checking_flag = True           # Enable 'expensive' imports for sphinx_autodoc_typehints
nbsphinx_allow_errors = True            # Continue through Jupyter errors
# autodoc_typehints = "description"       # Sphinx-native method. Not as good as sphinx_autodoc_typehints
add_module_names = False                # Remove namespaces from class/method signatures



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'alabaster'
html_theme = 'pydata_sphinx_theme'
# html_static_path = ['_static']


autosummary_imported_members = True


html_theme_options = {
    "github_url": "https://github.com/HenryAsa/MIT-rush-auto-calcs",
}


# -----------------------------------------------------------------------------
# Custom event handlers
# -----------------------------------------------------------------------------

from sphinx.application import Sphinx

module_mappings = {
    'cimgt': 'cartopy.io.img_tiles',
    'np': 'numpy',
    'pd': 'pandas',
    'plt': 'matplotlib.pyplt',
    # Add more mappings as needed
}

def replace_modules_with_full_path(app, what, name, obj, options, signature, return_annotation):
    if signature:
        for alias, fullpath in module_mappings.items():
            signature = signature.replace(f'{alias}.', f'{fullpath}.')
    return (signature, return_annotation)

def replace_modules_in_docstring(app, what, name, obj, options, lines):
    for i, line in enumerate(lines):
        for alias, fullpath in module_mappings.items():
            lines[i] = line.replace(f'{alias}.', f'{fullpath}.')

def setup(app: Sphinx):
    app.connect('autodoc-process-signature', replace_modules_with_full_path)
    app.connect('autodoc-process-docstring', replace_modules_in_docstring)
