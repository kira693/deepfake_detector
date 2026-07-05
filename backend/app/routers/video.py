import time
import tempfile
import os
from fastapi import APIRouter, File, UploadFile, HTTPException
from app.schemas import VideoDetectionResponse, DetectionResult, DetectionType, Verdict
from app.services.video_service import get_video_detector
from app.config import settings
from app.utils.logger import setup_logger

router = APIRouter()
logger = setup_logger(__name__)


@router.post("/detect/video", response_model=VideoDetectionResponse)
async def detect_ai_video(file: UploadFile = File(...)):
    if file.content_type not in settings.ALLOWED_VIDEO_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported video type: {file.content_type}")

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.MAX_VIDEO_SIZE_MB:
        raise HTTPException(status_code=413, detail=f"File too large: {size_mb:.1f}MB")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        detector = get_video_detector()
        start_time = time.time()
        prediction = detector.predict(tmp_path)
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
            detection_type=DetectionType.AI_VIDEO,
            processing_time_ms=elapsed_ms,
            details={
                "temporal_variance": prediction.get("temporal_variance", 0),
                "frames_analyzed": prediction["frames_analyzed"],
            },
        )

        return VideoDetectionResponse(
            filename=file.filename,
            file_size_bytes=len(content),
            total_frames_analyzed=prediction["frames_analyzed"],
            result=result,
            frame_results=prediction.get("frame_results", []),
            message=f"Analyzed {prediction['frames_analyzed']} frames in {elapsed_ms:.0f}ms.",
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Video detection failed: {e}")
        raise HTTPException(status_code=500, detail="Detection model error.")
    finally:
        os.unlink(tmp_path)
        