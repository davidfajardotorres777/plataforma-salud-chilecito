@echo off
set PYTHONDONTWRITEBYTECODE=1
pytest -q -p no:cacheprovider
