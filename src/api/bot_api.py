"""
API REST para el bot conversacional.
Endpoints para chat, historial y configuración del bot.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from src.bot import get_bot, reset_bot

# Modelos Pydantic
class ChatRequest(BaseModel):
    """Solicitud de chat al bot"""
    message: str
    session_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Hola, quiero listar los pacientes",
                "session_id": "user-123"
            }
        }


class ChatResponse(BaseModel):
    """Respuesta del bot"""
    response: str
    intent: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "Aquí están los pacientes registrados...",
                "intent": "listar_pacientes",
                "session_id": "user-123",
                "timestamp": "2026-06-05T10:30:00"
            }
        }


class HistoryResponse(BaseModel):
    """Historial de conversación"""
    messages: List[Dict[str, Any]]
    total_messages: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {"role": "user", "content": "Hola", "timestamp": "2026-06-05T10:30:00"},
                    {"role": "assistant", "content": "¡Hola! ¿Cómo te puedo ayudar?", "timestamp": "2026-06-05T10:30:01"}
                ],
                "total_messages": 2
            }
        }


class BotInfoResponse(BaseModel):
    """Información del bot"""
    backend_type: str
    model_name: str
    history_size: int
    has_transformers: bool
    api_version: str = "1.0"
    
    class Config:
        json_schema_extra = {
            "example": {
                "backend_type": "SimpleFallbackBackend",
                "model_name": "simple",
                "history_size": 0,
                "has_transformers": False,
                "api_version": "1.0"
            }
        }


class ClearHistoryResponse(BaseModel):
    """Respuesta de limpieza de historial"""
    status: str
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Historial limpiado correctamente"
            }
        }


# Router de la API
router = APIRouter(
    prefix="/api/bot",
    tags=["Bot IA Conversacional"],
    responses={
        404: {"description": "Recurso no encontrado"},
        500: {"description": "Error del servidor"}
    }
)


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Enviar mensaje al bot",
    description="Envía un mensaje al bot conversacional y recibe una respuesta"
)
async def chat(request: ChatRequest):
    """
    Endpoint para chatear con el bot
    
    - **message**: Mensaje del usuario (requerido)
    - **session_id**: ID de sesión opcional para tracking
    """
    try:
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío")
        
        bot = get_bot()
        response = bot.chat(request.message)
        
        # Extraer intención del mensaje
        intent_info = bot.backend.extract_intent(request.message)
        intent = intent_info.get('intent', None)
        
        from datetime import datetime
        
        return ChatResponse(
            response=response,
            intent=intent,
            session_id=request.session_id,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando mensaje: {str(e)}")


@router.get(
    "/history",
    response_model=HistoryResponse,
    summary="Obtener historial de conversación",
    description="Retorna el historial de mensajes de la conversación actual"
)
async def get_history(limit: int = Query(10, ge=1, le=100)):
    """
    Obtiene el historial de la conversación
    
    - **limit**: Cantidad máxima de mensajes a retornar (1-100, default: 10)
    """
    try:
        bot = get_bot()
        history = bot.get_history()
        
        # Limitar resultados
        limited_history = history[-limit:] if limit else history
        
        return HistoryResponse(
            messages=limited_history,
            total_messages=len(history)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo historial: {str(e)}")


@router.delete(
    "/history",
    response_model=ClearHistoryResponse,
    summary="Limpiar historial",
    description="Elimina todo el historial de conversación"
)
async def clear_history():
    """Limpia el historial de conversación"""
    try:
        bot = get_bot()
        bot.clear_history()
        
        return ClearHistoryResponse(
            status="success",
            message="Historial de conversación limpiado correctamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error limpiando historial: {str(e)}")


@router.post(
    "/reset",
    response_model=ClearHistoryResponse,
    summary="Reiniciar bot",
    description="Reinicia la instancia del bot (limpia caché y estado)"
)
async def reset():
    """Reinicia la instancia del bot"""
    try:
        reset_bot()
        
        return ClearHistoryResponse(
            status="success",
            message="Bot reiniciado correctamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reiniciando bot: {str(e)}")


@router.get(
    "/info",
    response_model=BotInfoResponse,
    summary="Obtener información del bot",
    description="Retorna información sobre la configuración actual del bot"
)
async def get_info():
    """Obtiene información sobre el bot"""
    try:
        bot = get_bot()
        info = bot.get_system_info()
        
        return BotInfoResponse(
            backend_type=info['backend_type'],
            model_name=info['model_name'],
            history_size=info['history_size'],
            has_transformers=info['has_transformers']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo información: {str(e)}")


@router.get(
    "/help",
    summary="Obtener ayuda",
    description="Retorna instrucciones sobre cómo usar el bot"
)
async def get_help():
    """Retorna información de ayuda"""
    return {
        "api_version": "1.0",
        "base_url": "/api/bot",
        "endpoints": {
            "POST /chat": {
                "description": "Enviar mensaje al bot",
                "body": {"message": "Tu pregunta aquí"}
            },
            "GET /history": {
                "description": "Obtener historial de conversación",
                "params": {"limit": "Cantidad de mensajes (default: 10)"}
            },
            "DELETE /history": {
                "description": "Limpiar historial"
            },
            "POST /reset": {
                "description": "Reiniciar bot"
            },
            "GET /info": {
                "description": "Información del bot"
            },
            "GET /help": {
                "description": "Esta ayuda"
            }
        },
        "examples": {
            "chat": {
                "request": {"message": "Listar pacientes"},
                "response": {"response": "...", "intent": "listar_pacientes"}
            },
            "history": {
                "url": "/api/bot/history?limit=10",
                "response": {"messages": [...], "total_messages": 10}
            }
        },
        "documentation": "Ver /docs para documentación interactiva Swagger"
    }
