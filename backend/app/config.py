from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "DeepFake Detector"
    DEBUG: bool = False

    # Model paths
    IMAGE_MODEL_PATH: str = str(BASE_DIR / "models" / "weights" / "image_detector.h5")
    VIDEO_MODEL_PATH: str = str(BASE_DIR / "models" / "weights" / "video_detector.h5")
    DEEPFAKE_MODEL_PATH: str = str(BASE_DIR / "models" / "weights" / "deepfake_detector.h5")

    # Upload limits
    MAX_IMAGE_SIZE_MB: int = 10
    MAX_VIDEO_SIZE_MB: int = 100
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png", "image/webp"]
    ALLOWED_VIDEO_TYPES: list = ["video/mp4", "video/avi", "video/mov", "video/mkv"]

    # Detection thresholds
    AI_IMAGE_THRESHOLD: float = 0.5
    AI_VIDEO_THRESHOLD: float = 0.5
    DEEPFAKE_THRESHOLD: float = 0.5

    # Video frame sampling
    VIDEO_FRAME_SAMPLE_RATE: int = 10

    class Config:
        env_file = ".env"

settings = Settings()   