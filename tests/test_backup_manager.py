import os
import zipfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from backup_manager import BackupManager

@pytest.fixture
def temp_backup_dir(tmp_path):
    # tmp_path is a pathlib.Path
    return tmp_path

def test_restaurar_backup_mongodb_path_traversal(temp_backup_dir):
    bm = BackupManager(backup_dir=str(temp_backup_dir))

    # Create a fake mongodb backup zip
    backup_id = "test_malicious"
    mongo_dir = temp_backup_dir / "mongodb"
    mongo_dir.mkdir(exist_ok=True)

    zip_path = mongo_dir / f"{backup_id}.zip"
    with zipfile.ZipFile(str(zip_path), 'w') as zf:
        zf.writestr("../../etc/passwd", "malicious content")
        zf.writestr("normal_file.txt", "normal content")
        zf.writestr("../malicious2.txt", "malicious content")

    # We mock get_mongo_config to return dummy config
    # We also mock subprocess.run so we don't actually run mongorestore
    with patch('config_vars.get_mongo_config') as mock_config, \
         patch('subprocess.run') as mock_run:
        mock_config.return_value = {"uri": "mongodb://localhost", "db_name": "testdb"}
        mock_run.return_value = MagicMock(returncode=0)

        # When we try to restore, it should catch the path traversal exception
        # We can capture the stdout or check the return value, the method returns False on Exception
        result = bm.restaurar_backup_mongodb(backup_id)
        assert result is False

def test_restaurar_backup_mongodb_success(temp_backup_dir):
    bm = BackupManager(backup_dir=str(temp_backup_dir))

    # Create a fake mongodb backup zip
    backup_id = "test_normal"
    mongo_dir = temp_backup_dir / "mongodb"
    mongo_dir.mkdir(exist_ok=True)

    zip_path = mongo_dir / f"{backup_id}.zip"
    with zipfile.ZipFile(str(zip_path), 'w') as zf:
        zf.writestr("normal_file.txt", "normal content")
        zf.writestr("some_folder/other_file.txt", "normal content")

    with patch('config_vars.get_mongo_config') as mock_config, \
         patch('subprocess.run') as mock_run:
        mock_config.return_value = {"uri": "mongodb://localhost", "db_name": "testdb"}
        mock_run.return_value = MagicMock(returncode=0)

        # When we try to restore, it should succeed
        result = bm.restaurar_backup_mongodb(backup_id)
        assert result is True
        mock_run.assert_called_once()
