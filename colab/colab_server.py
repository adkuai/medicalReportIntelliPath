"""
=============================================================================
Google Colab Server for Project 2: Specialized Zero-Shot Medical Chart & Prescription Intelligence
Target Hardware: Google Colab Free T4 GPU (15GB VRAM)
Model: Qwen/Qwen2.5-VL-7B-Instruct (4-bit NF4 Quantization)

COLAB SETUP COMMANDS:
!pip install -q -U --force-reinstall "pillow>=10.4.0,<11.2.0"
!pip install -q -U "bitsandbytes>=0.46.1" "transformers>=4.49.0" accelerate torchvision
!pip install -q -U qwen-vl-utils fastapi uvicorn pyngrok nest_asyncio pydantic python-multipart
(After installing, click Runtime -> Restart session before running this script!)
=============================================================================
"""

import os
import io
import re
import json
import base64
import torch
from PIL import Image
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

# Install check & dependencies imports
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import nest_asyncio
from pyngrok import ngrok

from transformers import (
    Qwen2_5_VLForConditionalGeneration,
    AutoProcessor,
    BitsAndBytesConfig
)
from qwen_vl_utils import process_vision_info

# Initialize FastAPI App
app = FastAPI(title="Colab Qwen2.5-VL Medical Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# 1. MODEL LOADING & INITIALIZATION (T4 GPU Optimized)
# ---------------------------------------------------------------------------
MODEL_ID = "Qwen/Qwen2.5-VL-7B-Instruct"

print("=" * 70)
print(f"Loading {MODEL_ID} for Google Colab T4 GPU...")
print("=" * 70)

try:
    import bitsandbytes as bnb
    print(f"Using bitsandbytes {bnb.__version__} (4-bit NF4 quantization, ~6GB VRAM)...")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        MODEL_ID,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True
    )
except ImportError as bnb_err:
    print(f"⚠️ bitsandbytes load note: {bnb_err}")
    print("Falling back to standard float16 precision with device_map='auto'...")
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        MODEL_ID,
        device_map="auto",
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True
    )

# Set resolution bounds: min 256*28*28, max 1280*28*28 to balance OCR fidelity and speed
processor = AutoProcessor.from_pretrained(
    MODEL_ID,
    min_pixels=256 * 28 * 28,
    max_pixels=1280 * 28 * 28
)

print("\nModel successfully loaded on GPU!")
print(f"VRAM Allocated: {torch.cuda.memory_allocated() / 1e9:.2f} GB")
print(f"VRAM Reserved:  {torch.cuda.memory_reserved() / 1e9:.2f} GB\n")

# ---------------------------------------------------------------------------
# 2. HIGHLY SPECIALIZED CLINICAL ZERO-SHOT SYSTEM PROMPT
# ---------------------------------------------------------------------------
CLINICAL_SYSTEM_PROMPT = """You are a board-certified Clinical Document AI and Medical Chart Intelligence system.
Your mission is to perform rigorous, zero-shot transcription and laboratory interpretation from photographs of messy doctor prescriptions and complex diagnostic lab reports.

RULES:
1. Examine handwriting with utmost care: decipher medication names (brand vs generic), dosage strengths (e.g., 500mg, 40mg, 60K IU), dosage forms (Tablet, Capsule, Syrup, Sachet, Injection), and schedule notation (1-0-1, OD, BD, TDS, QID, HS, Before Food, After Food).
2. For laboratory tables, extract test names (e.g., Vitamin D, Hemoglobin, Fasting Blood Sugar, HbA1c, Serum Creatinine), numeric observed values, units, and reference intervals.
3. Classify each lab marker status as NORMAL, HIGH, LOW, CRITICAL_HIGH, or CRITICAL_LOW.
4. If an observed metric is outside safe boundaries, flag is_out_of_range = true and assign appropriate risk_level (moderate, high, critical).
5. Generate high-priority clinical alerts for severe anomalies or critical medication precautions.

OUTPUT FORMAT:
You MUST respond with ONLY a strictly valid JSON object adhering to this schema:
{
  "document_type": "handwritten_prescription" | "laboratory_report" | "composite_chart",
  "patient_info": {
    "name": "string",
    "age": "string",
    "gender": "string",
    "date": "string",
    "uhid_patient_id": "string"
  },
  "doctor_hospital_info": {
    "doctor_name": "string",
    "clinic_hospital": "string",
    "specialty": "string",
    "contact": "string"
  },
  "diagnosis_notes": ["string"],
  "medications": [
    {
      "drug_name": "string",
      "generic_name": "string",
      "dosage": "string",
      "form": "Tablet" | "Capsule" | "Syrup" | "Sachet" | "Drops" | "Injection" | "Other",
      "timing": {
        "morning": true/false,
        "afternoon": true/false,
        "evening": true/false,
        "night": true/false
      },
      "food_relation": "Before Food" | "After Food" | "With Food" | "Empty Stomach" | "As Needed",
      "duration": "string",
      "instructions": "string",
      "confidence": "high" | "medium" | "low"
    }
  ],
  "lab_metrics": [
    {
      "test_name": "string",
      "category": "string",
      "observed_value": "string or number",
      "unit": "string",
      "reference_interval": {
        "min": number or null,
        "max": number or null,
        "text": "string"
      },
      "status": "NORMAL" | "HIGH" | "LOW" | "CRITICAL_HIGH" | "CRITICAL_LOW",
      "is_out_of_range": true/false,
      "risk_level": "none" | "moderate" | "high" | "critical",
      "clinical_significance": "string"
    }
  ],
  "critical_alerts": ["string"],
  "transcription_confidence_summary": "string"
}
"""

# ---------------------------------------------------------------------------
# 3. FASTAPI REQUEST / RESPONSE SCHEMAS & ENDPOINTS
# ---------------------------------------------------------------------------
class AnalyzeRequest(BaseModel):
    images: List[str]  # List of base64 JPEG/PNG strings
    temperature: Optional[float] = 0.1
    max_tokens: Optional[int] = 3072

@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_name": MODEL_ID,
        "gpu_available": torch.cuda.is_available(),
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None",
        "vram_allocated_gb": round(torch.cuda.memory_allocated() / 1e9, 2) if torch.cuda.is_available() else 0
    }

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    if not req.images:
        raise HTTPException(status_code=400, detail="At least one image base64 string is required.")

    # Decode base64 images into PIL Images
    pil_images = []
    for idx, b64_str in enumerate(req.images):
        try:
            # Strip data URI prefix if present
            if "," in b64_str:
                b64_str = b64_str.split(",", 1)[1]
            img_bytes = base64.b64decode(b64_str)
            img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            pil_images.append(img)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to decode image #{idx+1}: {str(e)}")

    # Construct Qwen2.5-VL Multi-modal Message
    content_list = []
    for img in pil_images:
        content_list.append({"type": "image", "image": img})
    content_list.append({
        "type": "text",
        "text": "Analyze this medical document in detail. Extract patient details, transcribe doctor handwriting, build the medication dosage timing matrix, read all laboratory markers, evaluate reference intervals, and return the strict JSON schema."
    })

    messages = [
        {"role": "system", "content": CLINICAL_SYSTEM_PROMPT},
        {"role": "user", "content": content_list}
    ]

    # Preprocess inputs
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, video_inputs = process_vision_info(messages)
    
    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt"
    ).to("cuda")

    # Run zero-shot inference
    with torch.no_grad():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=req.max_tokens,
            temperature=req.temperature,
            do_sample=False
        )
        
        # Trim input prompt tokens from output
        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        
        output_text = processor.batch_decode(
            generated_ids_trimmed,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )[0]

    # Clean markdown formatting & extract JSON
    clean_text = output_text.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:]
    elif clean_text.startswith("```"):
        clean_text = clean_text[3:]
    if clean_text.endswith("```"):
        clean_text = clean_text[:-3]
    clean_text = clean_text.strip()

    # Find JSON bounds if surrounded by conversational filler
    json_match = re.search(r"(\{.*\})", clean_text, re.DOTALL)
    if json_match:
        clean_text = json_match.group(1)

    try:
        parsed_json = json.loads(clean_text)
        return parsed_json
    except json.JSONDecodeError as err:
        # Fallback wrapper if model omitted closing brace or slight JSON syntax imperfection
        print(f"JSON Parse warning: {err}\nRaw Model Output:\n{output_text}")
        return {
            "document_type": "composite_chart",
            "transcription_confidence_summary": output_text,
            "patient_info": {},
            "doctor_hospital_info": {},
            "diagnosis_notes": ["Raw output captured; check transcription summary."],
            "medications": [],
            "lab_metrics": [],
            "critical_alerts": ["Model response was partially unstructured."],
            "raw_text": output_text
        }

# ---------------------------------------------------------------------------
# 4. TUNNEL & RUN SERVER
# ---------------------------------------------------------------------------
def run_colab_server(ngrok_auth_token: Optional[str] = None, port: int = 8000):
    import subprocess
    import time
    nest_asyncio.apply()

    public_url = None

    if ngrok_auth_token and ngrok_auth_token.strip():
        ngrok.set_auth_token(ngrok_auth_token.strip())
        ngrok.kill()
        tunnel = ngrok.connect(port, proto="http")
        public_url = tunnel.public_url
    else:
        print("⚡ No ngrok token provided. Starting FREE Cloudflare Tunnel (No signup needed)...")
        subprocess.run(["wget", "-q", "-nc", "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb"], check=False)
        subprocess.run(["dpkg", "-i", "cloudflared-linux-amd64.deb"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        cf_process = subprocess.Popen(
            ["cloudflared", "tunnel", "--url", f"http://127.0.0.1:{port}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        start_time = time.time()
        while time.time() - start_time < 25:
            line = cf_process.stderr.readline()
            if not line:
                time.sleep(0.5)
                continue
            match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
            if match:
                public_url = match.group(0)
                break

    print("\n" + "=" * 70)
    print("🚀 GOOGLE COLAB SERVER IS LIVE!")
    if public_url:
        print(f"Public API URL: {public_url}")
        print(f"Healthcheck:   {public_url}/health")
        print(f"Analyze API:   {public_url}/analyze")
        print("=" * 70)
        print(f"\n👉 Copy this URL: {public_url}")
        print("👉 Paste it into your backend/.env as:")
        print(f"   COLAB_API_URL={public_url}\n")
        print("Or paste it directly into the frontend dashboard header!\n" + "=" * 70)
    else:
        print("Starting server on local port", port)

    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    auth_token = os.environ.get("NGROK_AUTHTOKEN", "").strip()
    run_colab_server(ngrok_auth_token=auth_token or None)


