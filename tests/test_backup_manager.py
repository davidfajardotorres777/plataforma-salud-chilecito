import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from backup_manager import BackupManager


@pytest.fixture
def backup_manager_instance():
    # Use patch to mock the directories creation during init
    with patch("backup_manager.Path.mkdir"):
        return BackupManager(backup_dir="mocked_backups")


@patch("backup_manager.datetime")
def test_limpiar_backups_antiguos_ninguno(mock_datetime, backup_manager_instance):
    # Setup mock date: Nov 30, 2023
    mock_now = datetime(2023, 11, 30)
    mock_datetime.now.return_value = mock_now
    mock_datetime.fromisoformat.side_effect = datetime.fromisoformat

    # Set up some dummy recent backups (e.g. 5 days ago)
    recent_date = (mock_now - timedelta(days=5)).isoformat()
    mock_backups = [
        {"id": "b1", "tipo": "mongodb", "fecha": recent_date},
        {"id": "b2", "tipo": "redis", "fecha": recent_date},
    ]

    with patch.object(backup_manager_instance, "listar_backups", return_value=mock_backups) as mock_listar:
        with patch.object(backup_manager_instance, "eliminar_backup") as mock_eliminar:
            # Execute
            deleted = backup_manager_instance.limpiar_backups_antiguos(dias=30)

            # Verify
            assert deleted == 0
            mock_listar.assert_called_once_with()
            mock_eliminar.assert_not_called()


@patch("backup_manager.datetime")
def test_limpiar_backups_antiguos_algunos(mock_datetime, backup_manager_instance):
    mock_now = datetime(2023, 11, 30)
    mock_datetime.now.return_value = mock_now
    mock_datetime.fromisoformat.side_effect = datetime.fromisoformat

    old_date1 = (mock_now - timedelta(days=35)).isoformat()
    old_date2 = (mock_now - timedelta(days=40)).isoformat()
    recent_date = (mock_now - timedelta(days=10)).isoformat()

    mock_backups = [
        {"id": "old1", "tipo": "mongodb", "fecha": old_date1},
        {"id": "old2", "tipo": "redis", "fecha": old_date2},
        {"id": "recent1", "tipo": "mongodb", "fecha": recent_date},
    ]

    with patch.object(backup_manager_instance, "listar_backups", return_value=mock_backups) as mock_listar:
        with patch.object(backup_manager_instance, "eliminar_backup", return_value=True) as mock_eliminar:
            # Execute
            deleted = backup_manager_instance.limpiar_backups_antiguos(dias=30)

            # Verify
            assert deleted == 2
            mock_listar.assert_called_once_with()
            assert mock_eliminar.call_count == 2
            mock_eliminar.assert_any_call("old1", "mongodb")
            mock_eliminar.assert_any_call("old2", "redis")


@patch("backup_manager.datetime")
def test_limpiar_backups_antiguos_fallo_eliminar(mock_datetime, backup_manager_instance):
    mock_now = datetime(2023, 11, 30)
    mock_datetime.now.return_value = mock_now
    mock_datetime.fromisoformat.side_effect = datetime.fromisoformat

    old_date1 = (mock_now - timedelta(days=35)).isoformat()
    old_date2 = (mock_now - timedelta(days=40)).isoformat()

    mock_backups = [
        {"id": "old1", "tipo": "mongodb", "fecha": old_date1},
        {"id": "old2", "tipo": "redis", "fecha": old_date2},
    ]

    with patch.object(backup_manager_instance, "listar_backups", return_value=mock_backups) as mock_listar:
        with patch.object(backup_manager_instance, "eliminar_backup") as mock_eliminar:
            # Mock eliminar_backup to fail on the first call and succeed on the second
            mock_eliminar.side_effect = [False, True]

            # Execute
            deleted = backup_manager_instance.limpiar_backups_antiguos(dias=30)

            # Verify
            assert deleted == 1
            mock_listar.assert_called_once_with()
            assert mock_eliminar.call_count == 2


@patch("backup_manager.datetime")
def test_limpiar_backups_antiguos_dias_personalizados(mock_datetime, backup_manager_instance):
    mock_now = datetime(2023, 11, 30)
    mock_datetime.now.return_value = mock_now
    mock_datetime.fromisoformat.side_effect = datetime.fromisoformat

    date15 = (mock_now - timedelta(days=15)).isoformat()
    date5 = (mock_now - timedelta(days=5)).isoformat()

    mock_backups = [
        {"id": "b15", "tipo": "mongodb", "fecha": date15},
        {"id": "b5", "tipo": "redis", "fecha": date5},
    ]

    with patch.object(backup_manager_instance, "listar_backups", return_value=mock_backups) as mock_listar:
        with patch.object(backup_manager_instance, "eliminar_backup", return_value=True) as mock_eliminar:
            # Execute with dias=10
            deleted = backup_manager_instance.limpiar_backups_antiguos(dias=10)

            # Verify
            assert deleted == 1
            mock_listar.assert_called_once_with()
            mock_eliminar.assert_called_once_with("b15", "mongodb")
