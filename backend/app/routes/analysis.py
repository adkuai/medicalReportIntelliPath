from fastapi import APIRouter, UploadFile, File, Form, Query, HTTPException, status
from typing import Optional
from app.schemas import ClinicalAnalysisResult, ColabStatusResponse
from app.services.pdf_processor import PDFProcessor
from app.services.colab_client import colab_client, MOCK_CLINICAL_ANALYSIS
from app.services.clinical_validator import ClinicalValidator

router = APIRouter(prefix="/api", tags=["Medical Intelligence"])

@router.get("/status", response_model=ColabStatusResponse)
async def check_colab_status(colab_url: Optional[str] = Query(None, description="Optional override Colab URL")):
    """
    Checks if the Google Colab T4 GPU instance is reachable via its public tunnel.
    """
    active_url = colab_url
    if active_url and ("your-colab-tunnel" in active_url or not active_url.startswith("http")):
        active_url = None
    result = await colab_client.check_health(override_url=active_url)
    return ColabStatusResponse(
        status=result.get("status", "offline"),
        colab_url=result.get("colab_url", ""),
        accessible=result.get("accessible", False),
        model_name=result.get("model_name", "Qwen/Qwen2.5-VL-7B-Instruct"),
        latency_ms=result.get("latency_ms"),
        message=result.get("message", "")
    )

@router.post("/analyze", response_model=ClinicalAnalysisResult)
async def analyze_medical_document(
    file: UploadFile = File(...),
    custom_colab_url: Optional[str] = Form(None)
):
    """
    Accepts high-resolution smartphone photographs of prescriptions or multi-page lab reports (PNG/JPG/PDF).
    Renders pages, calls Qwen2.5-VL-7B-Instruct on Colab, isolates out-of-range clinical bounds,
    and returns pristine structured clinical intelligence.
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    # Read uploaded bytes
    try:
        contents = await file.read()
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        # Process file into base64 images
        base64_images, mime_type = PDFProcessor.process_uploaded_bytes(contents, file.filename or "upload.jpg")

        # Sanitize custom_colab_url: ignore placeholder or invalid URLs
        active_url = custom_colab_url
        if active_url and ("your-colab-tunnel" in active_url or not active_url.startswith("http")):
            active_url = None

        # Send to Colab model (or graceful fallback)
        raw_result = await colab_client.send_to_colab(base64_images, custom_colab_url=active_url)

        # Validate bounds, highlight red grid anomalies, normalize timing matrix
        final_result = ClinicalValidator.validate_and_enhance(raw_result)
        
        # Attach file metadata
        final_result.metadata["filename"] = file.filename
        final_result.metadata["pages_processed"] = len(base64_images)
        final_result.metadata["mime_type"] = mime_type

        return final_result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing medical document: {str(e)}"
        )

@router.get("/sample", response_model=ClinicalAnalysisResult)
async def get_sample_clinical_data():
    """
    Returns verified clinical demonstration dataset (handwritten prescription + out-of-range lab markers)
    for instant UI testing and verification.
    """
    return ClinicalValidator.validate_and_enhance(MOCK_CLINICAL_ANALYSIS)

