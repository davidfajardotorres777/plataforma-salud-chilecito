import pytest
from unittest.mock import patch, MagicMock
from backup_manager import BackupManager

def test_crear_backup_mongodb_error_subprocess():
    backup = BackupManager()

    with patch("backup_manager.subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "mongodump failed"
        mock_run.return_value = mock_result

        with pytest.raises(Exception, match="Error al crear backup: mongodump failed"):
            backup.crear_backup_mongodb("test_backup")
