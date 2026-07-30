#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$PROJECT_DIR"

if [ ! -x .venv/bin/python ]; then
    echo "Virtual environment not found. Run ./setup.sh first."
    exit 1
fi

PYTHON=.venv/bin/python
SCHEMA_FILE=${TMPDIR:-/tmp}/course-attendance-schema.yml

$PYTHON manage.py check
$PYTHON manage.py makemigrations --check --dry-run
$PYTHON manage.py test
$PYTHON manage.py spectacular --file "$SCHEMA_FILE" --validate

echo "All project verification checks passed."
echo "Validated schema: $SCHEMA_FILE"
