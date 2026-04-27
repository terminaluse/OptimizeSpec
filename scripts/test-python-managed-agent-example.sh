#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PACKAGE_DIR="${OPTIMIZESPEC_PY_EXAMPLE_PACKAGE:-$ROOT_DIR/skills/optimizespec-common/references/runtimes/claude-managed-agent/python-managed-agent-package}"
VENV_DIR="${OPTIMIZESPEC_PY_EXAMPLE_VENV:-$ROOT_DIR/.venv/optimizespec-py-managed-agent-example}"
CHECK_ONLY=0
SKIP_SETUP=0

for arg in "$@"; do
  case "$arg" in
    --check-only) CHECK_ONLY=1 ;;
    --no-setup) SKIP_SETUP=1 ;;
    *)
      echo "Unknown argument: $arg" >&2
      exit 2
      ;;
  esac
done

for required in \
  "$PACKAGE_DIR/pyproject.toml" \
  "$PACKAGE_DIR/requirements-managed-agents-preview.txt" \
  "$PACKAGE_DIR/src/optimizespec/cli.py"; do
  if [[ ! -f "$required" ]]; then
    echo "Missing Python example file: $required" >&2
    exit 1
  fi
done

assert_package_clean() {
  local dirty
  dirty="$(
    find "$PACKAGE_DIR" \
      \( -name __pycache__ -o -name '*.pyc' -o -name '*.pyo' -o -name '*.egg-info' -o -name build -o -name dist -o -name .venv -o -name .env -o -name runs \) \
      -print
  )"
  if [[ -n "$dirty" ]]; then
    echo "Python example package contains generated artifacts:" >&2
    echo "$dirty" >&2
    exit 1
  fi
}

assert_package_clean

if [[ "$CHECK_ONLY" == "1" ]]; then
  exit 0
fi

if [[ "$SKIP_SETUP" != "1" || ! -x "$VENV_DIR/bin/python" ]]; then
  "$ROOT_DIR/scripts/setup-python-managed-agent-example.sh"
fi

source "$VENV_DIR/bin/activate"

WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
  echo "ANTHROPIC_API_KEY is required; Python Managed Agents example tests are live-only." >&2
  exit 1
fi

MAX_METRIC_CALLS="${OPTIMIZESPEC_PY_EXAMPLE_MAX_METRIC_CALLS:-8}"
MAX_RUNTIME_SECONDS="${OPTIMIZESPEC_PY_EXAMPLE_MAX_RUNTIME_SECONDS:-120}"

echo "Running Python Managed Agents live optimizer: run_dir=$WORK_DIR/live-optimize max_metric_calls=$MAX_METRIC_CALLS max_runtime_seconds=$MAX_RUNTIME_SECONDS"
PYTHONDONTWRITEBYTECODE=1 python -m optimizespec.cli live-optimize \
  --run-dir "$WORK_DIR/live-optimize" \
  --max-metric-calls "$MAX_METRIC_CALLS" \
  --max-runtime-seconds "$MAX_RUNTIME_SECONDS" >/dev/null

assert_package_clean
echo "Python Managed Agents live example passed."
