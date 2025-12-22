from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get(
    "",
    summary="Health Check",
    description="Basic health check endpoint."
)
def health_check():
    """
    Basic health check endpoint.
    :return:
    A JSON response indicating the services is running.
    """
    return {
        "status": "ok",
        "message": "Rag Based Assistant is running.",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }