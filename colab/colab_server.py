# ============================================================
# QWEN2.5-VL-3B MEDICAL DOCUMENT INTELLIGENCE
# GOOGLE COLAB: CPU + RAM / GPU COMPATIBLE
# FASTAPI + CLOUDFLARE QUICK TUNNEL
# ============================================================
#
# GOOGLE COLAB SETUP INSTRUCTIONS:
# In the first cell of your Google Colab notebook, run:
# !pip install -q -U "optimum-quanto>=0.2.4" "transformers>=4.49.0" accelerate torchvision
# !pip install -q -U qwen-vl-utils fastapi uvicorn nest_asyncio pydantic python-multipart httpx
#
# After installing, click: Runtime -> Restart session, then run this script!
# ============================================================

import os
import io
import re
import gc
import json
import time
import base64
import subprocess
import platform
import queue
import threading
import asyncio
from typing import List, Optional

import nest_asyncio
import httpx
import uvicorn
import torch
from PIL import Image
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from transformers import (
    Qwen2_5_VLForConditionalGeneration,
    AutoProcessor,
    QuantoConfig
)
from qwen_vl_utils import process_vision_info

nest_asyncio.apply()

# ============================================================
# 1. HARDWARE DETECTION & DEVICE SETUP
# ============================================================

USE_CUDA = torch.cuda.is_available()

if USE_CUDA:
    DEVICE = "cuda"
    print("=" * 75)
    print("QWEN2.5-VL MEDICAL DOCUMENT INTELLIGENCE")
    print(f"EXECUTION MODE: GPU ACCELERATED ({torch.cuda.get_device_name(0)})")
    print("=" * 75)
else:
    DEVICE = "cpu"
    # Limit CPU threads to prevent CPU resource thrashing
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    os.environ["OMP_NUM_THREADS"] = "4"
    os.environ["MKL_NUM_THREADS"] = "4"
    torch.set_num_threads(4)
    print("=" * 75)
    print("QWEN2.5-VL MEDICAL DOCUMENT INTELLIGENCE")
    print("EXECUTION MODE: CPU + RAM ONLY")
    print("=" * 75)

print("PyTorch version:", torch.__version__)
print("CUDA availability:", USE_CUDA)
print("Execution device:", DEVICE)

MODEL_ID = "Qwen/Qwen2.5-VL-3B-Instruct"

# ============================================================
# 2. LOAD QWEN MODEL (INT4 QUANTIZATION ON CPU / FP16 ON GPU)
# ============================================================

print(f"\nLoading model {MODEL_ID}. This may take a few moments...")

if USE_CUDA:
    print("Loading on GPU in float16 precision...")
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float16,
        device_map="auto",
        low_cpu_mem_usage=True
    )
else:
    print("Quantization: INT4 (Optimum Quanto) on CPU...")
    quantization_config = QuantoConfig(weights="int4")
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        MODEL_ID,
        quantization_config=quantization_config,
        torch_dtype=torch.float32,
        device_map={"": "cpu"},
        low_cpu_mem_usage=True
    )

model.eval()

# Load image processor
processor = AutoProcessor.from_pretrained(
    MODEL_ID,
    min_pixels=256 * 28 * 28,
    max_pixels=1280 * 28 * 28
)

print("\n" + "=" * 75)
print("MODEL LOADED SUCCESSFULLY")
print("Model:", MODEL_ID)
print("Execution device:", DEVICE)
print("Quantization:", "None (float16)" if USE_CUDA else "INT4 (Quanto)")
print("=" * 75)

# ============================================================
# 3. FASTAPI SERVICE INITIALIZATION
# ============================================================

app = FastAPI(
    title="Qwen2.5-VL Clinical Intelligence Server",
    description="Medical document intelligence API powered by Qwen2.5-VL"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ============================================================
# 4. CLINICAL SYSTEM PROMPT
# ============================================================

CLINICAL_SYSTEM_PROMPT = """
You are a board-certified Clinical Document AI and Medical Chart Intelligence system.
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

IMPORTANT:
- Do not invent missing patient information. Use empty strings for unavailable string values.
- Use empty arrays when no entries are found.
- Do not invent laboratory values or medication dosages.
- Return strictly valid JSON only. No markdown formatting, conversational text, or code block fences outside the JSON.
"""

# ============================================================
# 5. REQUEST MODEL
# ============================================================

class AnalyzeRequest(BaseModel):
    images: List[str]
    temperature: Optional[float] = 0.1
    max_tokens: Optional[int] = 3072

inference_lock = threading.Lock()

# ============================================================
# 6. HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_name": MODEL_ID,
        "gpu_available": USE_CUDA,
        "gpu_name": torch.cuda.get_device_name(0) if USE_CUDA else None,
        "vram_allocated_gb": round(torch.cuda.memory_allocated() / 1e9, 2) if USE_CUDA else 0.0,
        "device": DEVICE,
        "quantization": "None (FP16)" if USE_CUDA else "int4",
        "inference_engine": "Transformers + Optimum Quanto" if not USE_CUDA else "Transformers"
    }

# ============================================================
# 7. MEDICAL DOCUMENT ANALYSIS
# ============================================================

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    if not req.images:
        raise HTTPException(
            status_code=400,
            detail="No images supplied"
        )

    pil_images = []

    try:
        # ----------------------------------------------------
        # Decode uploaded Base64 images
        # ----------------------------------------------------
        for idx, b64_str in enumerate(req.images):
            if "," in b64_str:
                b64_str = b64_str.split(",", 1)[1]

            try:
                img_bytes = base64.b64decode(b64_str, validate=True)
                image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                pil_images.append(image)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid image at position {idx + 1}: {str(e)}"
                )

        # ----------------------------------------------------
        # Prepare multimodal messages
        # ----------------------------------------------------
        content_list = [
            {"type": "image", "image": img}
            for img in pil_images
        ]

        content_list.append({
            "type": "text",
            "text": (
                "Analyze this medical document in detail. "
                "Extract all available information. "
                "Return strict JSON following the provided schema."
            )
        })

        messages = [
            {"role": "system", "content": CLINICAL_SYSTEM_PROMPT},
            {"role": "user", "content": content_list}
        ]

        # ----------------------------------------------------
        # Prepare model input
        # ----------------------------------------------------
        text = processor.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        image_inputs, video_inputs = process_vision_info(messages)

        inputs = processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt"
        )

        inputs = inputs.to(DEVICE)

        print("\n" + "=" * 60)
        print("NEW MEDICAL DOCUMENT REQUEST")
        print("Number of images:", len(pil_images))
        print("Execution device:", DEVICE)
        print("Maximum output tokens:", req.max_tokens)
        print("=" * 60)

        # ----------------------------------------------------
        # Inference using torch.no_grad()
        # NOTE: Using torch.no_grad() instead of torch.inference_mode()
        # is CRITICAL because Quanto INT4 quantization and KV-caching
        # mutate tensor versions during generation, which throws
        # "Cannot set version_counter for inference tensor" under inference_mode().
        # ----------------------------------------------------
        with inference_lock:
            with torch.no_grad():
                generated_ids = model.generate(
                    **inputs,
                    max_new_tokens=req.max_tokens,
                    do_sample=False,
                    use_cache=True
                )

            generated_ids_trimmed = [
                out_ids[len(in_ids):]
                for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]

            output_text = processor.batch_decode(
                generated_ids_trimmed,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False
            )[0]

        # ----------------------------------------------------
        # Clean model response & extract JSON safely
        # ----------------------------------------------------
        clean_text = output_text.strip()

        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        elif clean_text.startswith("```"):
            clean_text = clean_text[3:]

        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]

        clean_text = clean_text.strip()

        # Extract JSON object bounds if model added surrounding commentary
        json_match = re.search(r"(\{.*\})", clean_text, re.DOTALL)
        if json_match:
            clean_text = json_match.group(1)

        try:
            result = json.loads(clean_text)
        except json.JSONDecodeError:
            # Fix common trailing comma syntax mistakes in LLM output
            fixed_text = re.sub(r",\s*([\]}])", r"\1", clean_text)
            try:
                result = json.loads(fixed_text)
            except Exception:
                print("JSON parsing warning; preserving model extraction in structured container:")
                print(output_text[:1000])
                result = {
                    "document_type": "composite_chart",
                    "patient_info": {},
                    "doctor_hospital_info": {},
                    "diagnosis_notes": [],
                    "medications": [],
                    "lab_metrics": [],
                    "critical_alerts": ["Model response was partially unstructured."],
                    "transcription_confidence_summary": output_text,
                    "metadata": {"raw_output": output_text}
                }

        if not isinstance(result, dict):
            result = {
                "document_type": "composite_chart",
                "patient_info": {},
                "doctor_hospital_info": {},
                "diagnosis_notes": [],
                "medications": [],
                "lab_metrics": [],
                "critical_alerts": [],
                "transcription_confidence_summary": str(result),
                "metadata": {"raw_output": str(result)}
            }

        print("Analysis completed successfully.")
        return result

    except HTTPException:
        raise

    except Exception as e:
        print("ANALYSIS ERROR:", repr(e))
        raise HTTPException(
            status_code=500,
            detail=f"Medical document analysis failed: {str(e)}"
        )

    finally:
        # Release image memory after processing
        for image in pil_images:
            try:
                image.close()
            except Exception:
                pass
        pil_images.clear()
        gc.collect()

# ============================================================
# 8. INSTALL CLOUDFLARED (FREE CLOUDFLARE QUICK TUNNEL)
# ============================================================

print("\nInstalling Cloudflare Tunnel...")

architecture = platform.machine().lower()

if architecture in ("x86_64", "amd64"):
    download_url = (
        "https://github.com/cloudflare/cloudflared/"
        "releases/latest/download/cloudflared-linux-amd64"
    )
elif architecture in ("aarch64", "arm64"):
    download_url = (
        "https://github.com/cloudflare/cloudflared/"
        "releases/latest/download/cloudflared-linux-arm64"
    )
else:
    raise RuntimeError(f"Unsupported architecture: {architecture}")

binary_path = "/usr/local/bin/cloudflared"

subprocess.run(
    ["curl", "-fL", "--retry", "3", download_url, "-o", binary_path],
    check=True
)

os.chmod(binary_path, 0o755)

subprocess.run([binary_path, "--version"], check=True)

print("Cloudflared installed successfully.")

# ============================================================
# 9. START FASTAPI SERVER
# ============================================================

print("\nStarting FastAPI server on 127.0.0.1:8000...")

# Terminate any existing background tunnel
subprocess.run(["pkill", "-x", "cloudflared"], check=False)

config = uvicorn.Config(
    app,
    host="127.0.0.1",
    port=8000,
    log_level="info"
)

server = uvicorn.Server(config)
server_task = asyncio.create_task(server.serve())

# ============================================================
# 10. VERIFY API HEALTH
# ============================================================

server_ready = False

async def verify_server_ready():
    async with httpx.AsyncClient() as client:
        for attempt in range(60):
            try:
                response = await client.get("http://127.0.0.1:8000/health", timeout=5)
                if response.status_code == 200:
                    print("\nFastAPI health check successful!")
                    print("API response:", json.dumps(response.json(), indent=4))
                    return True
            except Exception:
                print(f"Waiting for FastAPI... {attempt + 1}/60")
            await asyncio.sleep(1)
    return False

# Run verification in background loop
loop = asyncio.get_event_loop()
if loop.is_running():
    # In Jupyter / Colab
    import nest_asyncio
    nest_asyncio.apply()
    server_ready = loop.run_until_complete(verify_server_ready())
else:
    server_ready = asyncio.run(verify_server_ready())

if not server_ready:
    raise RuntimeError("FastAPI health check failed.")

print("\nFastAPI server is running.")

# ============================================================
# 11. START CLOUDFLARE QUICK TUNNEL
# ============================================================

print("\nStarting Cloudflare Quick Tunnel...")

cf_process = subprocess.Popen(
    [binary_path, "tunnel", "--no-autoupdate", "--url", "http://127.0.0.1:8000"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1
)

log_queue = queue.Queue()

def read_cloudflare_logs():
    for line in cf_process.stderr:
        log_queue.put(line)

threading.Thread(target=read_cloudflare_logs, daemon=True).start()

public_url = None
start_time = time.time()

while time.time() - start_time < 60:
    if cf_process.poll() is not None:
        raise RuntimeError(f"Cloudflare exited with code {cf_process.returncode}")

    try:
        line = log_queue.get(timeout=0.5)
        print(line.strip())
        match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
        if match:
            public_url = match.group(0)
            break
    except queue.Empty:
        continue

if not public_url:
    cf_process.terminate()
    raise RuntimeError("Cloudflare tunnel URL was not generated within 60 seconds.")

# ============================================================
# 12. DISPLAY PUBLIC API URL
# ============================================================

print("\n" + "=" * 75)
print("YOUR PUBLIC COLAB SERVER URL IS LIVE:")
print(public_url)
print("=" * 75)
print("\nAdd this to your backend/.env as:")
print(f"COLAB_API_URL={public_url}")
print("\nOr paste this URL directly into the frontend dashboard header input!")
print("\nHealth endpoint:")
print(f"{public_url}/health")
print("\nSwagger API documentation:")
print(f"{public_url}/docs")
print("=" * 75)

# ============================================================
# 13. KEEP SERVER AND TUNNEL RUNNING
# ============================================================

print(f"\nServer is running ({DEVICE.upper()}).")
print("Do not stop this Colab cell while using the API.")

async def run_server_loop():
    await server_task

try:
    curr_loop = asyncio.get_event_loop()
    if curr_loop.is_running():
        import nest_asyncio
        nest_asyncio.apply()
        curr_loop.run_until_complete(run_server_loop())
    else:
        asyncio.run(run_server_loop())
except Exception as e:
    # If run in an interactive Colab cell, you can also execute: await server_task
    print("Server loop active:", e)


