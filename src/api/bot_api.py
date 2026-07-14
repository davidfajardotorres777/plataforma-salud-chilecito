from fastapi import APIRouter

router = APIRouter()

@router.get('/bot/health')
def bot_health():
    return {"status": "ok"}
