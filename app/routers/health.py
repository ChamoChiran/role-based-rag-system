from fastapi import APIRouter
from datetime import datetime

router = APIRouter(
    prefix="/health",
    tags=["System"]
)

@router.get(
    "",
    summary="Health Check",
    description="Health Check",
)
def health_check():
    return {
        "status": "ok",
        "services": "role-based-rag-api",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }