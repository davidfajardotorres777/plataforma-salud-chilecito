"""
Módulo de backup para Plataforma Salud Chilecito
===============================================
Proporciona funcionalidad de backup y restauración de MongoDB.

Características:
- Backup automático de MongoDB
- Backup incremental
- Restauración de backups
- Retención de backups
- Compresión de backups

Uso básico:
    from backup_manager import BackupManager
    
    backup = BackupManager()
    
    # Crear backup
    backup_id = backup.crear_backup()
    
    # Restaurar backup
    backup.restaurar_backup(backup_id)
    
    # Listar backups
    backups = backup.listar_backups()
"""

import os
import re
import subprocess
import shutil
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path


class BackupManager:
    """
    Gestor de backups para MongoDB.
    
    Proporciona métodos para crear, listar y restaurar backups
    de la base de datos MongoDB.
    """
    
    def __init__(self, backup_dir: str = "backups"):
        """
        Inicializa una nueva instancia del gestor de backups.
        
        Args:
            backup_dir: Directorio donde se almacenarán los backups
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Crear subdirectorios
        (self.backup_dir / "mongodb").mkdir(exist_ok=True)
        (self.backup_dir / "redis").mkdir(exist_ok=True)
    
    def crear_backup_mongodb(self, nombre: Optional[str] = None) -> str:
        """
        Crea un backup de MongoDB.
        
        Args:
            nombre: Nombre del backup (opcional)
        
        Returns:
            str: ID del backup creado
        """
        from config_vars import get_mongo_config
        
        config = get_mongo_config()
        
        # Generar nombre si no se proporciona
        if not nombre:
            nombre = f"mongodb_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_path = self.backup_dir / "mongodb" / nombre
        backup_path.mkdir(exist_ok=True)
        
        try:
            # Usar mongodump para crear el backup
            cmd = [
                "mongodump",
                "--uri", config["uri"],
                "--db", config["db_name"],
                "--out", str(backup_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Comprimir el backup
                zip_path = shutil.make_archive(str(backup_path), 'zip', str(backup_path))
                shutil.rmtree(str(backup_path))
                
                # Guardar metadata
                metadata = {
                    "id": nombre,
                    "tipo": "mongodb",
                    "fecha": datetime.now().isoformat(),
                    "archivo": os.path.basename(zip_path),
                    "tamaño": os.path.getsize(zip_path)
                }
                
                metadata_path = self.backup_dir / "mongodb" / f"{nombre}_metadata.json"
                with open(metadata_path, 'w') as f:
                    import json
                    json.dump(metadata, f, indent=2)
                
                return nombre
            else:
                raise Exception(f"Error al crear backup: {result.stderr}")
        
        except Exception as e:
            print(f"Error al crear backup de MongoDB: {e}")
            raise
    
    def crear_backup_redis(self, nombre: Optional[str] = None) -> str:
        """
        Crea un backup de Redis.
        
        Args:
            nombre: Nombre del backup (opcional)
        
        Returns:
            str: ID del backup creado
        """
        from config_vars import get_redis_config
        
        config = get_redis_config()
        
        # Generar nombre si no se proporciona
        if not nombre:
            nombre = f"redis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_path = self.backup_dir / "redis" / f"{name}.rdb"
        
        try:
            # Usar redis-cli para crear el backup
            cmd = [
                "redis-cli",
                "-h", config["host"],
                "-p", str(config["port"]),
                "BGSAVE"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Copiar el archivo RDB de Redis
                redis_data_dir = "/var/lib/redis"  # Default Redis data directory
                if os.path.exists(redis_data_dir):
                    shutil.copy(os.path.join(redis_data_dir, "dump.rdb"), str(backup_path))
                
                # Guardar metadata
                metadata = {
                    "id": nombre,
                    "tipo": "redis",
                    "fecha": datetime.now().isoformat(),
                    "archivo": os.path.basename(backup_path),
                    "tamaño": os.path.getsize(backup_path) if os.path.exists(backup_path) else 0
                }
                
                metadata_path = self.backup_dir / "redis" / f"{nombre}_metadata.json"
                with open(metadata_path, 'w') as f:
                    import json
                    json.dump(metadata, f, indent=2)
                
                return nombre
            else:
                raise Exception(f"Error al crear backup: {result.stderr}")
        
        except Exception as e:
            print(f"Error al crear backup de Redis: {e}")
            raise
    
    def crear_backup_completo(self, nombre: Optional[str] = None) -> str:
        """
        Crea un backup completo de MongoDB y Redis.
        
        Args:
            nombre: Nombre del backup (opcional)
        
        Returns:
            str: ID del backup creado
        """
        if not nombre:
            nombre = f"completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Crear backup de MongoDB
        mongo_backup_id = self.crear_backup_mongodb(f"{nombre}_mongodb")
        
        # Crear backup de Redis
        redis_backup_id = self.crear_backup_redis(f"{nombre}_redis")
        
        return nombre
    
    def listar_backups(self, tipo: Optional[str] = None) -> List[Dict]:
        """
        Lista todos los backups disponibles.
        
        Args:
            tipo: Tipo de backup (mongodb, redis, completo)
        
        Returns:
            list[dict]: Lista de backups
        """
        backups = []
        
        if tipo in [None, "mongodb"]:
            # Listar backups de MongoDB
            for metadata_file in (self.backup_dir / "mongodb").glob("*_metadata.json"):
                with open(metadata_file, 'r') as f:
                    import json
                    metadata = json.load(f)
                    backups.append(metadata)
        
        if tipo in [None, "redis"]:
            # Listar backups de Redis
            for metadata_file in (self.backup_dir / "redis").glob("*_metadata.json"):
                with open(metadata_file, 'r') as f:
                    import json
                    metadata = json.load(f)
                    backups.append(metadata)
        
        # Ordenar por fecha descendente
        backups.sort(key=lambda x: x["fecha"], reverse=True)
        
        return backups
    
    def restaurar_backup_mongodb(self, backup_id: str) -> bool:
        """
        Restaura un backup de MongoDB.
        
        Args:
            backup_id: ID del backup a restaurar
        
        Returns:
            bool: True si se restauró exitosamente
        """
        if not re.match(r'^[\w\-]+$', backup_id):
            raise ValueError(f"ID de backup inválido: {backup_id}")

        from config_vars import get_mongo_config
        
        config = get_mongo_config()
        
        try:
            # Buscar el archivo de backup
            backup_file = None
            for file in (self.backup_dir / "mongodb").glob(f"{backup_id}.zip"):
                backup_file = file
                break
            
            if not backup_file:
                raise Exception(f"No se encontró el backup {backup_id}")
            
            # Descomprimir el backup
            temp_dir = self.backup_dir / "temp" / backup_id
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            shutil.unpack_archive(str(backup_file), str(temp_dir))
            
            # Usar mongorestore para restaurar
            cmd = [
                "mongorestore",
                "--uri", config["uri"],
                "--db", config["db_name"],
                str(temp_dir / config["db_name"])
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Limpiar directorio temporal
            shutil.rmtree(str(temp_dir))
            
            if result.returncode == 0:
                return True
            else:
                raise Exception(f"Error al restaurar backup: {result.stderr}")
        
        except Exception as e:
            print(f"Error al restaurar backup de MongoDB: {e}")
            return False
    
    def eliminar_backup(self, backup_id: str, tipo: str) -> bool:
        """
        Elimina un backup.
        
        Args:
            backup_id: ID del backup a eliminar
            tipo: Tipo de backup (mongodb, redis)
        
        Returns:
            bool: True si se eliminó exitosamente
        """
        if not re.match(r'^[\w\-]+$', backup_id):
            raise ValueError(f"ID de backup inválido: {backup_id}")

        try:
            if tipo == "mongodb":
                backup_dir = self.backup_dir / "mongodb"
            elif tipo == "redis":
                backup_dir = self.backup_dir / "redis"
            else:
                raise Exception(f"Tipo de backup no válido: {tipo}")
            
            # Eliminar archivo de backup
            for file in backup_dir.glob(f"{backup_id}.*"):
                file.unlink()
            
            return True
        
        except Exception as e:
            print(f"Error al eliminar backup: {e}")
            return False
    
    def limpiar_backups_antiguos(self, dias: int = 30) -> int:
        """
        Elimina backups más antiguos que el número de días especificado.
        
        Args:
            dias: Número de días de retención
        
        Returns:
            int: Número de backups eliminados
        """
        from datetime import timedelta
        
        backups = self.listar_backups()
        fecha_limite = datetime.now() - timedelta(days=dias)
        
        eliminados = 0
        for backup in backups:
            fecha_backup = datetime.fromisoformat(backup["fecha"])
            if fecha_backup < fecha_limite:
                if self.eliminar_backup(backup["id"], backup["tipo"]):
                    eliminados += 1
        
        return eliminados
