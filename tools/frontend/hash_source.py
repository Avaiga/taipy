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

import hashlib
import os
import sys

ignore_folder = ["node_modules", "dist", "coverage", "build", "scripts", "test-config"]
ignore_file_name = [
    "DS_Store",
    "env.local",
    "env.development.local",
    "env.test.local",
    "env.production.local",
    ".eslintrc.js",
    ".gitignore",
    "jest.config.js",
    "typedoc-mkdocs.json",
    ".env",
    "dev.env",
]
ignore_file_extension = [".md"]


def hash_file(file_path):
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()


def hash_files_in_frontend_folder(frontend_folder):
    combined_hasher = hashlib.sha256()
    file_hashes = {}
    lookup_fe_folder = [f"{frontend_folder}{os.sep}taipy", f"{frontend_folder}{os.sep}taipy-gui"]
    if len(sys.argv) > 1 and sys.argv[1] == "--taipy-gui-only":
        lookup_fe_folder.pop(0)
    for root_folder in lookup_fe_folder:
        # Sort before looping to ensure consistent cache key
        for root, _, files in sorted(os.walk(root_folder)):
            if any(ignore in root for ignore in ignore_folder):
                continue
            # Sort before looping to ensure consistent cache key
            for file in sorted(files):
                if any(ignore in file for ignore in ignore_file_name):
                    continue
                if any(file.endswith(ignore) for ignore in ignore_file_extension):
                    continue
                file_path = os.path.join(root, file)
                file_hash = hash_file(file_path)
                file_hashes[file_path] = file_hash
                combined_hasher.update(file_hash.encode())

    combined_hash = combined_hasher.hexdigest()
    return file_hashes, combined_hash


if __name__ == "__main__":
    frontend_folder = "frontend"
    file_hashes, combined_hash = hash_files_in_frontend_folder(frontend_folder)
    # for path, file_hash in sorted(file_hashes.items()):
    #     print(f"{path}: {file_hash}")
    print(f"Taipy Frontend hash {combined_hash}")  # noqa: T201
    # write combined hash to file
    with open("hash.txt", "w") as f:
        f.write(combined_hash)
