import numpy as np
import cv2
from app.utils.logger import setup_logger
from app.config import settings
from app.services.image_service import get_image_detector

logger = setup_logger(__name__)


class AIVideoDetector:
    def __init__(self):
        self.image_detector = get_image_detector()
        self.frame_sample_rate = settings.VIDEO_FRAME_SAMPLE_RATE

    def extract_frames(self, video_path: str) -> list:
        cap = cv2.VideoCapture(video_path)
        frames = []
        frame_idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if frame_idx % self.frame_sample_rate == 0:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append((frame_idx, frame_rgb))
            frame_idx += 1
        cap.release()
        logger.info(f"Extracted {len(frames)} frames from {frame_idx} total")
        return frames

    def analyze_frames(self, frames: list) -> list:
        results = []
        for frame_idx, frame in frames:
            result = self.image_detector.predict(frame)
            results.append({
                "frame_index": frame_idx,
                "ai_probability": result["ai_probability"],
                "confidence": result["confidence"],
            })
        return results

    def aggregate_results(self, frame_results: list) -> dict:
        if not frame_results:
            return {
                "ai_probability": 0.5,
                "confidence": 0.0,
                "is_ai_generated": False,
                "frames_analyzed": 0,
            }
        probs = np.array([r["ai_probability"] for r in frame_results])
        confs = np.array([r["confidence"] for r in frame_results])
        weights = confs + 1e-8
        weighted_prob = float(np.average(probs, weights=weights))
        variance = float(np.var(probs))
        consistency_bonus = max(0.0, 0.2 - variance)
        final_confidence = min(1.0, abs(weighted_prob - 0.5) * 2.0 + consistency_bonus)
        return {
            "ai_probability": weighted_prob,
            "confidence": final_confidence,
            "is_ai_generated": weighted_prob >= settings.AI_VIDEO_THRESHOLD,
            "temporal_variance": variance,
            "frames_analyzed": len(frame_results),
        }

    def predict(self, video_path: str) -> dict:
        frames = self.extract_frames(video_path)
        if not frames:
            raise ValueError("Could not extract any frames from the video.")
        frame_results = self.analyze_frames(frames)
        aggregated = self.aggregate_results(frame_results)
        aggregated["frame_results"] = frame_results
        return aggregated


_detector: AIVideoDetector | None = None

def get_video_detector() -> AIVideoDetector:
    global _detector
    if _detector is None:
        _detector = AIVideoDetector()
    return _detector