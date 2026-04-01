#!/bin/bash
set -e

: <<'DOCSTRING'
This script formats the codebase using the black formatter.
If the --diff flag is passed, it will only check for formatting issues.
If the --diff flag is not passed, it will format the codebase in place.
DOCSTRING

script_dir="$(dirname "${0}")/.."
diff="false"
for arg in "${@}"; do
  if [ "${arg}" = "--diff" ]; then
    shift
    diff="true"
  elif [ "${arg}" = "--dir" ]; then
    shift # Move to the next argument
    if [ $# -eq 0 ]; then
      echo "Error: --dir requires a value"
      exit 1
    fi
    script_dir="${1}"
  fi
done

cd "${script_dir}"

TARGET_PYTHON_VERSION="py314" # see: black --help (--target-version)

run_formatter_diff() {
  if ! uv run -- black --line-length=120 --diff --check --color --target-version="${TARGET_PYTHON_VERSION}" .; then
    echo "Formatting issues have been found, please run \`make format\` to fix them."
    exit 1
  fi
  echo "No formatting issues found."
}

run_formatter_inplace() {
  uv run -- black --line-length=120 --target-version="${TARGET_PYTHON_VERSION}" .
}

if [ "${diff}" = "true" ]; then
  run_formatter_diff
else
  run_formatter_inplace
fi
