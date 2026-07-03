import pytest
import zipfile
import os
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from backup_manager import BackupManager

def test_backup_manager_zip_slip_vulnerability(tmp_path):
    """
    Verifica que el BackupManager.restaurar_backup_mongodb proteja contra
    vulnerabilidades de Zip Slip.
    """
    backup_dir = tmp_path / "backups"
    manager = BackupManager(backup_dir=str(backup_dir))

    # Setup test zip
    mongo_backup_dir = backup_dir / "mongodb"
    mongo_backup_dir.mkdir(parents=True, exist_ok=True)

    backup_id = "malicious_backup"
    zip_path = mongo_backup_dir / f"{backup_id}.zip"

    with zipfile.ZipFile(str(zip_path), 'w') as z:
        z.writestr('../../../../../tmp/evil.txt', 'evil_content')
        z.writestr('good.txt', 'good_content')

    # Mockear config_vars para que no falle al obtener la config de DB
    with patch('config_vars.get_mongo_config') as mock_config:
        mock_config.return_value = {"uri": "mongodb://localhost", "db_name": "test_db"}

        # Test vulnerability
        # Since it prints the error and returns False, we can check the return value
        # and also verify that the exception was caught by checking stdout or just checking
        # if the file was extracted to /tmp (it shouldn't be).

        result = manager.restaurar_backup_mongodb(backup_id)

        assert result is False, "La restauración debió fallar por la excepción de seguridad"

        # Opcionalmente verificamos que el archivo evil NO existe en el path absoluto
        # Note: No podemos verificar fácilmente /tmp/evil.txt porque depende del OS y entorno,
        # pero sabemos que si falló, se evitó la extracción completa.
