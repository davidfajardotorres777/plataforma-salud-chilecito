"""
Rutas API REST para el módulo de Financiamiento
"""

from flask import Blueprint, request, jsonify
from src.services.FinancingService import FinancingService
from src.dao.APISubscriptionDAO import APISubscriptionDAO

# Inicializar DAO y Servicio
subscription_dao = APISubscriptionDAO()
financing_service = FinancingService(subscription_dao)

# Crear blueprint
financing_bp = Blueprint('financing', __name__, url_prefix='/api/financing')


# ===== REGISTRO Y SUSCRIPCIÓN =====

@financing_bp.route('/register', methods=['POST'])
def register_for_api():
    """Registra un usuario para acceso a la API"""
    try:
        data = request.get_json()
        result = financing_service.register_for_api_access(
            user_id=data.get('user_id'),
            organization_name=data.get('organization_name'),
            email=data.get('email'),
            phone=data.get('phone', '')
        )
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@financing_bp.route('/plans', methods=['GET'])
def get_pricing_plans():
    """Obtiene todos los planes de precios disponibles"""
    try:
        plans = financing_service.get_pricing_plans()
        return jsonify({
            "status": "success",
            "plans": plans
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


# ===== UPGRADE DE PLANES =====

@financing_bp.route('/upgrade/request', methods=['POST'])
def request_upgrade():
    """Solicita un upgrade de plan"""
    try:
        data = request.get_json()
        result = financing_service.request_upgrade(
            subscription_id=data.get('subscription_id'),
            target_tier=data.get('target_tier')
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


# ===== PAGOS Y TRANSACCIONES =====

@financing_bp.route('/payment/initiate', methods=['POST'])
def initiate_payment():
    """Inicia una transacción de pago"""
    try:
        data = request.get_json()
        result = financing_service.initiate_payment(
            subscription_id=data.get('subscription_id'),
            amount_usd=data.get('amount_usd'),
            card_last_four=data.get('card_last_four', '4242')
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@financing_bp.route('/payment/simulate', methods=['POST'])
def simulate_payment():
    """Simula el procesamiento de un pago"""
    try:
        data = request.get_json()
        result = financing_service.simulate_payment_processing(
            transaction_id=data.get('transaction_id'),
            success_code=data.get('success_code', 'SUCCESS')
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@financing_bp.route('/upgrade/complete', methods=['POST'])
def complete_upgrade():
    """Completa el upgrade después de un pago exitoso"""
    try:
        data = request.get_json()
        result = financing_service.complete_upgrade(
            subscription_id=data.get('subscription_id'),
            transaction_id=data.get('transaction_id'),
            target_tier=data.get('target_tier')
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


# ===== GESTIÓN DE CLAVES API =====

@financing_bp.route('/api-keys/generate', methods=['POST'])
def generate_api_key():
    """Genera nuevas credenciales de API"""
    try:
        data = request.get_json()
        result = financing_service.generate_api_credentials(
            subscription_id=data.get('subscription_id'),
            key_name=data.get('key_name', '')
        )
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@financing_bp.route('/api-keys/<subscription_id>', methods=['GET'])
def list_api_keys(subscription_id):
    """Lista las claves API de una suscripción"""
    try:
        result = financing_service.list_api_keys(subscription_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@financing_bp.route('/api-keys/<subscription_id>/<key_id>', methods=['DELETE'])
def revoke_api_key(subscription_id, key_id):
    """Revoca una clave API"""
    try:
        result = financing_service.revoke_api_key(subscription_id, key_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


# ===== MONITOREO Y ESTADÍSTICAS =====

@financing_bp.route('/subscription/<subscription_id>/status', methods=['GET'])
def get_subscription_status(subscription_id):
    """Obtiene el estado completo de una suscripción"""
    try:
        result = financing_service.get_subscription_status(subscription_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@financing_bp.route('/subscription/<subscription_id>/payments', methods=['GET'])
def get_payment_history(subscription_id):
    """Obtiene el historial de pagos"""
    try:
        result = financing_service.get_payment_history(subscription_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@financing_bp.route('/statistics', methods=['GET'])
def get_platform_statistics():
    """Obtiene estadísticas de la plataforma de financiamiento"""
    try:
        result = financing_service.get_platform_statistics()
        return jsonify({
            "status": "success",
            "data": result
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
