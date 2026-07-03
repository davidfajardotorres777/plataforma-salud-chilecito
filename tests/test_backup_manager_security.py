import pytest
import os
from pathlib import Path
from backup_manager import BackupManager

def test_eliminar_backup_path_traversal():
    """Test that eliminar_backup prevents path traversal via backup_id."""
    manager = BackupManager(backup_dir="tests/test_backups")

    # Valid backup ID should not raise ValueError
    try:
        manager.eliminar_backup("valid-backup-id_123", "mongodb")
    except ValueError:
        pytest.fail("Valid backup_id raised ValueError")

    # Path traversal attempts should raise ValueError
    with pytest.raises(ValueError, match="ID de backup inválido"):
        manager.eliminar_backup("../../../etc/passwd", "mongodb")

    with pytest.raises(ValueError, match="ID de backup inválido"):
        manager.eliminar_backup("foo*bar", "mongodb")

def test_restaurar_backup_mongodb_path_traversal():
    """Test that restaurar_backup_mongodb prevents path traversal via backup_id."""
    manager = BackupManager(backup_dir="tests/test_backups")

    # Path traversal attempts should raise ValueError
    with pytest.raises(ValueError, match="ID de backup inválido"):
        manager.restaurar_backup_mongodb("../../../etc/passwd")

    with pytest.raises(ValueError, match="ID de backup inválido"):
        manager.restaurar_backup_mongodb("some*glob?pattern")
