# Bot IA Avanzado - Guía Completa

## Descripción General

El nuevo Bot IA de plataforma-salud-chilecito es un asistente conversacional **funcional y real** que:

✅ Entiende **conversaciones naturales** (no solo comandos)  
✅ Mantiene **contexto conversacional**  
✅ Expone una **API REST** para integración  
✅ Soporta múltiples **backends de IA**  
✅ Es **replicable** en otros proyectos  

---

## 1. Instalación y Configuración

### 1.1 Instalación Básica (Sin dependencias adicionales)

```bash
# El bot ya funciona sin configuración extra
# Solo asegúrate de tener los requirements.txt instalados

pip install -r requirements.txt
```

### 1.2 Instalación Avanzada (Con Hugging Face)

Para usar modelos de lenguaje más avanzados:

```bash
# Instala transformers y torch
pip install transformers torch

# O para GPU:
pip install transformers torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 1.3 Instalación con OpenAI (Opcional)

```bash
pip install openai
```

---

## 2. Uso del Bot Conversacional

### 2.1 Uso Básico en Python

```python
from src.bot import get_bot

# Obtener instancia del bot
bot = get_bot()

# Chatear con el bot
respuesta = bot.chat("Hola, quiero listar los pacientes")
print(respuesta)

# Obtener historial
historial = bot.get_history()
for msg in historial:
    print(f"{msg['role']}: {msg['content']}")

# Limpiar historial
bot.clear_history()

# Obtener información del bot
info = bot.get_system_info()
print(f"Backend: {info['backend_type']}")
print(f"Modelo: {info['model_name']}")
```

### 2.2 Uso con Hugging Face

```python
from src.bot import ConversationalBot, HuggingFaceBackend

# Crear bot con Hugging Face
backend = HuggingFaceBackend(model_name="distilgpt2")
bot = ConversationalBot(backend=backend)

# Chatear
respuesta = bot.chat("¿Qué pacientes hay en el sistema?")
print(respuesta)
```

### 2.3 Backends Disponibles

#### SimpleFallbackBackend (por defecto)
- ✅ No requiere dependencias extra
- ✅ Respuestas rápidas
- ❌ Conversaciones menos naturales
- **Ideal para**: Producción sin dependencias

```python
from src.bot import SimpleFallbackBackend, ConversationalBot

backend = SimpleFallbackBackend()
bot = ConversationalBot(backend=backend)
```

#### HuggingFaceBackend
- ✅ Conversaciones naturales
- ✅ Modelos open-source
- ❌ Más lento, requiere transformers
- **Ideal para**: Desarrollo, pruebas

```python
from src.bot import HuggingFaceBackend, ConversationalBot

# Modelos recomendados:
# - "distilgpt2" (ligero, rápido)
# - "gpt2" (balanceado)
# - "tiiuae/falcon-7b-instruct" (muy bueno)
# - "meta-llama/Llama-2-7b-chat-hf" (excelente)

backend = HuggingFaceBackend(model_name="distilgpt2")
bot = ConversationalBot(backend=backend)
```

#### Backend Personalizado

```python
from src.bot import BaseAIBackend, ConversationalBot

class MiBackend(BaseAIBackend):
    def generate_response(self, prompt: str, context) -> str:
        # Tu lógica aquí
        return "Respuesta personalizada"
    
    def extract_intent(self, text: str) -> dict:
        # Tu lógica aquí
        return {"intent": "custom", "text": text}

backend = MiBackend()
bot = ConversationalBot(backend=backend)
```

---

## 3. API REST - Documentación Completa

### 3.1 Configuración en FastAPI

Para integrar el bot en tu aplicación FastAPI:

```python
from fastapi import FastAPI
from src.api import bot_router

app = FastAPI(
    title="Plataforma de Salud Chilecito",
    description="API con Bot IA Conversacional",
    version="1.0.0"
)

# Registrar router del bot
app.include_router(bot_router)

# Documentación interactiva en:
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

### 3.2 Endpoints de la API

#### 1️⃣ POST /api/bot/chat

**Envía un mensaje y recibe respuesta del bot**

```bash
curl -X POST "http://localhost:8000/api/bot/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hola, quiero listar los pacientes",
    "session_id": "user-123"
  }'
```

**Respuesta (200 OK):**
```json
{
  "response": "Puedo ayudarte con eso. Para listar pacientes, necesito conectar con la base de datos...",
  "intent": "listar_pacientes",
  "session_id": "user-123",
  "timestamp": "2026-06-05T10:30:45.123456"
}
```

**Parámetros:**
- `message` (string, requerido): Mensaje del usuario
- `session_id` (string, opcional): ID de sesión para tracking

**Códigos de respuesta:**
- `200`: Éxito
- `400`: Mensaje vacío o inválido
- `500`: Error del servidor

---

#### 2️⃣ GET /api/bot/history

**Obtiene el historial de conversación**

```bash
curl -X GET "http://localhost:8000/api/bot/history?limit=10"
```

**Respuesta (200 OK):**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hola",
      "timestamp": "2026-06-05T10:30:00"
    },
    {
      "role": "assistant",
      "content": "¡Hola! ¿Cómo te puedo ayudar?",
      "timestamp": "2026-06-05T10:30:01"
    }
  ],
  "total_messages": 2
}
```

**Parámetros:**
- `limit` (integer, default: 10): Cantidad máxima de mensajes (1-100)

---

#### 3️⃣ DELETE /api/bot/history

**Limpia el historial de conversación**

```bash
curl -X DELETE "http://localhost:8000/api/bot/history"
```

**Respuesta (200 OK):**
```json
{
  "status": "success",
  "message": "Historial de conversación limpiado correctamente"
}
```

---

#### 4️⃣ POST /api/bot/reset

**Reinicia la instancia del bot**

```bash
curl -X POST "http://localhost:8000/api/bot/reset"
```

**Respuesta (200 OK):**
```json
{
  "status": "success",
  "message": "Bot reiniciado correctamente"
}
```

---

#### 5️⃣ GET /api/bot/info

**Obtiene información del bot**

```bash
curl -X GET "http://localhost:8000/api/bot/info"
```

**Respuesta (200 OK):**
```json
{
  "backend_type": "SimpleFallbackBackend",
  "model_name": "simple",
  "history_size": 5,
  "has_transformers": false,
  "api_version": "1.0"
}
```

---

#### 6️⃣ GET /api/bot/help

**Obtiene información de ayuda sobre la API**

```bash
curl -X GET "http://localhost:8000/api/bot/help"
```

**Respuesta (200 OK):**
```json
{
  "api_version": "1.0",
  "base_url": "/api/bot",
  "endpoints": {...},
  "documentation": "Ver /docs para documentación interactiva"
}
```

---

## 4. Integración en Aplicaciones Web

### 4.1 JavaScript/TypeScript - Cliente Web

```typescript
// bot-client.ts
class BotClient {
  private baseUrl = '/api/bot';
  
  async sendMessage(message: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        message,
        session_id: this.getSessionId()
      })
    });
    return response.json();
  }
  
  async getHistory(limit = 10): Promise<any> {
    const response = await fetch(
      `${this.baseUrl}/history?limit=${limit}`
    );
    return response.json();
  }
  
  async clearHistory(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/history`, {
      method: 'DELETE'
    });
    return response.json();
  }
  
  private getSessionId(): string {
    let id = localStorage.getItem('bot_session_id');
    if (!id) {
      id = `session-${Date.now()}`;
      localStorage.setItem('bot_session_id', id);
    }
    return id;
  }
}

// Uso
const bot = new BotClient();

async function chat() {
  const message = document.getElementById('input').value;
  const response = await bot.sendMessage(message);
  
  console.log('Bot:', response.response);
  console.log('Intent:', response.intent);
}
```

### 4.2 React Component

```jsx
// BotChat.jsx
import { useState, useEffect } from 'react';

export default function BotChat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  
  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    setLoading(true);
    
    try {
      const response = await fetch('/api/bot/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
      });
      
      const data = await response.json();
      
      setMessages(prev => [
        ...prev,
        { role: 'user', content: input },
        { role: 'assistant', content: data.response }
      ]);
      
      setInput('');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="bot-chat">
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            {msg.content}
          </div>
        ))}
      </div>
      
      <form onSubmit={sendMessage}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Escribe tu mensaje..."
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Enviando...' : 'Enviar'}
        </button>
      </form>
    </div>
  );
}
```

### 4.3 Python - Cliente API

```python
import requests
import json

class BotAPIClient:
    def __init__(self, base_url='http://localhost:8000'):
        self.base_url = base_url
        self.session = requests.Session()
    
    def chat(self, message: str, session_id: str = None) -> dict:
        """Envía un mensaje al bot"""
        response = self.session.post(
            f'{self.base_url}/api/bot/chat',
            json={
                'message': message,
                'session_id': session_id
            }
        )
        return response.json()
    
    def get_history(self, limit: int = 10) -> dict:
        """Obtiene el historial"""
        response = self.session.get(
            f'{self.base_url}/api/bot/history',
            params={'limit': limit}
        )
        return response.json()
    
    def clear_history(self) -> dict:
        """Limpia el historial"""
        response = self.session.delete(
            f'{self.base_url}/api/bot/history'
        )
        return response.json()
    
    def get_info(self) -> dict:
        """Obtiene información del bot"""
        response = self.session.get(
            f'{self.base_url}/api/bot/info'
        )
        return response.json()

# Uso
client = BotAPIClient()

# Enviar mensaje
response = client.chat("Listar pacientes")
print(response['response'])

# Ver historial
history = client.get_history(limit=5)
for msg in history['messages']:
    print(f"{msg['role']}: {msg['content']}")
```

---

## 5. Despliegue y Replicación

### 5.1 Desplegar en tu proyecto

1. **Copiar archivos:**
```bash
cp -r src/bot/ tu-proyecto/src/
cp -r src/api/bot_api.py tu-proyecto/src/api/
```

2. **Agregar a requirements.txt:**
```txt
fastapi==0.104.0
uvicorn==0.24.0
pydantic==2.5.0
```

3. **Para modelos de IA (opcional):**
```txt
transformers==4.35.0
torch==2.1.0
```

4. **Registrar en tu FastAPI app:**
```python
from fastapi import FastAPI
from src.api import bot_router

app = FastAPI()
app.include_router(bot_router)
```

### 5.2 Variables de Entorno

Crear `.env`:
```env
# Bot Configuration
BOT_USE_HUGGINGFACE=false
BOT_MODEL=distilgpt2
BOT_MAX_HISTORY=10

# FastAPI
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
```

### 5.3 Docker (Opcional)

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 6. Ejemplos de Conversación

### Ejemplo 1: Consulta Simple
```
Usuario: Hola, ¿qué puedes hacer?
Bot: Puedo ayudarte con listar pacientes, médicos, centros, turnos...

Usuario: Listar pacientes
Bot: Para listar pacientes, necesito conectarme a la base de datos.
```

### Ejemplo 2: Búsqueda
```
Usuario: Busca pacientes en Chilecito
Bot: Buscando pacientes en el distrito de Chilecito...

Usuario: ¿Cuántos encontraste?
Bot: Encontré X pacientes registrados.
```

### Ejemplo 3: Creación
```
Usuario: Quiero crear un nuevo paciente
Bot: Claro, proporciona: nombre, DNI, teléfono, distrito y obra social

Usuario: Juan García, DNI 12345678, teléfono 3825-111222, Chilecito, APOS
Bot: Paciente creado exitosamente con ID: 1
```

---

## 7. Troubleshooting

### Error: "Transformers no instalado"
```bash
pip install transformers torch
```

### Error: "Modelo no encontrado"
```python
# Asegúrate de usar un modelo válido
backend = HuggingFaceBackend(model_name="distilgpt2")
```

### El bot responde muy lentamente
```python
# Usa un modelo más ligero
backend = HuggingFaceBackend(model_name="distilgpt2")
# O el backend simple (default)
bot = ConversationalBot()
```

### Historial muy grande
```python
# Limpiar historial
bot.clear_history()

# O limitar en GET /history
curl "http://localhost:8000/api/bot/history?limit=10"
```

---

## 8. Próximos Pasos

✅ Integrar con base de datos para respuestas dinámicas  
✅ Agregar autenticación y rate limiting  
✅ Implementar logging y monitoreo  
✅ Conectar con modelos más avanzados  
✅ Agregar soporte multi-idioma  

---

## 📚 Referencias

- [FastAPI](https://fastapi.tiangolo.com/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)
- [Pydantic](https://docs.pydantic.dev/)

---

**¿Preguntas?** Consulta la documentación del proyecto o abre un issue en GitHub.
