"""Quick diagnostic: check if the model actually differentiates real vs fake."""
import numpy as np
import tensorflow as tf
from pathlib import Path

MODEL_PATH = Path("models/weights/image_detector.h5")
DATASET_PATH = Path("datasets2/140k-real-and-fake-faces/real_vs_fake/real-vs-fake/valid")

print(f"Model exists: {MODEL_PATH.exists()}  ({MODEL_PATH})")
model = tf.keras.models.load_model(str(MODEL_PATH))

# Load a few real and fake images
for label in ["real", "fake"]:
    folder = DATASET_PATH / label
    images = list(folder.iterdir())[:5]
    scores = []
    for img_path in images:
        img = tf.keras.utils.load_img(img_path, target_size=(224, 224))
        arr = tf.keras.utils.img_to_array(img)
        arr = tf.keras.applications.efficientnet.preprocess_input(arr)
        arr = np.expand_dims(arr, axis=0)
        score = float(model.predict(arr, verbose=0)[0][0])
        scores.append(score)
    print(f"\n[{label.upper()}] raw scores: {[f'{s:.4f}' for s in scores]}")
    print(f"  mean={np.mean(scores):.4f}  min={np.min(scores):.4f}  max={np.max(scores):.4f}")
