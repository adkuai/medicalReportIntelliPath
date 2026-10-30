import httpx
import time
import json
import logging
from typing import Dict, Any, List
from app.config import settings

logger = logging.getLogger("colab_client")

MOCK_CLINICAL_ANALYSIS: Dict[str, Any] = {
    "document_type": "composite_chart",
    "patient_info": {
        "name": "Arjun Sharma",
        "age": "48 Years",
        "gender": "Male",
        "date": "2026-10-10",
        "uhid_patient_id": "MED-2026-98124"
    },
    "doctor_hospital_info": {
        "doctor_name": "Dr. Ramesh K. Mehta, MD",
        "clinic_hospital": "Apollo Center for Clinical Endocrinology",
        "specialty": "Internal Medicine & Diabetology",
        "contact": "+91-98765-43210"
    },
    "diagnosis_notes": [
        "Type-2 Diabetes Mellitus with sub-optimal glycemic control",
        "Symptomatic Vitamin D deficiency (fatigue, diffuse bone pain)",
        "Stage 1 Essential Hypertension"
    ],
    "medications": [
        {
            "drug_name": "Metformin Hydrochloride (Glycomet-SR)",
            "generic_name": "Metformin HCl",
            "dosage": "500 mg",
            "form": "Tablet",
            "timing": { "morning": True, "afternoon": False, "evening": False, "night": True },
            "food_relation": "After Food",
            "duration": "90 Days",
            "instructions": "Take immediately after breakfast and dinner to minimize GI upset",
            "confidence": "high"
        },
        {
            "drug_name": "Telmisartan (Telma)",
            "generic_name": "Telmisartan",
            "dosage": "40 mg",
            "form": "Tablet",
            "timing": { "morning": True, "afternoon": False, "evening": False, "night": False },
            "food_relation": "Before Food",
            "duration": "90 Days",
            "instructions": "Take early morning with water; monitor blood pressure regularly",
            "confidence": "high"
        },
        {
            "drug_name": "Cholecalciferol Sachet (Calcirol 60K)",
            "generic_name": "Vitamin D3",
            "dosage": "60,000 IU",
            "form": "Sachet",
            "timing": { "morning": False, "afternoon": False, "evening": True, "night": False },
            "food_relation": "After Food",
            "duration": "Once Weekly for 8 Weeks",
            "instructions": "Dissolve in warm milk every Sunday evening",
            "confidence": "high"
        },
        {
            "drug_name": "Pantoprazole (Pan-40)",
            "generic_name": "Pantoprazole",
            "dosage": "40 mg",
            "form": "Tablet",
            "timing": { "morning": True, "afternoon": False, "evening": False, "night": False },
            "food_relation": "Empty Stomach",
            "duration": "14 Days",
            "instructions": "Take 30 minutes before morning breakfast",
            "confidence": "high"
        }
    ],
    "lab_metrics": [
        {
            "test_name": "25-Hydroxy Vitamin D",
            "category": "Vitamins & Hormones",
            "observed_value": 8.4,
            "unit": "ng/mL",
            "reference_interval": { "min": 30.0, "max": 100.0, "text": "30.0 - 100.0 ng/mL" },
            "status": "CRITICAL_LOW",
            "is_out_of_range": True,
            "risk_level": "critical",
            "clinical_significance": "Severe hypovitaminosis D. High risk of osteomalacia and skeletal fragility. High-dose supplementation indicated."
        },
        {
            "test_name": "Glycated Hemoglobin (HbA1c)",
            "category": "Biochemistry",
            "observed_value": 8.9,
            "unit": "%",
            "reference_interval": { "min": 4.0, "max": 5.6, "text": "4.0 - 5.6 % (Non-diabetic)" },
            "status": "CRITICAL_HIGH",
            "is_out_of_range": True,
            "risk_level": "critical",
            "clinical_significance": "Poor glycemic control over preceding 90 days. Requires dual agent adjustment and lifestyle intervention."
        },
        {
            "test_name": "Fasting Blood Sugar (FBS)",
            "category": "Biochemistry",
            "observed_value": 168.0,
            "unit": "mg/dL",
            "reference_interval": { "min": 70.0, "max": 99.0, "text": "70.0 - 99.0 mg/dL" },
            "status": "HIGH",
            "is_out_of_range": True,
            "risk_level": "high",
            "clinical_significance": "Marked morning hyperglycemia."
        },
        {
            "test_name": "Hemoglobin (Hb)",
            "category": "Hematology",
            "observed_value": 13.8,
            "unit": "g/dL",
            "reference_interval": { "min": 13.0, "max": 17.0, "text": "13.0 - 17.0 g/dL" },
            "status": "NORMAL",
            "is_out_of_range": False,
            "risk_level": "none",
            "clinical_significance": "Adequate oxygen-carrying capacity."
        },
        {
            "test_name": "Serum Creatinine",
            "category": "Renal Function",
            "observed_value": 0.95,
            "unit": "mg/dL",
            "reference_interval": { "min": 0.6, "max": 1.2, "text": "0.6 - 1.2 mg/dL" },
            "status": "NORMAL",
            "is_out_of_range": False,
            "risk_level": "none",
            "clinical_significance": "Normal glomerular filtration function."
        },
        {
            "test_name": "Total Cholesterol",
            "category": "Lipid Profile",
            "observed_value": 235.0,
            "unit": "mg/dL",
            "reference_interval": { "min": 125.0, "max": 200.0, "text": "< 200.0 mg/dL" },
            "status": "HIGH",
            "is_out_of_range": True,
            "risk_level": "high",
            "clinical_significance": "Hypercholesterolemia. Elevated cardiovascular risk score."
        },
        {
            "test_name": "Serum Potassium",
            "category": "Electrolytes",
            "observed_value": 4.3,
            "unit": "mEq/L",
            "reference_interval": { "min": 3.5, "max": 5.0, "text": "3.5 - 5.0 mEq/L" },
            "status": "NORMAL",
            "is_out_of_range": False,
            "risk_level": "none",
            "clinical_significance": "Electrolyte balance within safe range."
        }
    ],
    "critical_alerts": [
        "CRITICAL ALERT: 25-Hydroxy Vitamin D is 8.4 ng/mL (<10 ng/mL = Severe Deficiency). Urgent therapeutic repletion needed.",
        "CRITICAL ALERT: HbA1c is 8.9% (Target: < 7.0%). Elevated risk of microvascular diabetic complications.",
        "PRECAUTION: Metformin dosage requires continuous monitoring of renal function and avoidance during acute dehydration."
    ],
    "transcription_confidence_summary": "Zero-shot Qwen2.5-VL-7B extraction complete. High handwriting transcription confidence on doctor prescription dosage markings and tabular diagnostic laboratory metrics.",
    "metadata": {
        "source": "mock_fallback",
        "model": "Qwen/Qwen2.5-VL-7B-Instruct (Emulated/Fallback)",
        "inference_time_sec": 1.45
    }
}

class ColabClient:
    def __init__(self):
        self.colab_url = settings.COLAB_API_URL.rstrip("/")
        self.timeout = float(settings.COLAB_TIMEOUT_SECONDS)

    async def check_health(self, override_url: str = None) -> Dict[str, Any]:
        """Tests if the Google Colab ngrok endpoint is live and responding"""
        target_url = (override_url or self.colab_url).rstrip("/")
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(
                    f"{target_url}/health",
                    headers={
                        "ngrok-skip-browser-warning": "true",
                        "User-Agent": "MedicalIntelligenceClient/1.0",
                    }
                )
                latency = round((time.time() - start_time) * 1000, 2)
                if res.status_code == 200:
                    return {
                        "status": "online",
                        "accessible": True,
                        "colab_url": target_url,
                        "latency_ms": latency,
                        "model_name": res.json().get("model_name", "Qwen/Qwen2.5-VL-7B-Instruct"),
                        "message": "Connected successfully to Google Colab T4 GPU instance!"
                    }
                else:
                    return {
                        "status": "degraded",
                        "accessible": False,
                        "colab_url": target_url,
                        "latency_ms": latency,
                        "message": f"Colab returned HTTP {res.status_code}"
                    }
        except Exception as e:
            return {
                "status": "offline",
                "accessible": False,
                "colab_url": target_url,
                "message": f"Unable to reach Colab endpoint ({type(e).__name__}). Running in fallback mode or start Colab notebook."
            }

        async def send_to_colab(self, base64_images: list[str], custom_colab_url: str = None) -> dict[str, any]:
            """
            Sends the processed document base64 images directly to the running Google Colab instance.
            Completely ignores mock data fallbacks to guarantee fresh analysis.
            """
            target_url = (custom_colab_url or self.colab_url).rstrip("/")
            
            # Format the request body payload precisely for your Colab BaseModel schema
            payload = {
                "images": base64_images,
                "temperature": 0.1,
                "max_tokens": 3072
            }
            
            logger.info(f"Shipping {len(base64_images)} document frame(s) to live GPU node: {target_url}/analyze")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                try:
                    response = await client.post(
                        f"{target_url}/analyze",
                        json=payload,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    # If the Colab server throws an error code, raise it immediately
                    if response.status_code != 200:
                        raise HTTPException(
                            status_code=response.status_code,
                            detail=f"Google Colab GPU processing failed: {response.text}"
                        )
                    
                    # Return the genuine live model extraction dictionary safely
                    return response.json()
                    
                except httpx.RequestError as exc:
                    logger.error(f"Network transport blockage reaching Colab tunnel: {str(exc)}")
                    raise HTTPException(
                        status_code=503,
                        detail=f"The backend could not reach your Google Colab AI Node tunnel endpoint link. Error: {str(exc)}"
                    )


