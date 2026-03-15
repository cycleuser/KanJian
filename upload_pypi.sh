#!/bin/bash
# Upload KanJian to PyPI
# Usage: ./upload_pypi.sh

set -e

echo "=== Building KanJian package ==="
python -m build

echo ""
echo "=== Checking package files ==="
ls -lh dist/

echo ""
echo "=== Uploading to PyPI ==="
echo "Make sure you have ~/.pypirc configured with your PyPI credentials"
echo "Or set TWINE_USERNAME and TWINE_PASSWORD environment variables"
echo ""

twine upload dist/*

echo ""
echo "=== Upload complete! ==="
echo "Check your package at: https://pypi.org/project/kanjian/"
