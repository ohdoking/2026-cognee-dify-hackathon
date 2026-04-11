import json
import os
from io import BytesIO

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()

DIFY_API_KEY = os.environ.get("DIFY_API_KEY")
DIFY_BASE_URL = os.environ.get("DIFY_URL", "https://api.dify.ai/v1").rstrip("/")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

app = FastAPI(title="BrainSync Auditor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AuditRequest(BaseModel):
    transcript: str


def parse_dify_result(raw_result):
    if isinstance(raw_result, str):
        clean_json = raw_result.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(clean_json)
        except json.JSONDecodeError:
            return raw_result
    return raw_result


def run_audit(transcript):
    if not DIFY_API_KEY:
        raise HTTPException(status_code=500, detail="DIFY_API_KEY is not configured.")

    response = requests.post(
        f"{DIFY_BASE_URL}/workflows/run",
        headers={
            "Authorization": f"Bearer {DIFY_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "inputs": {"meeting_transcript": transcript},
            "response_mode": "blocking",
            "user": "berlin_hacker",
        },
        timeout=120,
    )

    if response.status_code != 200:
        try:
            message = response.json().get("message", "Unknown error")
        except Exception:
            message = response.text or "Unknown error"
        raise HTTPException(status_code=response.status_code, detail=message)

    data = response.json()
    outputs = data.get("data", {}).get("outputs", {})
    return parse_dify_result(outputs.get("result", ""))


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "openaiConfigured": bool(OPENAI_API_KEY),
        "difyConfigured": bool(DIFY_API_KEY),
    }


@app.post("/api/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    if client is None:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not configured.")

    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    audio_file = BytesIO(audio_bytes)
    audio_file.name = file.filename or "recorded_audio.wav"

    try:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text",
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Transcription failed: {exc}") from exc

    return {"transcript": transcript}


@app.post("/api/audit")
def audit_transcript(payload: AuditRequest):
    transcript = payload.transcript.strip()
    if not transcript:
        raise HTTPException(status_code=400, detail="Transcript is required.")

    result = run_audit(transcript)
    return {"result": result}
