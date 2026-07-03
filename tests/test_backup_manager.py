import os
import json
import pytest
from unittest.mock import patch, MagicMock
from backup_manager import BackupManager

@patch('config_vars.get_mongo_config')
@patch('subprocess.run')
def test_crear_backup_mongodb_success(mock_subprocess_run, mock_get_mongo_config, tmp_path):
    mock_get_mongo_config.return_value = {"uri": "mongodb://localhost:27017", "db_name": "test_db"}
    mock_subprocess_run.return_value = MagicMock(returncode=0, stderr="")

    manager = BackupManager(backup_dir=str(tmp_path))
    nombre_backup = "test_backup"

    result = manager.crear_backup_mongodb(nombre=nombre_backup)

    # Assertions
    assert result == nombre_backup

    # Check that subprocess.run was called correctly
    expected_cmd = [
        "mongodump",
        "--uri", "mongodb://localhost:27017",
        "--db", "test_db",
        "--out", str(tmp_path / "mongodb" / nombre_backup)
    ]
    mock_subprocess_run.assert_called_once_with(expected_cmd, capture_output=True, text=True)

    # Check that the zip file and metadata file were created
    zip_path = tmp_path / "mongodb" / f"{nombre_backup}.zip"
    metadata_path = tmp_path / "mongodb" / f"{nombre_backup}_metadata.json"

    assert zip_path.exists()
    assert metadata_path.exists()

    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    assert metadata["id"] == nombre_backup
    assert metadata["tipo"] == "mongodb"
    assert "fecha" in metadata
    assert metadata["archivo"] == f"{nombre_backup}.zip"
    assert metadata["tamaño"] >= 0

@patch('config_vars.get_mongo_config')
@patch('subprocess.run')
def test_crear_backup_mongodb_subprocess_failure(mock_subprocess_run, mock_get_mongo_config, tmp_path):
    mock_get_mongo_config.return_value = {"uri": "mongodb://localhost:27017", "db_name": "test_db"}
    mock_subprocess_run.return_value = MagicMock(returncode=1, stderr="Failed to connect")

    manager = BackupManager(backup_dir=str(tmp_path))

    with pytest.raises(Exception) as exc_info:
        manager.crear_backup_mongodb(nombre="test_backup_fail")

    assert "Error al crear backup: Failed to connect" in str(exc_info.value)

@patch('config_vars.get_mongo_config')
@patch('subprocess.run')
@patch('backup_manager.datetime')
def test_crear_backup_mongodb_no_name(mock_datetime, mock_subprocess_run, mock_get_mongo_config, tmp_path):
    mock_get_mongo_config.return_value = {"uri": "mongodb://localhost:27017", "db_name": "test_db"}
    mock_subprocess_run.return_value = MagicMock(returncode=0, stderr="")

    from datetime import datetime
    mock_now = datetime(2023, 10, 27, 12, 0, 0)
    mock_datetime.now.return_value = mock_now

    manager = BackupManager(backup_dir=str(tmp_path))

    result = manager.crear_backup_mongodb()

    expected_name = "mongodb_20231027_120000"
    assert result == expected_name

    # Check that subprocess.run was called with expected path
    expected_cmd = [
        "mongodump",
        "--uri", "mongodb://localhost:27017",
        "--db", "test_db",
        "--out", str(tmp_path / "mongodb" / expected_name)
    ]
    mock_subprocess_run.assert_called_once_with(expected_cmd, capture_output=True, text=True)

    metadata_path = tmp_path / "mongodb" / f"{expected_name}_metadata.json"
    assert metadata_path.exists()
