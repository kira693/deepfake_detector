import tensorflow as tf
from pathlib import Path

# Paths
DATASET_PATH = Path("datasets2/140k-real-and-fake-faces/real_vs_fake/real-vs-fake")
MODEL_SAVE_PATH = Path("models/weights/image_detector.h5")
MODEL_SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)

INPUT_SIZE = (224, 224)
BATCH_SIZE = 32

# ── Phase 1 config (frozen base) ──
PHASE1_EPOCHS = 10
PHASE1_LR = 1e-3

# ── Phase 2 config (fine-tune top layers) ──
PHASE2_EPOCHS = 10
PHASE2_LR = 1e-5   # much lower LR to avoid destroying pretrained weights
FINE_TUNE_FROM = 200  # unfreeze layers from this index onward (~top 30% of EfficientNetB0)

# ─────────────────────────────────────────────
# 1. Load dataset
# ─────────────────────────────────────────────
print("Loading dataset...")
train_ds = tf.keras.utils.image_dataset_from_directory(
    DATASET_PATH / "train",
    image_size=INPUT_SIZE,
    batch_size=BATCH_SIZE,
    label_mode='binary',
    shuffle=True,
)

val_ds = tf.keras.utils.image_dataset_from_directory(
    DATASET_PATH / "valid",
    image_size=INPUT_SIZE,
    batch_size=BATCH_SIZE,
    label_mode='binary',
    shuffle=False,
)

print(f"Class names: {train_ds.class_names}")

def preprocess(images, labels):
    images = tf.keras.applications.efficientnet.preprocess_input(images)
    return images, labels

train_ds = train_ds.map(preprocess).prefetch(tf.data.AUTOTUNE)
val_ds = val_ds.map(preprocess).prefetch(tf.data.AUTOTUNE)

# ─────────────────────────────────────────────
# 2. Data augmentation (applied only during training)
# ─────────────────────────────────────────────
data_augmentation = tf.keras.Sequential([
    tf.keras.layers.RandomFlip("horizontal"),
    tf.keras.layers.RandomRotation(0.1),
    tf.keras.layers.RandomZoom(0.1),
    tf.keras.layers.RandomBrightness(0.2),
    tf.keras.layers.RandomContrast(0.2),
], name="data_augmentation")

# ─────────────────────────────────────────────
# 3. Build model
# ─────────────────────────────────────────────
print("Building model...")
base = tf.keras.applications.EfficientNetB0(
    include_top=False,
    weights="imagenet",
    input_shape=(*INPUT_SIZE, 3),
)
base.trainable = False  # freeze for Phase 1

model = tf.keras.Sequential([
    data_augmentation,
    base,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Dense(256, activation="relu"),
    tf.keras.layers.Dropout(0.4),
    tf.keras.layers.Dense(64, activation="relu"),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(1, activation="sigmoid"),
])

# ─────────────────────────────────────────────
# 4. Phase 1 — Train the head (base frozen)
# ─────────────────────────────────────────────
print("\n" + "="*50)
print("PHASE 1: Training head layers (base frozen)")
print("="*50)

model.compile(
    optimizer=tf.keras.optimizers.Adam(PHASE1_LR),
    loss="binary_crossentropy",
    metrics=["accuracy"],
)

model.summary()

phase1_callbacks = [
    tf.keras.callbacks.EarlyStopping(patience=3, restore_best_weights=True),
    tf.keras.callbacks.ReduceLROnPlateau(patience=2, factor=0.5),
]

history1 = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=PHASE1_EPOCHS,
    callbacks=phase1_callbacks,
)

phase1_val_loss, phase1_val_acc = model.evaluate(val_ds)
print(f"\nPhase 1 validation accuracy: {phase1_val_acc:.2%}")

# ─────────────────────────────────────────────
# 5. Phase 2 — Fine-tune top layers of the base
# ─────────────────────────────────────────────
print("\n" + "="*50)
print("PHASE 2: Fine-tuning top layers of EfficientNetB0")
print("="*50)

# Unfreeze the base from layer FINE_TUNE_FROM onward
base.trainable = True
for layer in base.layers[:FINE_TUNE_FROM]:
    layer.trainable = False

trainable_layers = sum(1 for l in base.layers if l.trainable)
frozen_layers = sum(1 for l in base.layers if not l.trainable)
print(f"  Base layers: {len(base.layers)} total, {trainable_layers} trainable, {frozen_layers} frozen")

# Re-compile with a much lower learning rate
model.compile(
    optimizer=tf.keras.optimizers.Adam(PHASE2_LR),
    loss="binary_crossentropy",
    metrics=["accuracy"],
)

phase2_callbacks = [
    tf.keras.callbacks.EarlyStopping(patience=4, restore_best_weights=True),
    tf.keras.callbacks.ReduceLROnPlateau(patience=2, factor=0.5, min_lr=1e-7),
]

history2 = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=PHASE2_EPOCHS,
    callbacks=phase2_callbacks,
)

# ─────────────────────────────────────────────
# 6. Save & evaluate
# ─────────────────────────────────────────────
print(f"\nSaving model to {MODEL_SAVE_PATH}...")
model.save(str(MODEL_SAVE_PATH))
print("Done! Model saved.")

val_loss, val_acc = model.evaluate(val_ds)
print(f"\n{'='*50}")
print(f"FINAL validation accuracy: {val_acc:.2%}")
print(f"Phase 1 was: {phase1_val_acc:.2%}")
print(f"Improvement: {(val_acc - phase1_val_acc):.2%}")
print(f"{'='*50}")