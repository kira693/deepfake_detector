import numpy as np
import tensorflow as tf
import cv2
from pathlib import Path
from app.utils.logger import setup_logger
from app.config import settings

logger = setup_logger(__name__)


class DeepfakeDetector:
    def __init__(self):
        self.face_detector = None
        self.deepfake_model = None
        self.input_size = (299, 299)
        self._load_models()

    def _load_models(self):
        logger.warning("Using Haar cascade face detector.")
        self.face_detector = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        deepfake_model_path = Path(settings.DEEPFAKE_MODEL_PATH)
        if deepfake_model_path.exists():
            self.deepfake_model = tf.keras.models.load_model(str(deepfake_model_path))
            logger.info("Deepfake classifier loaded")
        else:
            logger.warning("No trained weights found. Using demo Xception model.")
            self.deepfake_model = self._build_demo_model()

    def _build_demo_model(self):
        base = tf.keras.applications.Xception(
            include_top=False,
            weights="imagenet",
            input_shape=(*self.input_size, 3),
        )
        base.trainable = False
        model = tf.keras.Sequential([
            base,
            tf.keras.layers.GlobalAveragePooling2D(),
            tf.keras.layers.Dense(512, activation="relu"),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(1, activation="sigmoid"),
        ])
        model.build(input_shape=(None, *self.input_size, 3))
        return model

    def detect_faces(self, image: np.ndarray) -> list:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        faces = self.face_detector.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
        )
        return [tuple(f) for f in faces] if len(faces) > 0 else []

    def classify_face(self, face_crop: np.ndarray) -> dict:
        img = tf.image.resize(face_crop, self.input_size)
        img = tf.keras.applications.xception.preprocess_input(img.numpy())
        img = np.expand_dims(img, axis=0)
        score = float(self.deepfake_model.predict(img, verbose=0)[0][0])
        return {
            "deepfake_probability": score,
            "confidence": abs(score - 0.5) * 2.0,
            "is_deepfake": score >= settings.DEEPFAKE_THRESHOLD,
        }

    def predict(self, image: np.ndarray) -> dict:
        faces = self.detect_faces(image)

        if not faces:
            return {
                "faces_detected": 0,
                "deepfake_probability": 0.0,
                "confidence": 0.0,
                "is_deepfake": False,
                "face_results": [],
                "message": "No faces detected in the image.",
            }

        face_results = []
        for i, (x, y, w, h) in enumerate(faces):
            pad_x = int(w * 0.2)
            pad_y = int(h * 0.2)
            x1 = max(0, x - pad_x)
            y1 = max(0, y - pad_y)
            x2 = min(image.shape[1], x + w + pad_x)
            y2 = min(image.shape[0], y + h + pad_y)
            face_crop = image[y1:y2, x1:x2]
            if face_crop.size == 0:
                continue
            result = self.classify_face(face_crop)
            face_results.append({
                "face_index": i,
                "bounding_box": {"x": int(x), "y": int(y), "w": int(w), "h": int(h)},
                **result,
            })

        if not face_results:
            return {
                "faces_detected": len(faces),
                "deepfake_probability": 0.0,
                "confidence": 0.0,
                "is_deepfake": False,
                "face_results": [],
            }

        probs = [r["deepfake_probability"] for r in face_results]
        max_prob = max(probs)
        avg_conf = np.mean([r["confidence"] for r in face_results])

        return {
            "faces_detected": len(face_results),
            "deepfake_probability": max_prob,
            "confidence": float(avg_conf),
            "is_deepfake": max_prob >= settings.DEEPFAKE_THRESHOLD,
            "face_results": face_results,
        }


_detector: DeepfakeDetector | None = None

def get_deepfake_detector() -> DeepfakeDetector:
    global _detector
    if _detector is None:
        _detector = DeepfakeDetector()
    return _detector