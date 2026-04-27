#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PACKAGE_DIR="${OPTIMIZESPEC_PY_EXAMPLE_PACKAGE:-$ROOT_DIR/skills/optimizespec-common/references/runtimes/claude-managed-agent/python-managed-agent-package}"
VENV_DIR="${OPTIMIZESPEC_PY_EXAMPLE_VENV:-$ROOT_DIR/.venv/optimizespec-py-managed-agent-example}"
PYTHON_BIN="${PYTHON:-python3}"

if [[ ! -f "$PACKAGE_DIR/pyproject.toml" ]]; then
  echo "Python Managed Agents example package not found: $PACKAGE_DIR" >&2
  exit 1
fi

clean_packaging_artifacts() {
  find "$PACKAGE_DIR" \
    \( -name __pycache__ -o -name '*.pyc' -o -name '*.pyo' -o -name '*.egg-info' -o -name build -o -name dist \) \
    -prune -exec rm -rf {} +
}

if [[ ! -d "$VENV_DIR" ]]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

clean_packaging_artifacts
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip
PIP_NO_COMPILE=1 python -m pip install --no-compile "$PACKAGE_DIR[dev]"
PIP_NO_COMPILE=1 python -m pip install --no-compile -r "$PACKAGE_DIR/requirements-managed-agents-preview.txt"
python -m optimizespec.cli --help >/dev/null
clean_packaging_artifacts

echo "Python Managed Agents example environment ready: $VENV_DIR"
