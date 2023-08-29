import sys

pages = "{{ cookiecutter.__pages }}".split(" ")
# Remove empty string from pages list
pages = [page for page in pages if page != ""]

for page in pages:
    if not page.isidentifier():
        sys.exit(f'Page name "{page}" is not a valid Python identifier. Please choose another name.')
