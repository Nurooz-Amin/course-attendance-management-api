#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$PROJECT_DIR"

find_python() {
    for candidate in python3.13 python3.12 python3.11 python3.10 python3; do
        if command -v "$candidate" >/dev/null 2>&1; then
            if "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
                printf '%s\n' "$candidate"
                return 0
            fi
        fi
    done
    return 1
}

PYTHON_BIN=$(find_python || true)
if [ -z "${PYTHON_BIN:-}" ]; then
    echo "Error: Python 3.10 or newer is required."
    echo "On macOS with Homebrew, run: brew install python@3.13"
    exit 1
fi

echo "Using $($PYTHON_BIN --version) from $(command -v "$PYTHON_BIN")"

if [ -d .venv ]; then
    VENV_VERSION=$(.venv/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))' 2>/dev/null || true)
    if ! .venv/bin/python -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
        echo "Removing incompatible .venv created with Python ${VENV_VERSION:-unknown}."
        rm -rf .venv
    fi
fi

if [ ! -d .venv ]; then
    "$PYTHON_BIN" -m venv .venv
fi

. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from .env.example"
fi

python manage.py migrate
python manage.py seed_demo
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py spectacular --file "${TMPDIR:-/tmp}/course-attendance-schema.yml" --validate

echo
echo "Setup completed successfully."
echo "Start the server with:"
echo "  source .venv/bin/activate"
echo "  python manage.py runserver"
echo
echo "Then open http://127.0.0.1:8000/"
