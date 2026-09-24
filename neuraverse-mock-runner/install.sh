#!/bin/bash
# Install script for neuraverse-mock-runner
# Installs private wheels (with --no-deps to avoid broken hardcoded paths),
# then installs the rest via poetry.
# Safe to re-run — skips if already installed.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WHEELS_DIR="$SCRIPT_DIR/../node-template/wheels"

echo "=== Neuraverse Mock Runner — Install ==="

# Ensure 'python' exists (some containers only have python3)
if ! command -v python &>/dev/null && command -v python3 &>/dev/null; then
    ln -sf "$(which python3)" /usr/local/bin/python
    echo "Created python -> python3 symlink"
fi

# Quick check: skip if already installed
if cd "$SCRIPT_DIR" && poetry run python -c "import mock_runner" 2>/dev/null; then
    echo "Mock runner already installed. Skipping."
    echo ""
    echo "Usage:"
    echo "  CLI:  cd $SCRIPT_DIR && poetry run python -m mock_runner.cli --project \${MOCK_RUNNER_PROJECT:-.}"
    echo "  Web:  cd $SCRIPT_DIR && poetry run python -m mock_runner.web.app --project \${MOCK_RUNNER_PROJECT:-.}"
    exit 0
fi

# 0. Clear VIRTUAL_ENV if it points to the system Python — this tricks
#    Poetry into treating /usr as the active venv, which fails on PEP 668
#    (externally-managed-environment) systems.
if [ "$VIRTUAL_ENV" = "/usr" ] || [ "$VIRTUAL_ENV" = "/usr/" ]; then
    unset VIRTUAL_ENV
fi

# 1. Install poetry dependencies (public packages)
echo "Installing poetry dependencies..."
cd "$SCRIPT_DIR"
poetry install --no-root

# 2. Install private wheels with --no-deps (they have broken hardcoded paths in metadata)
echo "Installing private wheels..."
poetry run pip install --no-deps --force-reinstall \
    "$WHEELS_DIR/neuraverse_entities_apis_messages-1.31.0-py3-none-any.whl" \
    "$WHEELS_DIR/lib_python_neuraverse_common-2.5.1-py3-none-any.whl" \
    "$WHEELS_DIR/lib_python_neuraverse_service_grpc-2.1.0-py3-none-any.whl" \
    "$WHEELS_DIR/lib_python_neuraverse_service_http-2.1.0-py3-none-any.whl" \
    "$WHEELS_DIR/lib_python_neuraverse_node_sdk-2.6.0-py3-none-any.whl"

# 3. Install mock_runner package itself
echo "Installing mock_runner package..."
poetry install

echo ""
echo "Installation complete!"
echo ""
echo "Usage:"
echo "  CLI:  cd $SCRIPT_DIR && poetry run python -m mock_runner.cli --project \${MOCK_RUNNER_PROJECT:-.}"
echo "  Web:  cd $SCRIPT_DIR && poetry run python -m mock_runner.web.app --project \${MOCK_RUNNER_PROJECT:-.}"
