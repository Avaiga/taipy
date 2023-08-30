import re
import sys

repo_name = sys.argv[1]
branch_name = sys.argv[2]
# Regex pattern <img\s+([^>]*?)(?<!['"])(?<!\/)src\s*=\s*(['"])(?!http|\/)(.*?)\2([^>]*?)>
pattern = re.compile("<img\\s+([^>]*?)(?<!['\"])(?<!\\/)src\\s*=\\s*(['\"])(?!http|\\/)(.*?)\\2([^>]*?)>")
replacement = r'<img \1src="https://raw.githubusercontent.com/Avaiga/{repo_name}/{branch_name}/\3"\4>'

with open("README.md") as readme_file:
    readme_str = readme_file.read()
    modified_readme = re.sub(pattern, replacement.format(repo_name=repo_name, branch_name=branch_name), readme_str)

with open("README.md", "w") as readme_file:
    readme_file.write(modified_readme)
