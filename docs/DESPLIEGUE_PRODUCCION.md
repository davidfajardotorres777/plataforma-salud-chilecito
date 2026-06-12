# Despliegue en Producción - Plataforma Salud Chilecito

Este documento describe cómo desplegar la plataforma Salud Chilecito en un entorno de producción accesible desde internet (no localhost).

## Arquitectura de Producción

La plataforma utiliza:
- **MongoDB**: Base de datos principal
- **Redis**: Caché y gestión de sesiones
- **Python**: Backend con FastAPI/Flask
- **JavaScript**: Frontend

## Opciones de Despliegue

### Opción 1: Render (Recomendado para inicio rápido)

Render es una plataforma PaaS fácil de usar que soporta MongoDB, Redis y aplicaciones Python.

#### Paso 1: Crear cuenta en Render
1. Visita [render.com](https://render.com)
2. Crea una cuenta gratuita
3. Conecta tu repositorio de GitHub

#### Paso 2: Desplegar MongoDB
1. En Render, crea un nuevo "Web Service"
2. Selecciona "MongoDB" como tipo de servicio
3. Configura:
   - Nombre: `salud-chilecito-mongodb`
   - Región: La más cercana a tus usuarios
   - Plan: Free (para desarrollo) o Starter (para producción)
4. Copia la URL de conexión (MongoDB URI)

#### Paso 3: Desplegar Redis
1. En Render, crea un nuevo "Web Service"
2. Selecciona "Redis" como tipo de servicio
3. Configura:
   - Nombre: `salud-chilecito-redis`
   - Región: La misma que MongoDB
   - Plan: Free (para desarrollo) o Starter (para producción)
4. Copia la URL de conexión (Redis URL)

#### Paso 4: Desplegar la Aplicación
1. En Render, crea un nuevo "Web Service"
2. Selecciona tu repositorio
3. Configura:
   - Nombre: `salud-chilecito`
   - Runtime: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python -m src.webapp.server`
4. Agrega las siguientes variables de entorno:
   ```
   MONGO_URI=mongodb+srv://usuario:password@cluster.mongodb.net/salud_chilecito
   DB_NAME=salud_chilecito
   REDIS_HOST=redis-host
   REDIS_PORT=6379
   REDIS_PASSWORD=redis-password
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=tu_email@gmail.com
   SMTP_PASSWORD=tu_password_de_app
   FROM_EMAIL=noreply@saludchilecito.com
   SECRET_KEY=tu-clave-secreta-aqui-cambiala-en-produccion
   BASE_URL=https://salud-chilecito.onrender.com
   ENVIRONMENT=production
   ```

#### Paso 5: Configurar Dominio Personal (Opcional)
1. En Render, ve a tu servicio
2. En "Settings", selecciona "Domains"
3. Agrega tu dominio personal (ej: `saludchilecito.com`)
4. Configura los DNS según las instrucciones de Render

### Opción 2: Railway (Alternativa Simple)

Railway es otra plataforma PaaS que soporta MongoDB, Redis y aplicaciones Python.

#### Paso 1: Crear cuenta en Railway
1. Visita [railway.app](https://railway.app)
2. Crea una cuenta gratuita
3. Conecta tu repositorio de GitHub

#### Paso 2: Crear Proyecto
1. Crea un nuevo proyecto
2. Agrega tu repositorio
3. Railway detectará automáticamente que es una aplicación Python

#### Paso 3: Agregar Servicios
1. Agrega un servicio MongoDB
2. Agrega un servicio Redis
3. Configura las variables de entorno en la aplicación principal

### Opción 3: AWS (Para despliegues empresariales)

Para despliegues más complejos o de alto tráfico, AWS ofrece más control.

#### Servicios AWS necesarios:
- **Amazon DocumentDB** o **MongoDB Atlas**: Base de datos
- **ElastiCache**: Redis
- **Elastic Beanstalk** o **EC2**: Aplicación
- **Route 53**: DNS
- **Certificate Manager**: SSL/TLS

#### Configuración básica:
1. Crea una VPC en AWS
2. Despliega DocumentDB en la VPC
3. Despliega ElastiCache en la VPC
4. Despliega Elastic Beanstalk con tu aplicación
5. Configura Route 53 para tu dominio

## Configuración de Variables de Entorno

Para producción, asegúrate de configurar correctamente las siguientes variables:

### Base de Datos
```env
MONGO_URI=mongodb+srv://usuario:password@cluster.mongodb.net/salud_chilecito
DB_NAME=salud_chilecito
```

### Redis
```env
REDIS_HOST=redis-host
REDIS_PORT=6379
REDIS_PASSWORD=redis-password
REDIS_DB=0
```

### Email (SMTP)
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tu_email@gmail.com
SMTP_PASSWORD=tu_password_de_app
FROM_EMAIL=noreply@saludchilecito.com
```

### Aplicación
```env
SECRET_KEY=tu-clave-secreta-aqui-cambiala-en-produccion
BASE_URL=https://tu-dominio.com
ENVIRONMENT=production
```

**IMPORTANTE**: Genera una clave secreta segura para producción:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Seguridad en Producción

### 1. HTTPS/SSL
- Configura SSL/TLS en tu plataforma de despliegue
- Redirige todo el tráfico HTTP a HTTPS
- Usa certificados SSL válidos (Let's Encrypt es gratuito)

### 2. Variables de Entorno
- Nunca commits el archivo `.env`
- Usa `.env.example` como plantilla
- Configura todas las credenciales como secretos en tu plataforma de despliegue

### 3. Base de Datos
- Usa autenticación de MongoDB
- Configura IP whitelisting si es posible
- Habilita backups automáticos
- Usa MongoDB Atlas para backups automáticos y seguridad

### 4. Redis
- Configura contraseña de Redis
- Usa TLS para conexiones a Redis
- Configura persistencia de datos

## Monitoreo y Logs

### Render
- Render proporciona logs en tiempo real
- Métricas básicas de CPU, memoria y red
- Alertas por email para errores

### Railway
- Logs en tiempo real
- Métricas de recursos
- Integración con Slack para alertas

### AWS
- CloudWatch para logs y métricas
- CloudTrail para auditoría
- SNS para alertas

## Backups

### MongoDB Atlas
- Backups automáticos diarios
- Snapshots point-in-time
- Retención configurable

### Render
- Backups de base de datos incluidos en planes pagos
- Snapshots manuales disponibles

## Escalado

### Horizontal
- Aumenta el número de instancias de la aplicación
- Configura un load balancer
- MongoDB Atlas escala automáticamente

### Vertical
- Aumenta los recursos (CPU, RAM) de cada instancia
- Mejora para aplicaciones con alta demanda de cómputo

## Checklist de Despliegue

- [ ] Crear cuenta en plataforma de despliegue (Render/Railway/AWS)
- [ ] Desplegar MongoDB en producción
- [ ] Desplegar Redis en producción
- [ ] Configurar variables de entorno
- [ ] Desplegar aplicación principal
- [ ] Configurar dominio personal
- [ ] Configurar SSL/HTTPS
- [ ] Configurar backups automáticos
- [ ] Configurar monitoreo y alertas
- [ ] Probar registro de pacientes
- [ ] Probar verificación de email
- [ ] Probar login y sesiones
- [ ] Probar todas las funcionalidades principales

## Troubleshooting

### Error de conexión a MongoDB
- Verifica que la URI de MongoDB sea correcta
- Verifica que las credenciales sean válidas
- Verifica que la IP de la aplicación esté whitelisted

### Error de conexión a Redis
- Verifica que el host y puerto sean correctos
- Verifica que la contraseña sea correcta
- Verifica que Redis esté corriendo

### Error de envío de email
- Verifica las credenciales SMTP
- Para Gmail, usa "App Passwords" en lugar de la contraseña normal
- Verifica que el puerto sea correcto (587 para TLS, 465 para SSL)

### Error de sesión
- Verifica que Redis esté corriendo
- Verifica que la configuración de Redis sea correcta
- Verifica que el SECRET_KEY sea el mismo en todas las instancias

## Soporte

Para ayuda con el despliegue:
- Documentación de Render: [render.com/docs](https://render.com/docs)
- Documentación de Railway: [railway.app/docs](https://railway.app/docs)
- Documentación de MongoDB Atlas: [docs.atlas.mongodb.com](https://docs.atlas.mongodb.com)
