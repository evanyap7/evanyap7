#!/usr/bin/env bash
# Single gate: the pre-commit hook and the refresh workflow both run this.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m compileall -q scripts tests
if command -v ruff >/dev/null; then ruff check .; else uvx ruff check .; fi
python3 -m unittest discover -s tests -v
