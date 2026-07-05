import numpy as np
import tensorflow as tf
from pathlib import Path
from app.utils.logger import setup_logger
from app.config import settings

logger = setup_logger(__name__)


class AIImageDetector:
    def __init__(self):
        self.model = None
        self.input_size = (224, 224)
        self._load_model()

    def _load_model(self):
        model_path = Path(settings.IMAGE_MODEL_PATH)
        if model_path.exists():
            logger.info(f"Loading image model from {model_path}")
            self.model = tf.keras.models.load_model(str(model_path))
        else:
            logger.warning("No trained weights found. Using demo model.")
            self.model = self._build_demo_model()

    def _build_demo_model(self):
        base = tf.keras.applications.EfficientNetB0(
            include_top=False,
            weights="imagenet",
            input_shape=(*self.input_size, 3),
        )
        base.trainable = False
        model = tf.keras.Sequential([
            base,
            tf.keras.layers.GlobalAveragePooling2D(),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dense(256, activation="relu"),
            tf.keras.layers.Dropout(0.4),
            tf.keras.layers.Dense(64, activation="relu"),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(1, activation="sigmoid"),
        ])
        model.build(input_shape=(None, *self.input_size, 3))
        return model

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        img = tf.image.resize(image, self.input_size)
        img = tf.keras.applications.efficientnet.preprocess_input(img)
        return np.expand_dims(img.numpy(), axis=0)

    def predict(self, image: np.ndarray) -> dict:
        processed = self.preprocess(image)
        # raw_score is P(real) because classes are alphabetical: 0=fake, 1=real
        raw_score = float(self.model.predict(processed, verbose=0)[0][0])
        ai_probability = 1.0 - raw_score  # invert: high raw_score = real
        confidence = abs(raw_score - 0.5) * 2.0
        return {
            "ai_probability": ai_probability,
            "confidence": confidence,
            "is_ai_generated": ai_probability >= settings.AI_IMAGE_THRESHOLD,
            "raw_score": raw_score,
        }


_detector: AIImageDetector | None = None

def get_image_detector() -> AIImageDetector:
    global _detector
    if _detector is None:
        _detector = AIImageDetector()
    return _detector