# Copyright 2021-2025 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import argparse
import xmltodict
import sys
import subprocess


def check_total_coverage(coverage_file, threshold=80):
    """Check the total project coverage."""
    with open(coverage_file) as f:
        data = xmltodict.parse(f.read())
    total_coverage = float(data['coverage']['@line-rate']) * 100
    print(f"Total Coverage: {total_coverage:.2f}%")
    if total_coverage < threshold:
        print(f"Total project coverage is below {threshold}%: {total_coverage:.2f}%")
        sys.exit(1)


def check_changed_files_coverage(coverage_file, changed_files, threshold=80):
    """Check the coverage of changed files."""
    with open(coverage_file) as f:
        data = xmltodict.parse(f.read())

    # Handle multiple packages in the coverage report
    packages = data["coverage"]["packages"]["package"]
    if not isinstance(packages, list):
        packages = [packages]

    # Extract coverage data for all files
    files = {}
    for package in packages:
        classes = package["classes"]["class"]
        if not isinstance(classes, list):
            classes = [classes]
        for cls in classes:
            files[cls["@filename"]] = float(cls["@line-rate"]) * 100
    qty = 0
    sum_coverage = 0
    for file in changed_files:
        if file in files:
            coverage = files[file]
            print(f"Coverage for {file}: {coverage:.2f}%")
            sum_coverage += coverage
            qty += 1
        else:
            print(f"No coverage data found for {file}")

    if sum_coverage/qty < threshold:
        print(f"Coverage for changed files is below {threshold}%: {sum_coverage/qty:.2f}%")
        sys.exit(1)
    print(f"Coverage for changed files: {sum_coverage/qty:.2f}%")


def get_changed_files(base_branch):
    """Get the list of changed Python files in the pull request."""
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only', f"origin/{base_branch}", '--', '*.py'],
            capture_output=True,
            text=True,
            check=True,
        )
        changed_files = [
            file.replace("taipy/", "") for file in result.stdout.strip().splitlines() if not file.startswith(('tests/', 'tools/'))
        ]
        return changed_files
    except subprocess.CalledProcessError as e:
        print(f"Error fetching changed files: {e}")
        sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Coverage check script.")
    parser.add_argument('command', choices=['check-total', 'check-changed'], help="Command to execute")
    parser.add_argument('--coverage-file', default='coverage.xml', help="Path to the coverage XML file")
    parser.add_argument('--threshold', type=float, default=80, help="Coverage threshold percentage")
    parser.add_argument('--base-branch', help="Base branch for comparing changed files")

    args = parser.parse_args()

    if args.command == 'check-total':
        check_total_coverage(args.coverage_file, args.threshold)
    elif args.command == 'check-changed':
        if not args.base_branch:
            print("Error: --base-branch is required for check-changed")
            sys.exit(1)
        changed_files = get_changed_files(args.base_branch)
        if not changed_files:
            print("No relevant Python files changed.")
            sys.exit(0)
        check_changed_files_coverage(args.coverage_file, changed_files, args.threshold)
