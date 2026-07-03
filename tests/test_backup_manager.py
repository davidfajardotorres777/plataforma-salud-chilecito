import pytest
from unittest.mock import patch, MagicMock
from backup_manager import BackupManager

def test_crear_backup_mongodb_error_subprocess():
    backup = BackupManager()

    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Error de mongodump"
        mock_run.return_value = mock_result

        with pytest.raises(Exception) as excinfo:
            backup.crear_backup_mongodb()

        assert "Error al crear backup: Error de mongodump" in str(excinfo.value)
