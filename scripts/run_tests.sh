#!/usr/bin/env sh
export PYTHONDONTWRITEBYTECODE=1
pytest -q -p no:cacheprovider
