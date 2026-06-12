from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["Health"], summary="Check application health")
def health_check():
    """
    This endpoint can be used to check the health of the application.
    In the future, it can be expanded to check database and cache connections.
    """
    return {"status": "ok"}
