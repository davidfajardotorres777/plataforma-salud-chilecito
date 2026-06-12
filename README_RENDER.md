# Despliegue Rápido en Render

## Pasos para desplegar en 5 minutos

### 1. Crear cuenta en Render
- Ve a https://render.com
- Regístrate con tu cuenta de GitHub
- Es gratis

### 2. Conectar tu repositorio
- En Render, haz clic en "New +"
- Selecciona "Web Service"
- Conecta tu repositorio `plataforma-salud-chilecito`

### 3. Configurar el servicio
Render detectará automáticamente el archivo `render.yaml` y configurará:
- **Aplicación web**: Python con MongoDB y Redis
- **MongoDB**: Base de datos gratuita
- **Redis**: Caché gratuito

### 4. Configurar variables de email (opcional)
En las variables de entorno del servicio web, configura:
- `SMTP_USERNAME`: tu email de Gmail
- `SMTP_PASSWORD`: tu "App Password" de Gmail (crea una en https://myaccount.google.com/apppasswords)
- `FROM_EMAIL`: noreply@saludchilecito.com

### 5. Desplegar
- Haz clic en "Create Web Service"
- Render construirá y desplegará automáticamente
- En 3-5 minutos estará en línea

### 6. Acceder a tu plataforma
Render te dará una URL como: `https://salud-chilecito.onrender.com`

## URLs importantes
- **Registro**: `https://salud-chilecito.onrender.com/registro`
- **Login**: `https://salud-chilecito.onrender.com/`
- **API**: `https://salud-chilecito.onrender.com/api/auth/registro`

## Usuario admin inicial
Email: `admin@saludchilecito.com`
Contraseña: `admin123`

## Notas
- El plan gratuito de Render incluye:
  - 750 horas/mes de computación
  - MongoDB gratuito (512MB)
  - Redis gratuito (25MB)
- SSL/HTTPS automático
- Dominio gratuito de Render
- Para dominio personal, actualízalo en los settings de Render
