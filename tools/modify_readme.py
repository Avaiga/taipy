# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

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
