# 💰 MÓDULO DE FINANCIAMIENTO - Documentación Completa

## 📋 Descripción General

El módulo de **Financiamiento** permite a los dueños de la plataforma **Salud Chilecito** monetizar el acceso a su API Bot IA mediante:

✅ **Planes de suscripción** en 4 niveles (FREE, STARTER, PROFESSIONAL, ENTERPRISE)  
✅ **Solicitud y venta de acceso a la API** del Bot IA  
✅ **Simulador de pagos en dólares** para pruebas  
✅ **Gestión de claves API** por cliente  
✅ **Monitoreo de uso y estadísticas**  
✅ **Historial de transacciones y renovaciones**

---

## 🎯 Planes de Precios

| Plan | Precio/Mes | Requests/Mes | Conexiones | Soporte | Características |
|------|-----------|-------------|-----------|---------|-----------------|
| **FREE** | $0 | 100 | 1 | Email | API básica, Documentación |
| **STARTER** | $9.99 | 10,000 | 5 | Email | API completa, Webhooks, Sandbox |
| **PROFESSIONAL** | $49.99 | 100,000 | 50 | Priority | Analytics, Soporte prioritario |
| **ENTERPRISE** | $199.99 | 1,000,000+ | 500 | Dedicated | SLA, Soporte dedicado, Custom integrations |

---

## 🔗 Endpoints API REST

### 1️⃣ Registro y Suscripción

#### `POST /api/financing/register`
Registra un usuario para acceso a la API

```json
{
  "user_id": "user123",
  "organization_name": "Mi Empresa",
  "email": "contacto@empresa.com",
  "phone": "+54-123-4567"
}
```

**Respuesta:**
```json
{
  "status": "success",
  "subscription_id": "sub_abc123def456",
  "tier": "free",
  "api_key_id": "key_xyz789",
  "api_key_secret": "secret_key_here",
  "message": "Bienvenido al plan FREE. Tienes 100 requests/mes"
}
```

#### `GET /api/financing/plans`
Obtiene todos los planes disponibles

---

## 🖥️ Interfaz Web

### Acceder al módulo:
```
http://localhost:8000/financing
```

### Características de la UI:

📊 **Planes de Precios Interactivos**
- Vista en grid de los 4 planes disponibles
- Card destacada para el plan popular (PROFESSIONAL)
- Selección directa con cálculo automático del monto

🔄 **Simulador de Pagos**
- Ingreso de ID de suscripción
- Selección de monto (o automático por plan)
- Simulación de diferentes escenarios (SUCCESS, FAIL, DECLINED, TIMEOUT)
- Transacción ID generado automáticamente

📈 **Monitor de Estado**
- Consulta de estado de suscripción en tiempo real
- Visualización de uso de requests
- Información de vencimiento y precio

---

## 💡 Flujo de Uso

### 1. **Usuario se registra**
```
POST /api/financing/register
↓
Sistema crea suscripción PLAN FREE
↓
Se genera API Key inicial
```

### 2. **Usuario solicita upgrade**
```
POST /api/financing/upgrade/request
↓
Sistema retorna detalles del nuevo plan
↓
Usuario visualiza precio en USD
```

### 3. **Usuario realiza pago**
```
POST /api/financing/payment/initiate
↓
Sistema genera ID de transacción
↓
POST /api/financing/payment/simulate
↓
Simulador procesa con código seleccionado
↓
Si SUCCESS → Suscripción se actualiza
```

---

## 🚀 Próximas Mejoras

- [ ] Integración con Stripe/PayPal real
- [ ] Renovación automática de suscripciones
- [ ] Dashboard de administrador
- [ ] Reportes de ingresos detallados
- [ ] Soporte para múltiples monedas
- [ ] Webhooks para eventos de suscripción
- [ ] Descuentos por pago anual
