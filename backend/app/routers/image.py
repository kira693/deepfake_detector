import time
import numpy as np
from fastapi import APIRouter, File, UploadFile, HTTPException
from PIL import Image
import io
from app.schemas import ImageDetectionResponse, DetectionResult, DetectionType, Verdict
from app.services.image_service import get_image_detector
from app.config import settings
from app.utils.logger import setup_logger

router = APIRouter()
logger = setup_logger(__name__)


@router.post("/detect/image", response_model=ImageDetectionResponse)
async def detect_ai_image(file: UploadFile = File(...)):
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.MAX_IMAGE_SIZE_MB:
        raise HTTPException(status_code=413, detail=f"File too large: {size_mb:.1f}MB")

    try:
        pil_image = Image.open(io.BytesIO(content)).convert("RGB")
        image_array = np.array(pil_image)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not decode image: {str(e)}")

    detector = get_image_detector()
    start_time = time.time()

    try:
        prediction = detector.predict(image_array)
    except Exception as e:
        logger.error(f"Detection failed: {e}")
        raise HTTPException(status_code=500, detail="Detection model error.")

    elapsed_ms = (time.time() - start_time) * 1000

    if prediction["confidence"] < 0.15:
        verdict = Verdict.INCONCLUSIVE
    elif prediction["is_ai_generated"]:
        verdict = Verdict.AI_GENERATED
    else:
        verdict = Verdict.REAL

    result = DetectionResult(
        verdict=verdict,
        confidence=prediction["confidence"],
        ai_probability=prediction["ai_probability"],
        detection_type=DetectionType.AI_IMAGE,
        processing_time_ms=elapsed_ms,
        details={
            "image_size": list(pil_image.size),
            "raw_score": prediction["raw_score"],
        },
    )

    return ImageDetectionResponse(
        filename=file.filename,
        file_size_bytes=len(content),
        result=result,
        message=f"Image analyzed in {elapsed_ms:.0f}ms.",
    )