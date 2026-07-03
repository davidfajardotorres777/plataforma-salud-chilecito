import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from backup_manager import BackupManager

def test_limpiar_backups_antiguos_elimina_correctamente():
    # Setup
    manager = BackupManager(backup_dir="/tmp/test_backups")

    # Mock data
    now = datetime(2023, 10, 15, 12, 0, 0)
    old_date1 = now - timedelta(days=35)
    old_date2 = now - timedelta(days=40)
    recent_date = now - timedelta(days=10)

    mock_backups = [
        {"id": "backup1", "tipo": "mongodb", "fecha": old_date1.isoformat()},
        {"id": "backup2", "tipo": "redis", "fecha": old_date2.isoformat()},
        {"id": "backup3", "tipo": "mongodb", "fecha": recent_date.isoformat()},
    ]

    with patch('backup_manager.BackupManager.listar_backups', return_value=mock_backups), \
         patch('backup_manager.BackupManager.eliminar_backup', return_value=True) as mock_eliminar, \
         patch('backup_manager.datetime') as mock_datetime:

        mock_datetime.now.return_value = now
        mock_datetime.fromisoformat.side_effect = datetime.fromisoformat

        # Action
        eliminados = manager.limpiar_backups_antiguos(dias=30)

        # Assertions
        assert eliminados == 2
        mock_eliminar.assert_any_call("backup1", "mongodb")
        mock_eliminar.assert_any_call("backup2", "redis")
        assert mock_eliminar.call_count == 2

def test_limpiar_backups_antiguos_falla_eliminacion():
    # Setup
    manager = BackupManager(backup_dir="/tmp/test_backups")

    now = datetime(2023, 10, 15, 12, 0, 0)
    old_date = now - timedelta(days=35)

    mock_backups = [
        {"id": "backup1", "tipo": "mongodb", "fecha": old_date.isoformat()},
    ]

    with patch('backup_manager.BackupManager.listar_backups', return_value=mock_backups), \
         patch('backup_manager.BackupManager.eliminar_backup', return_value=False) as mock_eliminar, \
         patch('backup_manager.datetime') as mock_datetime:

        mock_datetime.now.return_value = now
        mock_datetime.fromisoformat.side_effect = datetime.fromisoformat

        # Action
        eliminados = manager.limpiar_backups_antiguos(dias=30)

        # Assertions
        assert eliminados == 0
        mock_eliminar.assert_called_once_with("backup1", "mongodb")

def test_limpiar_backups_antiguos_sin_backups():
    manager = BackupManager(backup_dir="/tmp/test_backups")

    with patch('backup_manager.BackupManager.listar_backups', return_value=[]), \
         patch('backup_manager.BackupManager.eliminar_backup') as mock_eliminar:

        eliminados = manager.limpiar_backups_antiguos(dias=30)

        assert eliminados == 0
        mock_eliminar.assert_not_called()
