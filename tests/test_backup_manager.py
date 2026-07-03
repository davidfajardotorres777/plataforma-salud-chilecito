import os
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from backup_manager import BackupManager


@pytest.fixture
def backup_manager(tmp_path):
    return BackupManager(backup_dir=str(tmp_path / "backups"))


def test_init(tmp_path):
    backup_dir = tmp_path / "backups"
    manager = BackupManager(backup_dir=str(backup_dir))

    assert (backup_dir / "mongodb").exists()
    assert (backup_dir / "mongodb").is_dir()
    assert (backup_dir / "redis").exists()
    assert (backup_dir / "redis").is_dir()


@patch("backup_manager.subprocess.run")
@patch("backup_manager.shutil.make_archive")
@patch("backup_manager.shutil.rmtree")
@patch("backup_manager.os.path.getsize")
@patch("backup_manager.os.path.basename")
def test_crear_backup_mongodb_success(mock_basename, mock_getsize, mock_rmtree, mock_make_archive, mock_run, backup_manager):
    mock_run.return_value = MagicMock(returncode=0, stderr="")
    mock_make_archive.return_value = "dummy_path.zip"
    mock_getsize.return_value = 1024
    mock_basename.return_value = "dummy_path.zip"

    backup_id = backup_manager.crear_backup_mongodb("test_mongo_backup")

    assert backup_id == "test_mongo_backup"
    mock_run.assert_called_once()
    assert "mongodump" in mock_run.call_args[0][0]

    # Check metadata
    metadata_path = backup_manager.backup_dir / "mongodb" / f"{backup_id}_metadata.json"
    assert metadata_path.exists()
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
        assert metadata["id"] == "test_mongo_backup"
        assert metadata["tipo"] == "mongodb"
        assert metadata["archivo"] == "dummy_path.zip"
        assert metadata["tamaño"] == 1024


@patch("backup_manager.subprocess.run")
def test_crear_backup_mongodb_failure(mock_run, backup_manager):
    mock_run.return_value = MagicMock(returncode=1, stderr="Failed to connect")

    with pytest.raises(Exception) as exc_info:
        backup_manager.crear_backup_mongodb("test_mongo_backup_fail")

    assert "Error al crear backup" in str(exc_info.value)


@patch("backup_manager.subprocess.run")
@patch("backup_manager.os.path.exists")
@patch("backup_manager.shutil.copy")
@patch("backup_manager.os.path.getsize")
def test_crear_backup_redis_success(mock_getsize, mock_copy, mock_exists, mock_run, backup_manager):
    mock_run.return_value = MagicMock(returncode=0, stderr="")
    mock_exists.side_effect = lambda p: True
    mock_getsize.return_value = 2048

    backup_id = backup_manager.crear_backup_redis("test_redis_backup")

    assert backup_id == "test_redis_backup"
    mock_run.assert_called_once()
    assert "redis-cli" in mock_run.call_args[0][0]

    # Check metadata
    metadata_path = backup_manager.backup_dir / "redis" / f"{backup_id}_metadata.json"
    assert metadata_path.exists()
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
        assert metadata["id"] == "test_redis_backup"
        assert metadata["tipo"] == "redis"
        assert metadata["archivo"] == f"{backup_id}.rdb"
        assert metadata["tamaño"] == 2048


@patch("backup_manager.subprocess.run")
def test_crear_backup_redis_failure(mock_run, backup_manager):
    mock_run.return_value = MagicMock(returncode=1, stderr="Redis error")

    with pytest.raises(Exception) as exc_info:
        backup_manager.crear_backup_redis("test_redis_fail")

    assert "Error al crear backup" in str(exc_info.value)


@patch.object(BackupManager, "crear_backup_mongodb")
@patch.object(BackupManager, "crear_backup_redis")
def test_crear_backup_completo(mock_crear_redis, mock_crear_mongo, backup_manager):
    mock_crear_mongo.return_value = "mongo_id"
    mock_crear_redis.return_value = "redis_id"

    nombre = "test_completo"
    backup_id = backup_manager.crear_backup_completo(nombre)

    assert backup_id == nombre
    mock_crear_mongo.assert_called_once_with(f"{nombre}_mongodb")
    mock_crear_redis.assert_called_once_with(f"{nombre}_redis")


def test_listar_backups(backup_manager):
    # Setup dummy metadata
    mongo_dir = backup_manager.backup_dir / "mongodb"
    redis_dir = backup_manager.backup_dir / "redis"

    now = datetime.now()

    mongo_meta = {
        "id": "mongo1",
        "tipo": "mongodb",
        "fecha": (now - timedelta(days=1)).isoformat()
    }
    with open(mongo_dir / "mongo1_metadata.json", 'w') as f:
        json.dump(mongo_meta, f)

    redis_meta = {
        "id": "redis1",
        "tipo": "redis",
        "fecha": now.isoformat()
    }
    with open(redis_dir / "redis1_metadata.json", 'w') as f:
        json.dump(redis_meta, f)

    backups = backup_manager.listar_backups()
    assert len(backups) == 2
    # Sorted by date desc
    assert backups[0]["id"] == "redis1"
    assert backups[1]["id"] == "mongo1"

    mongo_backups = backup_manager.listar_backups(tipo="mongodb")
    assert len(mongo_backups) == 1
    assert mongo_backups[0]["id"] == "mongo1"


@patch("backup_manager.subprocess.run")
@patch("backup_manager.shutil.unpack_archive")
@patch("backup_manager.shutil.rmtree")
def test_restaurar_backup_mongodb_success(mock_rmtree, mock_unpack, mock_run, backup_manager):
    mock_run.return_value = MagicMock(returncode=0, stderr="")

    # Create dummy zip file
    mongo_dir = backup_manager.backup_dir / "mongodb"
    backup_id = "test_restore"
    (mongo_dir / f"{backup_id}.zip").touch()

    result = backup_manager.restaurar_backup_mongodb(backup_id)
    assert result is True
    mock_unpack.assert_called_once()
    mock_run.assert_called_once()
    assert "mongorestore" in mock_run.call_args[0][0]


def test_restaurar_backup_mongodb_not_found(backup_manager):
    result = backup_manager.restaurar_backup_mongodb("non_existent_id")
    assert result is False


def test_eliminar_backup(backup_manager):
    mongo_dir = backup_manager.backup_dir / "mongodb"
    backup_id = "test_delete"

    # Create dummy files
    (mongo_dir / f"{backup_id}.zip").touch()
    (mongo_dir / f"{backup_id}_metadata.json").touch()

    result = backup_manager.eliminar_backup(backup_id, "mongodb")
    assert result is True

    assert not (mongo_dir / f"{backup_id}.zip").exists()
    assert not (mongo_dir / f"{backup_id}_metadata.json").exists()


@patch.object(BackupManager, "listar_backups")
@patch.object(BackupManager, "eliminar_backup")
def test_limpiar_backups_antiguos(mock_eliminar, mock_listar, backup_manager):
    now = datetime.now()

    mock_listar.return_value = [
        {"id": "recent", "tipo": "mongodb", "fecha": now.isoformat()},
        {"id": "old1", "tipo": "mongodb", "fecha": (now - timedelta(days=35)).isoformat()},
        {"id": "old2", "tipo": "redis", "fecha": (now - timedelta(days=40)).isoformat()}
    ]

    mock_eliminar.return_value = True

    eliminados = backup_manager.limpiar_backups_antiguos(dias=30)

    assert eliminados == 2
    assert mock_eliminar.call_count == 2
    mock_eliminar.assert_any_call("old1", "mongodb")
    mock_eliminar.assert_any_call("old2", "redis")
