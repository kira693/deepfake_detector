import time
import numpy as np
from fastapi import APIRouter, File, UploadFile, HTTPException
from PIL import Image
import io
from app.schemas import DeepfakeDetectionResponse, DetectionResult, DetectionType, Verdict
from app.services.deepfake_service import get_deepfake_detector
from app.config import settings
from app.utils.logger import setup_logger

router = APIRouter()
logger = setup_logger(__name__)


@router.post("/detect/deepfake", response_model=DeepfakeDetectionResponse)
async def detect_deepfake(file: UploadFile = File(...)):
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported type: {file.content_type}")

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.MAX_IMAGE_SIZE_MB:
        raise HTTPException(status_code=413, detail=f"File too large: {size_mb:.1f}MB")

    try:
        pil_image = Image.open(io.BytesIO(content)).convert("RGB")
        image_array = np.array(pil_image)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not decode image: {str(e)}")

    detector = get_deepfake_detector()
    start_time = time.time()

    try:
        prediction = detector.predict(image_array)
    except Exception as e:
        logger.error(f"Deepfake detection failed: {e}")
        raise HTTPException(status_code=500, detail="Detection model error.")

    elapsed_ms = (time.time() - start_time) * 1000
    df_prob = prediction["deepfake_probability"]
    confidence = prediction["confidence"]

    if prediction["faces_detected"] == 0:
        verdict = Verdict.INCONCLUSIVE
    elif confidence < 0.15:
        verdict = Verdict.INCONCLUSIVE
    elif prediction["is_deepfake"]:
        verdict = Verdict.DEEPFAKE
    else:
        verdict = Verdict.REAL

    result = DetectionResult(
        verdict=verdict,
        confidence=confidence,
        ai_probability=df_prob,
        detection_type=DetectionType.DEEPFAKE,
        processing_time_ms=elapsed_ms,
        details={
            "faces_detected": prediction["faces_detected"],
            "message": prediction.get("message", ""),
        },
    )

    return DeepfakeDetectionResponse(
        filename=file.filename,
        file_size_bytes=len(content),
        faces_detected=prediction["faces_detected"],
        result=result,
        face_results=prediction.get("face_results", []),
        message=f"Analyzed {prediction['faces_detected']} face(s) in {elapsed_ms:.0f}ms.",
    )