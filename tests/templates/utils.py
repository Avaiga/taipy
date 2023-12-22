# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import os
import platform
import subprocess
import sys


def _bytes_to_str(b: bytes):
    return str(b, "latin-1" if platform.system() == "Windows" else "utf-8")


def _run_template(taipy_path, cwd, main_path, time_out=30):
    """Run the templates on a subprocess and get stdout after timeout"""
    with subprocess.Popen(
        [sys.executable, main_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
        env=os.environ.copy().update(PYTHONPATH=taipy_path),
    ) as proc:
        try:
            stdout, stderr = proc.communicate(timeout=time_out)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()

    # Print the error if there is any (for debugging)
    if stderr := _bytes_to_str(stderr):
        print(stderr)

    return _bytes_to_str(stdout)
