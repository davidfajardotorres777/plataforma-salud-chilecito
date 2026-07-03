import pytest
import os
import json
from unittest.mock import patch, MagicMock
from pathlib import Path
from datetime import datetime, timedelta

from backup_manager import BackupManager

@pytest.fixture
def backup_manager(tmp_path):
    """Fixture that provides a BackupManager instance with a temporary directory."""
    return BackupManager(backup_dir=str(tmp_path / "backups"))

def test_init(tmp_path):
    """Test that __init__ creates the necessary directories."""
    backup_dir = tmp_path / "custom_backups"
    manager = BackupManager(backup_dir=str(backup_dir))

    assert backup_dir.exists()
    assert (backup_dir / "mongodb").exists()
    assert (backup_dir / "redis").exists()
    assert manager.backup_dir == backup_dir

@patch('config_vars.get_mongo_config')
@patch('backup_manager.subprocess.run')
@patch('backup_manager.shutil.make_archive')
@patch('backup_manager.shutil.rmtree')
@patch('backup_manager.os.path.getsize')
def test_crear_backup_mongodb_success(mock_getsize, mock_rmtree, mock_make_archive, mock_run, mock_get_mongo_config, backup_manager):
    """Test successful MongoDB backup creation."""
    # Setup mocks
    mock_get_mongo_config.return_value = {"uri": "mongodb://localhost", "db_name": "test_db"}
    mock_run_result = MagicMock()
    mock_run_result.returncode = 0
    mock_run.return_value = mock_run_result

    mock_make_archive.return_value = str(backup_manager.backup_dir / "mongodb" / "test_backup.zip")
    mock_getsize.return_value = 1024

    # Run method
    backup_id = backup_manager.crear_backup_mongodb("test_backup")

    # Asserts
    assert backup_id == "test_backup"

    # Verify subprocess call
    expected_path = backup_manager.backup_dir / "mongodb" / "test_backup"
    mock_run.assert_called_once_with(
        ["mongodump", "--uri", "mongodb://localhost", "--db", "test_db", "--out", str(expected_path)],
        capture_output=True, text=True
    )

    # Verify metadata file was created
    metadata_file = backup_manager.backup_dir / "mongodb" / "test_backup_metadata.json"
    assert metadata_file.exists()

    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
        assert metadata["id"] == "test_backup"
        assert metadata["tipo"] == "mongodb"
        assert metadata["tamaño"] == 1024

@patch('config_vars.get_mongo_config')
@patch('backup_manager.subprocess.run')
def test_crear_backup_mongodb_error(mock_run, mock_get_mongo_config, backup_manager):
    """Test MongoDB backup creation failure."""
    mock_get_mongo_config.return_value = {"uri": "mongodb://localhost", "db_name": "test_db"}

    mock_run_result = MagicMock()
    mock_run_result.returncode = 1
    mock_run_result.stderr = "Connection failed"
    mock_run.return_value = mock_run_result

    with pytest.raises(Exception) as excinfo:
        backup_manager.crear_backup_mongodb("fail_backup")

    assert "Error al crear backup" in str(excinfo.value)

@patch('config_vars.get_redis_config')
@patch('backup_manager.subprocess.run')
@patch('backup_manager.shutil.copy')
@patch('backup_manager.os.path.exists')
@patch('backup_manager.os.path.getsize')
def test_crear_backup_redis_success(mock_getsize, mock_exists, mock_copy, mock_run, mock_get_redis_config, backup_manager):
    """Test successful Redis backup creation."""
    mock_get_redis_config.return_value = {"host": "localhost", "port": 6379}

    mock_run_result = MagicMock()
    mock_run_result.returncode = 0
    mock_run.return_value = mock_run_result

    mock_exists.return_value = True
    mock_getsize.return_value = 2048
    backup_id = backup_manager.crear_backup_redis("test_redis_backup")

    assert backup_id == "test_redis_backup"

    # Verify subprocess
    mock_run.assert_called_once_with(
        ["redis-cli", "-h", "localhost", "-p", "6379", "BGSAVE"],
        capture_output=True, text=True
    )

    # Verify metadata
    metadata_file = backup_manager.backup_dir / "redis" / "test_redis_backup_metadata.json"
    assert metadata_file.exists()

    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
        assert metadata["id"] == "test_redis_backup"
        assert metadata["tipo"] == "redis"

@patch('config_vars.get_redis_config')
@patch('backup_manager.subprocess.run')
def test_crear_backup_redis_error(mock_run, mock_get_redis_config, backup_manager):
    """Test Redis backup creation failure."""
    mock_get_redis_config.return_value = {"host": "localhost", "port": 6379}

    mock_run_result = MagicMock()
    mock_run_result.returncode = 1
    mock_run_result.stderr = "Redis not reachable"
    mock_run.return_value = mock_run_result

    with pytest.raises(Exception) as excinfo:
        backup_manager.crear_backup_redis("fail_redis")

    assert "Error al crear backup" in str(excinfo.value)

@patch.object(BackupManager, 'crear_backup_mongodb')
@patch.object(BackupManager, 'crear_backup_redis')
def test_crear_backup_completo(mock_crear_redis, mock_crear_mongo, backup_manager):
    """Test full backup creation."""
    mock_crear_mongo.return_value = "mongo_id"
    mock_crear_redis.return_value = "redis_id"

    backup_id = backup_manager.crear_backup_completo("test_completo")

    assert backup_id == "test_completo"
    mock_crear_mongo.assert_called_once_with("test_completo_mongodb")
    mock_crear_redis.assert_called_once_with("test_completo_redis")

def test_listar_backups(backup_manager):
    """Test listing backups sorted by date."""
    # Create fake metadata files
    mongo_dir = backup_manager.backup_dir / "mongodb"
    redis_dir = backup_manager.backup_dir / "redis"

    old_date = (datetime.now() - timedelta(days=2)).isoformat()
    new_date = datetime.now().isoformat()

    with open(mongo_dir / "old_mongodb_metadata.json", "w") as f:
        json.dump({"id": "old", "tipo": "mongodb", "fecha": old_date}, f)

    with open(redis_dir / "new_redis_metadata.json", "w") as f:
        json.dump({"id": "new", "tipo": "redis", "fecha": new_date}, f)

    backups = backup_manager.listar_backups()

    assert len(backups) == 2
    # Should be sorted newest first
    assert backups[0]["id"] == "new"
    assert backups[1]["id"] == "old"

    # Test filtering by type
    mongo_backups = backup_manager.listar_backups(tipo="mongodb")
    assert len(mongo_backups) == 1
    assert mongo_backups[0]["id"] == "old"

@patch('config_vars.get_mongo_config')
@patch('backup_manager.subprocess.run')
@patch('backup_manager.shutil.unpack_archive')
@patch('backup_manager.shutil.rmtree')
def test_restaurar_backup_mongodb_success(mock_rmtree, mock_unpack, mock_run, mock_get_mongo_config, backup_manager):
    """Test successful MongoDB restore."""
    mock_get_mongo_config.return_value = {"uri": "mongodb://localhost", "db_name": "test_db"}

    mock_run_result = MagicMock()
    mock_run_result.returncode = 0
    mock_run.return_value = mock_run_result

    # Create fake backup zip
    mongo_dir = backup_manager.backup_dir / "mongodb"
    fake_zip = mongo_dir / "test_restore.zip"
    fake_zip.touch()

    result = backup_manager.restaurar_backup_mongodb("test_restore")

    assert result is True

    expected_temp_dir = backup_manager.backup_dir / "temp" / "test_restore"
    mock_unpack.assert_called_once_with(str(fake_zip), str(expected_temp_dir))

    mock_run.assert_called_once_with(
        ["mongorestore", "--uri", "mongodb://localhost", "--db", "test_db", str(expected_temp_dir / "test_db")],
        capture_output=True, text=True
    )
    mock_rmtree.assert_called_once_with(str(expected_temp_dir))

def test_restaurar_backup_mongodb_error_not_found(backup_manager):
    """Test restore fails when backup not found."""
    result = backup_manager.restaurar_backup_mongodb("nonexistent")
    assert result is False

def test_eliminar_backup(backup_manager):
    """Test backup deletion."""
    mongo_dir = backup_manager.backup_dir / "mongodb"
    fake_zip = mongo_dir / "test_delete.zip"
    fake_meta = mongo_dir / "test_delete_metadata.json"
    # Also create a file that matches what the metadata filename actually is
    # Actually the code saves metadata as f"{nombre}_metadata.json"
    # But the delete method does `glob(f"{backup_id}.*")` which will only match `test_delete.zip` and not `test_delete_metadata.json` if we just do `test_delete.*`.
    # The bug in the code is that it doesnt delete metadata if it just matches `test_delete.*`. Wait. `backup_id` is the `nombre` without extension. `test_delete.*` matches `test_delete.zip`. It does NOT match `test_delete_metadata.json`.

    fake_zip.touch()
    fake_meta.touch()

    assert fake_zip.exists()
    assert fake_meta.exists()

    result = backup_manager.eliminar_backup("test_delete", "mongodb")

    assert result is True
    assert not fake_zip.exists()
    assert not fake_meta.exists()

    # Test invalid type
    result_invalid = backup_manager.eliminar_backup("test", "invalid_type")
    assert result_invalid is False

@patch.object(BackupManager, 'listar_backups')
@patch.object(BackupManager, 'eliminar_backup')
def test_limpiar_backups_antiguos(mock_eliminar, mock_listar, backup_manager):
    """Test clearing old backups."""
    old_date = (datetime.now() - timedelta(days=40)).isoformat()
    new_date = (datetime.now() - timedelta(days=10)).isoformat()

    mock_listar.return_value = [
        {"id": "old_backup", "tipo": "mongodb", "fecha": old_date},
        {"id": "new_backup", "tipo": "redis", "fecha": new_date}
    ]

    mock_eliminar.return_value = True

    eliminados = backup_manager.limpiar_backups_antiguos(dias=30)

    assert eliminados == 1
    mock_eliminar.assert_called_once_with("old_backup", "mongodb")
