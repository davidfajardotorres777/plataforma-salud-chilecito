import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess
from backup_manager import BackupManager
import os
import shutil
import json
from datetime import datetime

@patch('config_vars.get_mongo_config')
@patch('subprocess.run')
@patch('shutil.make_archive')
def test_crear_backup_mongodb_success(mock_make_archive, mock_run, mock_get_config, tmp_path):
    mock_get_config.return_value = {"uri": "mongodb://localhost", "db_name": "test_db"}
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    # We must mock shutil.make_archive as there isn't actually anything to archive, but the function tries to
    # the function shutil.make_archive returns the path to the zip
    manager = BackupManager(backup_dir=str(tmp_path))

    zip_path = str(tmp_path / "mongodb" / "mi_backup.zip")
    mock_make_archive.return_value = zip_path

    # we need to create an empty zip file so os.path.getsize(zip_path) works
    with open(zip_path, 'wb') as f:
        f.write(b"")

    backup_id = manager.crear_backup_mongodb("mi_backup")

    assert backup_id == "mi_backup"

    # Verificar que el zip y metadata existen
    meta_path = tmp_path / "mongodb" / "mi_backup_metadata.json"

    assert Path(zip_path).exists()
    assert meta_path.exists()

    # Verificar contenido de metadata
    with open(meta_path, 'r') as f:
        metadata = json.load(f)
        assert metadata["id"] == "mi_backup"
        assert metadata["tipo"] == "mongodb"
        assert metadata["archivo"] == "mi_backup.zip"
        assert "fecha" in metadata
        assert metadata["tamaño"] == 0

    # Verificar llamada a subprocess
    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    assert args[0] == [
        "mongodump",
        "--uri", "mongodb://localhost",
        "--db", "test_db",
        "--out", str(tmp_path / "mongodb" / "mi_backup")
    ]

@patch('config_vars.get_mongo_config')
@patch('subprocess.run')
def test_crear_backup_mongodb_failure(mock_run, mock_get_config, tmp_path):
    mock_get_config.return_value = {"uri": "mongodb://localhost", "db_name": "test_db"}
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr="Error dump")

    manager = BackupManager(backup_dir=str(tmp_path))

    with pytest.raises(Exception, match="Error al crear backup: Error dump"):
        manager.crear_backup_mongodb("mi_backup_fail")

@patch('config_vars.get_mongo_config')
@patch('subprocess.run')
@patch('shutil.make_archive')
@patch('backup_manager.datetime')
def test_crear_backup_mongodb_no_name(mock_datetime, mock_make_archive, mock_run, mock_get_config, tmp_path):
    mock_get_config.return_value = {"uri": "mongodb://localhost", "db_name": "test_db"}
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    # mock datetime.now()
    mock_now = datetime(2023, 10, 27, 12, 34, 56)
    mock_datetime.now.return_value = mock_now

    expected_name = "mongodb_20231027_123456"

    manager = BackupManager(backup_dir=str(tmp_path))

    zip_path = str(tmp_path / "mongodb" / f"{expected_name}.zip")
    mock_make_archive.return_value = zip_path

    # we need to create an empty zip file so os.path.getsize(zip_path) works
    with open(zip_path, 'wb') as f:
        f.write(b"")

    backup_id = manager.crear_backup_mongodb()

    assert backup_id == expected_name

    # Verificar que el zip y metadata existen
    meta_path = tmp_path / "mongodb" / f"{expected_name}_metadata.json"

    assert Path(zip_path).exists()
    assert meta_path.exists()
