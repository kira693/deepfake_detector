from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import image, video, deepfake, health
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

app = FastAPI(
    title="DeepFake & AI Media Detector API",
    description="Detect AI-generated images, videos, and deepfakes",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(image.router, prefix="/api/v1", tags=["image"])
app.include_router(video.router, prefix="/api/v1", tags=["video"])
app.include_router(deepfake.router, prefix="/api/v1", tags=["deepfake"])

@app.on_event("startup")
async def startup_event():
    logger.info("Starting DeepFake Detector API...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down DeepFake Detector API...")