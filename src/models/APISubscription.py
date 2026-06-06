"""
Modelo de Suscripción API - Financiamiento y Venta de API Bot IA
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List
import uuid


class SubscriptionTier(Enum):
    """Niveles de suscripción disponibles"""
    FREE = "free"                    # Gratis - 100 req/mes
    STARTER = "starter"              # $9.99 USD/mes - 10k req/mes
    PROFESSIONAL = "professional"    # $49.99 USD/mes - 100k req/mes
    ENTERPRISE = "enterprise"        # $199.99 USD/mes - Ilimitado


class PaymentStatus(Enum):
    """Estados de pago"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


@dataclass
class PricingPlan:
    """Plan de precios"""
    tier: SubscriptionTier
    monthly_price_usd: float
    api_requests_limit: int
    max_concurrent_connections: int
    features: List[str]
    support_level: str  # "email" | "priority" | "dedicated"
    
    def __post_init__(self):
        if self.tier == SubscriptionTier.FREE:
            self.monthly_price_usd = 0.0
        elif self.tier == SubscriptionTier.STARTER:
            self.monthly_price_usd = 9.99
        elif self.tier == SubscriptionTier.PROFESSIONAL:
            self.monthly_price_usd = 49.99
        elif self.tier == SubscriptionTier.ENTERPRISE:
            self.monthly_price_usd = 199.99


@dataclass
class APIKey:
    """Clave API para desarrolladores"""
    key_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    key_secret: str = field(default_factory=lambda: str(uuid.uuid4()).replace("-", ""))
    name: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    is_active: bool = True
    rate_limit_requests_per_minute: int = 60
    
    def mark_as_used(self):
        """Marca la clave como usada"""
        self.last_used = datetime.now()
    
    def get_masked_secret(self) -> str:
        """Retorna la clave ocultada para seguridad"""
        return f"{self.key_secret[:4]}...{self.key_secret[-4:]}"


@dataclass
class APISubscription:
    """Suscripción a la API del Bot IA"""
    subscription_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    organization_name: str = ""
    tier: SubscriptionTier = SubscriptionTier.FREE
    
    # Datos de suscripción
    status: str = "active"  # active | suspended | cancelled
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=30))
    renewed_at: Optional[datetime] = None
    
    # Claves API
    api_keys: List[APIKey] = field(default_factory=list)
    
    # Uso actual del mes
    current_month_requests: int = 0
    api_request_limit: int = 100
    
    # Datos de contacto
    email: str = ""
    phone: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    
    # Metadata
    is_sandbox: bool = True  # Modo de prueba inicialmente
    webhook_url: Optional[str] = None
    
    def can_make_request(self) -> bool:
        """Verifica si puede hacer una solicitud"""
        if self.status != "active":
            return False
        if self.current_month_requests >= self.api_request_limit:
            return False
        if datetime.now() > self.expires_at:
            return False
        return True
    
    def log_api_request(self):
        """Registra una solicitud de API"""
        if self.can_make_request():
            self.current_month_requests += 1
            return True
        return False
    
    def upgrade_tier(self, new_tier: SubscriptionTier):
        """Actualiza el plan de suscripción"""
        self.tier = new_tier
        pricing = self._get_pricing_for_tier(new_tier)
        self.api_request_limit = pricing.api_requests_limit
        self.renewed_at = datetime.now()
    
    def create_api_key(self, name: str) -> APIKey:
        """Crea una nueva clave API"""
        key = APIKey(name=name)
        self.api_keys.append(key)
        return key
    
    def revoke_api_key(self, key_id: str) -> bool:
        """Desactiva una clave API"""
        for key in self.api_keys:
            if key.key_id == key_id:
                key.is_active = False
                return True
        return False
    
    def get_active_api_keys(self) -> List[APIKey]:
        """Obtiene todas las claves API activas"""
        return [key for key in self.api_keys if key.is_active]
    
    def _get_pricing_for_tier(self, tier: SubscriptionTier) -> PricingPlan:
        """Obtiene plan de precios por tier"""
        plans = {
            SubscriptionTier.FREE: PricingPlan(
                tier=SubscriptionTier.FREE,
                monthly_price_usd=0.0,
                api_requests_limit=100,
                max_concurrent_connections=1,
                features=["API básica", "Documentación"],
                support_level="email"
            ),
            SubscriptionTier.STARTER: PricingPlan(
                tier=SubscriptionTier.STARTER,
                monthly_price_usd=9.99,
                api_requests_limit=10000,
                max_concurrent_connections=5,
                features=["API completa", "Webhooks", "Sandbox mode"],
                support_level="email"
            ),
            SubscriptionTier.PROFESSIONAL: PricingPlan(
                tier=SubscriptionTier.PROFESSIONAL,
                monthly_price_usd=49.99,
                api_requests_limit=100000,
                max_concurrent_connections=50,
                features=["API completa", "Webhooks", "Analytics", "Soporte prioritario"],
                support_level="priority"
            ),
            SubscriptionTier.ENTERPRISE: PricingPlan(
                tier=SubscriptionTier.ENTERPRISE,
                monthly_price_usd=199.99,
                api_requests_limit=1000000,
                max_concurrent_connections=500,
                features=["Todo incluido", "SLA garantizado", "Soporte dedicado", "Custom integrations"],
                support_level="dedicated"
            ),
        }
        return plans.get(tier, plans[SubscriptionTier.FREE])
    
    def get_pricing_info(self) -> PricingPlan:
        """Retorna información de precios del tier actual"""
        return self._get_pricing_for_tier(self.tier)


@dataclass
class PaymentTransaction:
    """Transacción de pago"""
    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    subscription_id: str = ""
    amount_usd: float = 0.0
    currency: str = "USD"
    
    status: PaymentStatus = PaymentStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    
    # Simulación de pago
    card_last_four: str = ""
    payment_method: str = "credit_card"  # credit_card | paypal | stripe
    
    # Metadata
    description: str = ""
    error_message: Optional[str] = None
    
    def mark_as_completed(self):
        """Marca pago como completado"""
        self.status = PaymentStatus.COMPLETED
        self.processed_at = datetime.now()
    
    def mark_as_failed(self, error: str = ""):
        """Marca pago como fallido"""
        self.status = PaymentStatus.FAILED
        self.processed_at = datetime.now()
        self.error_message = error
