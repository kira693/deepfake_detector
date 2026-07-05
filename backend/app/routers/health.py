from fastapi import APIRouter
from app.schemas import HealthResponse
from pathlib import Path
from app.config import settings

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    models_loaded = {
        "image_detector": Path(settings.IMAGE_MODEL_PATH).exists(),
        "video_detector": Path(settings.VIDEO_MODEL_PATH).exists(),
        "deepfake_detector": Path(settings.DEEPFAKE_MODEL_PATH).exists(),
    }
    return HealthResponse(
        status="ok",
        models_loaded=models_loaded,
        version="1.0.0",
    )