import os
import re
from typing import Dict


def define_env(env):
    """
    Mandatory to make this a proper MdDocs macro
    """
    pass


TOC_ENTRY_PART1 = r"<li\s*class=\"md-nav__item\">\s*<a\s*href=\""
TOC_ENTRY_PART2 = r"\"\s*class=\"md-nav__link\">([^<]*)</a>\s*</li>\s*"


def find_dummy_h3_entries(content: str) -> Dict[str, str]:
    """
    Find 'dummy <h3>' entries.

    These are <h3> tags that are just redirections to another page.
    These need to be removed, and redirection must be used in TOC.
    """

    ids = {}
    TOC_ENTRY = re.compile(TOC_ENTRY_PART1 + r"(#[^\"]+)" + TOC_ENTRY_PART2, re.M | re.S)
    while True:
        toc_entry = TOC_ENTRY.search(content)
        if toc_entry is None:
            break
        content = content[toc_entry.end() :]
        id = toc_entry.group(1)[1:]
        dummy_h3 = re.search(r"<h3\s+id=\"" + id + r"\">\s*<a\s+href=\"(.*?)\".*?</h3>", content, re.M | re.S)
        if dummy_h3 is not None:
            ids[id] = dummy_h3.group(1)
    return ids


def remove_dummy_h3(content: str, ids: Dict[str, str]) -> str:
    """
    Removes dummy <h3> entries and fix TOC.
    """

    for id, redirect in ids.items():
        # Replace redirection in TOC
        content = re.sub(
            TOC_ENTRY_PART1 + "#" + id + TOC_ENTRY_PART2,
            '<li class="md-nav__item"><a href="' + redirect + '" class="md-nav__link">\\1</a></li>\n',
            content,
            re.M | re.S,
        )
        # Remove dummy <h3>
        content = re.sub(r"<h3\s+id=\"" + id + r"\">\s*<a\s+href=\".*?\".*?</h3>", "", content, re.M | re.S)
    return content


def on_post_build(env):
    "Post-build actions for Taipy"

    site_dir = env.conf["site_dir"]
    for root, _, file_list in os.walk(site_dir):
        for f in file_list:
            if f.endswith(".html"):
                filename = os.path.join(root, f)
                file_was_changed = False
                with open(filename) as html_file:
                    try:
                        html_content = html_file.read()
                    except Exception as e:
                        print(f"Couldn't read HTML file {filename}")
                        raise e
                    # Rebuild coherent links from TOC to sub-pages
                    ids = find_dummy_h3_entries(html_content)
                    if ids:
                        html_content = remove_dummy_h3(html_content, ids)
                        file_was_changed = True
                    # Collapse doubled <h1>/<h2> page titles
                    REPEATED_H1_H2 = re.compile(
                        r"<h1>(.*?)</h1>\s*<h2\s+id=\"(.*?)\">\1(<a\s+class=\"headerlink\".*?</a>)?</h2>", re.M | re.S
                    )
                    html_content, n_changes = REPEATED_H1_H2.subn('<h1 id="\\2">\\1\\3</h1>', html_content)
                    if n_changes != 0:
                        file_was_changed = True
                if file_was_changed:
                    with open(filename, "w") as html_file:
                        html_file.write(html_content)
