"""
Sistema de Webhooks para sincronización bidireccional con sistemas hospitalarios.

Permite que los hospitales reciban notificaciones en tiempo real cuando ocurren eventos
en Salud Chilecito (ej: turno creado, turno cancelado, paciente actualizado).
"""

import json
import secrets
import hashlib
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path
import requests


class WebhookManager:
    """Gestión de webhooks para integración con sistemas externos."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path("runtime/webhooks.json")
        self.webhooks = self._load_webhooks()
    
    def _load_webhooks(self) -> Dict:
        """Carga los webhooks desde el almacenamiento."""
        if self.storage_path.exists():
            return json.loads(self.storage_path.read_text(encoding="utf-8"))
        return {}
    
    def _save_webhooks(self) -> None:
        """Guarda los webhooks en el almacenamiento."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.storage_path.write_text(json.dumps(self.webhooks, indent=2, ensure_ascii=False), encoding="utf-8")
    
    def register_webhook(self, hospital_id: int, url: str, events: List[str], 
                         secret: Optional[str] = None) -> str:
        """
        Registra un nuevo webhook para un hospital.
        
        Args:
            hospital_id: ID del hospital
            url: URL donde se enviarán las notificaciones
            events: Lista de eventos a suscribir (ej: ["turno.created", "turno.cancelled"])
            secret: Secreto para firmar los payloads (opcional, se genera uno si no se proporciona)
        
        Returns:
            ID del webhook registrado
        """
        webhook_id = secrets.token_hex(16)
        if not secret:
            secret = secrets.token_hex(32)
        
        self.webhooks[webhook_id] = {
            "hospital_id": hospital_id,
            "url": url,
            "events": events,
            "secret": secret,
            "created_at": datetime.now().isoformat(),
            "is_active": True,
            "delivery_stats": {
                "total_sent": 0,
                "successful": 0,
                "failed": 0
            }
        }
        
        self._save_webhooks()
        return webhook_id
    
    def unregister_webhook(self, webhook_id: str) -> bool:
        """
        Elimina un webhook.
        
        Args:
            webhook_id: ID del webhook a eliminar
        
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        if webhook_id not in self.webhooks:
            return False
        
        del self.webhooks[webhook_id]
        self._save_webhooks()
        return True
    
    def get_webhooks(self, hospital_id: Optional[int] = None) -> List[Dict]:
        """
        Obtiene los webhooks registrados.
        
        Args:
            hospital_id: Filtrar por hospital_id (opcional)
        
        Returns:
            Lista de webhooks (sin mostrar el secreto por seguridad)
        """
        webhooks_list = []
        
        for webhook_id, webhook_data in self.webhooks.items():
            if hospital_id and webhook_data["hospital_id"] != hospital_id:
                continue
            
            # No mostrar el secreto completo
            safe_webhook = webhook_data.copy()
            safe_webhook["id"] = webhook_id
            safe_webhook["secret"] = f"***{safe_webhook['secret'][-8:]}" if safe_webhook.get("secret") else None
            
            webhooks_list.append(safe_webhook)
        
        return webhooks_list
    
    def trigger_event(self, event_type: str, data: Dict) -> None:
        """
        Dispara un evento a todos los webhooks suscritos.
        
        Args:
            event_type: Tipo de evento (ej: "turno.created")
            data: Datos del evento
        """
        for webhook_id, webhook_data in self.webhooks.items():
            if not webhook_data["is_active"]:
                continue
            
            if event_type not in webhook_data["events"]:
                continue
            
            # Enviar en background para no bloquear
            self._send_webhook(webhook_id, webhook_data, event_type, data)
    
    def _send_webhook(self, webhook_id: str, webhook_data: Dict, 
                     event_type: str, data: Dict) -> None:
        """
        Envía un webhook a la URL registrada.
        
        Args:
            webhook_id: ID del webhook
            webhook_data: Datos del webhook
            event_type: Tipo de evento
            data: Datos del evento
        """
        payload = {
            "id": secrets.token_hex(16),
            "event": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        # Firmar el payload si hay secreto
        headers = {"Content-Type": "application/json"}
        if webhook_data.get("secret"):
            signature = self._sign_payload(payload, webhook_data["secret"])
            headers["X-Webhook-Signature"] = signature
        
        try:
            response = requests.post(
                webhook_data["url"],
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code in [200, 201, 202]:
                webhook_data["delivery_stats"]["total_sent"] += 1
                webhook_data["delivery_stats"]["successful"] += 1
            else:
                webhook_data["delivery_stats"]["total_sent"] += 1
                webhook_data["delivery_stats"]["failed"] += 1
                
        except Exception as e:
            webhook_data["delivery_stats"]["total_sent"] += 1
            webhook_data["delivery_stats"]["failed"] += 1
            print(f"Error sending webhook {webhook_id}: {e}")
        
        self._save_webhooks()
    
    def _sign_payload(self, payload: Dict, secret: str) -> str:
        """
        Firma el payload con HMAC-SHA256.
        
        Args:
            payload: Payload a firmar
            secret: Secreto para firmar
        
        Returns:
            Firma hexadecimal
        """
        import hmac
        
        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"sha256={signature}"
    
    def verify_signature(self, payload: Dict, signature: str, secret: str) -> bool:
        """
        Verifica la firma de un webhook.
        
        Args:
            payload: Payload recibido
            signature: Firma recibida (X-Webhook-Signature header)
            secret: Secreto del webhook
        
        Returns:
            True si la firma es válida, False en caso contrario
        """
        expected_signature = self._sign_payload(payload, secret)
        return hmac.compare_digest(expected_signature, signature)


class EventTypes:
    """Tipos de eventos disponibles para webhooks."""
    
    # Eventos de turnos
    TURNO_CREATED = "turno.created"
    TURNO_UPDATED = "turno.updated"
    TURNO_CANCELLED = "turno.cancelled"
    TURNO_CONFIRMED = "turno.confirmed"
    
    # Eventos de pacientes
    PACIENTE_CREATED = "paciente.created"
    PACIENTE_UPDATED = "paciente.updated"
    
    # Eventos de médicos
    MEDICO_CREATED = "medico.created"
    MEDICO_UPDATED = "medico.updated"
    
    # Eventos de agendas
    AGENDA_CREATED = "agenda.created"
    AGENDA_UPDATED = "agenda.updated"
    AGENDA_DELETED = "agenda.deleted"
    
    # Eventos de documentos
    DOCUMENTO_UPLOADED = "documento.uploaded"
    
    @classmethod
    def all_events(cls) -> List[str]:
        """Retorna todos los eventos disponibles."""
        return [
            cls.TURNO_CREATED, cls.TURNO_UPDATED, cls.TURNO_CANCELLED, cls.TURNO_CONFIRMED,
            cls.PACIENTE_CREATED, cls.PACIENTE_UPDATED,
            cls.MEDICO_CREATED, cls.MEDICO_UPDATED,
            cls.AGENDA_CREATED, cls.AGENDA_UPDATED, cls.AGENDA_DELETED,
            cls.DOCUMENTO_UPLOADED
        ]


# Instancia global
webhook_manager = WebhookManager()
