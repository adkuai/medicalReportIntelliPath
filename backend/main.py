from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.config import settings
from app.routes.analysis import router as analysis_router

app = FastAPI(
    title="Specialized Zero-Shot Medical Chart & Prescription Intelligence API",
    description="Backend microservice for zero-shot clinical document analysis powered by Qwen2.5-VL-7B-Instruct",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(analysis_router)

@app.get("/")
def read_root():
    return {
        "service": "Specialized Zero-Shot Medical Chart & Prescription Intelligence API",
        "status": "active",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "colab_configured_url": settings.COLAB_API_URL
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)

