"""
DAO para gestionar suscripciones API y pagos
"""

from typing import List, Optional, Dict
from datetime import datetime, timedelta
from src.models.APISubscription import (
    APISubscription, SubscriptionTier, PaymentTransaction, 
    PaymentStatus, APIKey
)
import json


class APISubscriptionDAO:
    """Data Access Object para suscripciones API"""
    
    def __init__(self, storage_path: str = "runtime/subscriptions.json"):
        self.storage_path = storage_path
        self.subscriptions: Dict[str, APISubscription] = {}
        self.transactions: List[PaymentTransaction] = []
        self._load_subscriptions()
    
    def _load_subscriptions(self):
        """Carga suscripciones desde archivo"""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                # Aquí iría la lógica para cargar desde JSON
        except FileNotFoundError:
            self.subscriptions = {}
    
    def _save_subscriptions(self):
        """Guarda suscripciones a archivo"""
        # Implementar guardado en JSON o BD
        pass
    
    # ===== CREAR Y OBTENER SUSCRIPCIONES =====
    
    def create_subscription(self, user_id: str, organization_name: str, 
                          email: str, tier: SubscriptionTier = SubscriptionTier.FREE) -> APISubscription:
        """Crea una nueva suscripción"""
        sub = APISubscription(
            user_id=user_id,
            organization_name=organization_name,
            tier=tier,
            email=email,
            api_request_limit=100 if tier == SubscriptionTier.FREE else 10000
        )
        self.subscriptions[sub.subscription_id] = sub
        self._save_subscriptions()
        return sub
    
    def get_subscription(self, subscription_id: str) -> Optional[APISubscription]:
        """Obtiene una suscripción por ID"""
        return self.subscriptions.get(subscription_id)
    
    def get_subscriptions_by_user(self, user_id: str) -> List[APISubscription]:
        """Obtiene todas las suscripciones de un usuario"""
        return [sub for sub in self.subscriptions.values() if sub.user_id == user_id]
    
    def list_all_subscriptions(self, tier: Optional[SubscriptionTier] = None) -> List[APISubscription]:
        """Lista todas las suscripciones, opcionalmente filtradas por tier"""
        subs = list(self.subscriptions.values())
        if tier:
            subs = [sub for sub in subs if sub.tier == tier]
        return subs
    
    # ===== ACTUALIZAR SUSCRIPCIONES =====
    
    def upgrade_subscription(self, subscription_id: str, new_tier: SubscriptionTier) -> Optional[APISubscription]:
        """Actualiza el tier de una suscripción"""
        sub = self.get_subscription(subscription_id)
        if sub:
            sub.upgrade_tier(new_tier)
            self._save_subscriptions()
        return sub
    
    def suspend_subscription(self, subscription_id: str, reason: str = "") -> bool:
        """Suspende una suscripción"""
        sub = self.get_subscription(subscription_id)
        if sub:
            sub.status = "suspended"
            self._save_subscriptions()
            return True
        return False
    
    def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancela una suscripción"""
        sub = self.get_subscription(subscription_id)
        if sub:
            sub.status = "cancelled"
            self._save_subscriptions()
            return True
        return False
    
    def renew_subscription(self, subscription_id: str) -> Optional[APISubscription]:
        """Renueva una suscripción por otro mes"""
        sub = self.get_subscription(subscription_id)
        if sub:
            sub.expires_at = datetime.now() + timedelta(days=30)
            sub.current_month_requests = 0
            sub.renewed_at = datetime.now()
            sub.status = "active"
            self._save_subscriptions()
        return sub
    
    # ===== GESTIÓN DE CLAVES API =====
    
    def create_api_key(self, subscription_id: str, key_name: str) -> Optional[APIKey]:
        """Crea una nueva clave API"""
        sub = self.get_subscription(subscription_id)
        if sub:
            key = sub.create_api_key(key_name)
            self._save_subscriptions()
            return key
        return None
    
    def revoke_api_key(self, subscription_id: str, key_id: str) -> bool:
        """Revoca una clave API"""
        sub = self.get_subscription(subscription_id)
        if sub:
            result = sub.revoke_api_key(key_id)
            self._save_subscriptions()
            return result
        return False
    
    def get_api_keys(self, subscription_id: str) -> List[APIKey]:
        """Obtiene todas las claves API activas de una suscripción"""
        sub = self.get_subscription(subscription_id)
        if sub:
            return sub.get_active_api_keys()
        return []
    
    # ===== GESTIÓN DE PAGOS =====
    
    def create_payment_transaction(self, subscription_id: str, amount_usd: float,
                                  payment_method: str = "credit_card",
                                  card_last_four: str = "") -> PaymentTransaction:
        """Crea una nueva transacción de pago"""
        transaction = PaymentTransaction(
            subscription_id=subscription_id,
            amount_usd=amount_usd,
            payment_method=payment_method,
            card_last_four=card_last_four,
            description=f"Pago de suscripción - {amount_usd} USD"
        )
        self.transactions.append(transaction)
        return transaction
    
    def process_payment_simulation(self, transaction_id: str, 
                                  success: bool = True,
                                  error_message: str = "") -> Optional[PaymentTransaction]:
        """Simula el procesamiento de un pago"""
        transaction = self._find_transaction(transaction_id)
        if transaction:
            if success:
                transaction.mark_as_completed()
                # Renovar suscripción
                self.renew_subscription(transaction.subscription_id)
            else:
                transaction.mark_as_failed(error_message)
        return transaction
    
    def get_transaction_history(self, subscription_id: str) -> List[PaymentTransaction]:
        """Obtiene el historial de pagos de una suscripción"""
        return [t for t in self.transactions if t.subscription_id == subscription_id]
    
    def get_payment_statistics(self) -> Dict:
        """Obtiene estadísticas de pagos"""
        completed = [t for t in self.transactions if t.status == PaymentStatus.COMPLETED]
        failed = [t for t in self.transactions if t.status == PaymentStatus.FAILED]
        
        total_revenue = sum(t.amount_usd for t in completed)
        
        return {
            "total_transactions": len(self.transactions),
            "completed_transactions": len(completed),
            "failed_transactions": len(failed),
            "total_revenue_usd": total_revenue,
            "average_transaction_usd": total_revenue / len(completed) if completed else 0
        }
    
    # ===== UTILIDADES =====
    
    def _find_transaction(self, transaction_id: str) -> Optional[PaymentTransaction]:
        """Busca una transacción por ID"""
        for t in self.transactions:
            if t.transaction_id == transaction_id:
                return t
        return None
    
    def check_api_request_limit(self, subscription_id: str) -> Dict:
        """Verifica el estado de límite de solicitudes"""
        sub = self.get_subscription(subscription_id)
        if not sub:
            return {"error": "Suscripción no encontrada"}
        
        can_request = sub.can_make_request()
        pricing = sub.get_pricing_info()
        
        return {
            "subscription_id": subscription_id,
            "tier": sub.tier.value,
            "current_requests": sub.current_month_requests,
            "limit": pricing.api_requests_limit,
            "remaining": pricing.api_requests_limit - sub.current_month_requests,
            "can_make_request": can_request,
            "expires_at": sub.expires_at.isoformat(),
            "status": sub.status
        }
    
    def log_api_request(self, subscription_id: str) -> bool:
        """Registra una solicitud API"""
        sub = self.get_subscription(subscription_id)
        if sub:
            result = sub.log_api_request()
            self._save_subscriptions()
            return result
        return False
