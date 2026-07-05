from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class DetectionType(str, Enum):
    AI_IMAGE = "ai_image"
    AI_VIDEO = "ai_video"
    DEEPFAKE = "deepfake"


class Verdict(str, Enum):
    REAL = "REAL"
    AI_GENERATED = "AI_GENERATED"
    DEEPFAKE = "DEEPFAKE"
    INCONCLUSIVE = "INCONCLUSIVE"


class DetectionResult(BaseModel):
    verdict: Verdict
    confidence: float = Field(..., ge=0.0, le=1.0)
    ai_probability: float = Field(..., ge=0.0, le=1.0)
    detection_type: DetectionType
    processing_time_ms: float
    details: dict = {}


class ImageDetectionResponse(BaseModel):
    filename: str
    file_size_bytes: int
    result: DetectionResult
    message: str


class VideoDetectionResponse(BaseModel):
    filename: str
    file_size_bytes: int
    total_frames_analyzed: int
    result: DetectionResult
    frame_results: list[dict] = []
    message: str


class DeepfakeDetectionResponse(BaseModel):
    filename: str
    file_size_bytes: int
    faces_detected: int
    result: DetectionResult
    face_results: list[dict] = []
    message: str


class HealthResponse(BaseModel):
    status: str
    models_loaded: dict
    version: str