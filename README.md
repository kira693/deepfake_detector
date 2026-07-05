# DeepFake Detector

A mobile app + REST API that detects whether an image is **real or AI-generated / deepfaked**, using a pretrained EfficientNetB0 model fine-tuned on 140k real-vs-fake faces.

---

## Demo

| Home Screen | Result — Real | Result — AI Generated |
|:-----------:|:-------------:|:---------------------:|
| Pick detection type and upload from gallery | Green-verdict with confidence bar | Orange- verdict with AI probability |

---

## Architecture

```
deepfake-detector/
├── backend/           # FastAPI REST API (Python + TensorFlow)
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── schemas.py
│   │   ├── routers/   # image.py, deepfake.py, video.py, health.py
│   │   ├── services/  # image_service.py, deepfake_service.py, video_service.py
│   │   └── utils/
│   ├── Dockerfile
│   └── requirements.txt
├── mobile/            # React Native (Expo) app
│   ├── app/           # Expo Router pages
│   └── src/
│       ├── screens/   # HomeScreen, ResultScreen
│       └── services/  # api.ts — axios calls to backend
├── models/
│   └── weights/       # Place your .h5 model files here
└── docker-compose.yml
```

---

##  Features

-  **AI Image Detection** — detect GAN/diffusion-generated images  
-  **Deepfake Detection** — face-crop + classify with Haar cascade + Xception  
-  **AI Video Detection** — frame-sampling pipeline (optional)  
-  Confidence score + AI probability bar on result screen  
-  FastAPI backend with CORS enabled for mobile  

---

##  Quick Start

### Option A — Docker (recommended)

**Prerequisites:** Docker Desktop installed and running.

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/deepfake-detector.git
cd deepfake-detector

# 2. Put your trained model in the weights directory
#    (see "Model Weights" section below)
cp /path/to/image_detector.h5 models/weights/

# 3. Build & run
docker compose up --build
```

The API will be available at **http://localhost:8000**  
Interactive docs at **http://localhost:8000/docs**

---

### Option B — Run Locally (without Docker)

#### Backend

```bash
# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Place your model weights in models/weights/image_detector.h5

# Start the API server
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Mobile App

```bash
cd mobile
npm install
npx expo start
```

Then scan the QR code with the **Expo Go** app on your phone.

> **Important:** Update `BASE_URL` in `mobile/src/services/api.ts` to your machine's local IP address:
> ```ts
> const BASE_URL = 'http://YOUR_LOCAL_IP:8000/api/v1';
> ```
> Find your IP with `ipconfig` (Windows) or `ifconfig` (macOS/Linux). Your phone must be on the **same Wi-Fi network**.

---

##  Model Weights

The trained `.h5` model files are **not included** in this repository (they are large binary files). You have two options:

### Option 1 — Use your own trained model
Train an EfficientNetB0 binary classifier on a real-vs-fake dataset (e.g. [140k Real and Fake Faces](https://www.kaggle.com/datasets/xhlulu/140k-real-and-fake-faces)) and save it as:
```
models/weights/image_detector.h5
```

### Option 2 — Use the demo model (no training needed)
If no `.h5` file is found, the backend automatically falls back to a **pretrained ImageNet EfficientNetB0** with a randomly-initialised classification head. Results will be random but the API will still function end-to-end for testing.

---

##  API Reference

Base URL: `http://localhost:8000/api/v1`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check + model load status |
| `POST` | `/detect/image` | Detect AI-generated image |
| `POST` | `/detect/deepfake` | Detect deepfake faces in image |
| `POST` | `/detect/video` | Detect AI-generated video |

### Example — Detect Image

```bash
curl -X POST http://localhost:8000/api/v1/detect/image \
  -F "file=@your_image.jpg"
```

**Response:**
```json
{
  "filename": "your_image.jpg",
  "file_size_bytes": 204800,
  "result": {
    "verdict": "REAL",
    "confidence": 0.94,
    "ai_probability": 0.03,
    "detection_type": "ai_image",
    "processing_time_ms": 1200.0,
    "details": { "image_size": [512, 512], "raw_score": 0.97 }
  },
  "message": "Image analyzed in 1200ms."
}
```

**Verdicts:**
- `REAL` — image appears to be a genuine photograph  
- `AI_GENERATED` — image appears to be AI/GAN generated  
- `DEEPFAKE` — face in image appears to be deepfaked  
- `INCONCLUSIVE` — model confidence too low to decide  

---

##  Tech Stack

| Layer | Technology |
|-------|-----------|
| Mobile | React Native + Expo Router |
| API | FastAPI + Uvicorn |
| ML | TensorFlow / Keras — EfficientNetB0 |
| Face detection | OpenCV Haar Cascade |
| Containerisation | Docker + Docker Compose |

---

##  Project Configuration

| File | Purpose |
|------|---------|
| `backend/app/config.py` | Model paths, thresholds, size limits |
| `docker-compose.yml` | Container orchestration |
| `mobile/src/services/api.ts` | Backend URL for mobile app |

To change detection thresholds, edit `backend/app/config.py`:
```python
AI_IMAGE_THRESHOLD: float = 0.5   # above this → AI_GENERATED
DEEPFAKE_THRESHOLD: float = 0.5   # above this → DEEPFAKE
```

---

## License

MIT — see [LICENSE](LICENSE) for details.
