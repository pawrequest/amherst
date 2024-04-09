project = 'Amherst'
author = 'PawRequest'
release = '0.0.1'
copyright = f'2024, {author}'
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
    'sphinx_rtd_dark_mode',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosectionlabel',
]
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_css_files = ['custom.css']

html_context = {
    'display_github': True,
    'github_user': 'PawRequest',
    'github_repo': 'amherst',
}
html_baseurl = 'https://amherst.readthedocs.io/en/latest'

readme_src_files = 'index.rst'
readme_docs_url_type = 'html'
add_module_names = False
# autodoc_member_order = 'bysource'

autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'undoc-members': True,
}