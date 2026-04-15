import json
import re
import time
from io import BytesIO

import requests
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

from api.config import (
    COGNEE_DATASET_NAME,
    DIFY_API_KEY,
    DIFY_BASE_URL,
    OPENAI_API_KEY,
)
from api.schemas import (
    AuditRequest,
    CogneeFeedbackBatchRequest,
    CogneeFeedbackRequest,
    CogneeIngestRequest,
)
from api.services.cognee import (
    build_feedback_error_response,
    build_feedback_response,
    cognee_dataset_name,
    ingest_text_to_cognee,
    ingest_transcript_to_cognee,
    is_cognee_configured,
)
from api.v2.router import router as v2_router

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

app.include_router(v2_router)

def parse_dify_result(raw_result):
    if isinstance(raw_result, str):
        clean_json = raw_result.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(clean_json)
        except Exception:
            return raw_result
    return raw_result


def summarize_html_error(html_text: str):
    title_match = re.search(r"<title>(.*?)</title>", html_text, re.IGNORECASE | re.DOTALL)
    title = title_match.group(1).strip() if title_match else ""
    if "504" in html_text or "Gateway time-out" in html_text:
      return "Dify workflow timed out upstream (504). Try again in a moment or shorten the transcript."
    if title:
        return title
    return "Dify returned an HTML error page."


def extract_dify_error_message(response: requests.Response):
    content_type = (response.headers.get("content-type") or "").lower()

    if "application/json" in content_type:
        try:
            data = response.json()
            return (
                data.get("message")
                or data.get("detail")
                or data.get("error")
                or f"Dify request failed with status {response.status_code}."
            )
        except Exception:
            pass

    body = (response.text or "").strip()
    if "<html" in body.lower():
        return summarize_html_error(body)
    if body:
        return body[:400]
    return f"Dify request failed with status {response.status_code}."


def run_audit(transcript: str):
    if not DIFY_API_KEY:
        raise HTTPException(status_code=500, detail="DIFY_API_KEY is not configured.")

    request_headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json",
    }
    request_body = {
        "inputs": {"meeting_transcript": transcript},
        "response_mode": "blocking",
        "user": "berlin_hacker",
    }

    last_error_message = "Unknown Dify error."
    last_status_code = 502
    retryable_statuses = {502, 503, 504, 524}

    for attempt in range(2):
        try:
            response = requests.post(
                f"{DIFY_BASE_URL}/workflows/run",
                headers=request_headers,
                json=request_body,
                timeout=180,
            )
        except requests.Timeout as exc:
            last_error_message = "Dify workflow request timed out. Try again in a moment or shorten the transcript."
            last_status_code = 504
            if attempt == 0:
                time.sleep(1.0)
                continue
            raise HTTPException(status_code=504, detail=last_error_message) from exc
        except requests.RequestException as exc:
            last_error_message = f"Could not reach Dify workflow service: {exc}"
            last_status_code = 502
            if attempt == 0:
                time.sleep(1.0)
                continue
            raise HTTPException(status_code=502, detail=last_error_message) from exc

        if response.status_code == 200:
            try:
                data = response.json()
            except Exception as exc:
                raise HTTPException(
                    status_code=502,
                    detail="Dify returned an unreadable response payload.",
                ) from exc
            outputs = data.get("data", {}).get("outputs", {})
            return parse_dify_result(outputs.get("result", ""))

        last_error_message = extract_dify_error_message(response)
        last_status_code = response.status_code

        if response.status_code in retryable_statuses and attempt == 0:
            time.sleep(1.0)
            continue

        raise HTTPException(status_code=response.status_code, detail=last_error_message)

    raise HTTPException(status_code=last_status_code, detail=last_error_message)


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "openaiConfigured": bool(OPENAI_API_KEY),
        "cogneeConfigured": is_cognee_configured(),
        "difyConfigured": bool(DIFY_API_KEY),
        "cogneeDatasetName": COGNEE_DATASET_NAME,
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


@app.post("/api/cognee/ingest-transcript")
def cognee_ingest_transcript(payload: CogneeIngestRequest):
    dataset_name = cognee_dataset_name(payload.dataset_name)
    result = ingest_transcript_to_cognee(payload.transcript, dataset_name)
    return result


def extract_uploaded_text(filename: str, raw_bytes: bytes):
    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Uploaded context file is empty.")

    allowed_suffixes = (".txt", ".md", ".markdown", ".json", ".csv", ".yaml", ".yml")
    lowered_name = (filename or "").lower()
    if lowered_name and not lowered_name.endswith(allowed_suffixes):
        raise HTTPException(
            status_code=400,
            detail="Unsupported context file type. Use .txt, .md, .json, .csv, .yaml, or .yml.",
        )

    for encoding in ("utf-8-sig", "utf-8", "utf-16", "latin-1"):
        try:
            text = raw_bytes.decode(encoding).strip()
            if text:
                return text
        except UnicodeDecodeError:
            continue

    raise HTTPException(status_code=400, detail="Could not decode the uploaded context file.")


@app.post("/api/cognee/upload-context")
async def cognee_upload_context_file(
    file: UploadFile = File(...),
    dataset_name: str | None = Form(None),
):
    raw_bytes = await file.read()
    text = extract_uploaded_text(file.filename or "context.txt", raw_bytes)
    target_dataset = cognee_dataset_name(dataset_name)
    result = ingest_text_to_cognee(text, target_dataset)
    return {
        **result,
        "fileName": file.filename or "context.txt",
        "chars": len(text),
        "sourceType": "context_file",
    }


@app.post("/api/cognee/search-feedback")
def cognee_search_feedback(payload: CogneeFeedbackRequest):
    return build_feedback_response(payload)


@app.post("/api/cognee/summary-feedback")
def cognee_summary_feedback(payload: CogneeFeedbackBatchRequest):
    items = []
    for index, item in enumerate(payload.items):
        item_payload = item.model_copy(update={"index": item.index if item.index is not None else index})
        try:
            items.append(
                build_feedback_response(
                    item_payload,
                    dataset_name_override=payload.dataset_name,
                    top_k_override=payload.top_k,
                )
            )
        except Exception as exc:
            items.append(build_feedback_error_response(item_payload, exc))

    return {"items": items}


@app.post("/api/audit")
def audit_transcript(payload: AuditRequest):
    transcript = payload.transcript.strip()
    if not transcript:
        raise HTTPException(status_code=400, detail="Transcript is required.")

    result = run_audit(transcript)
    cognee_result = None
    if is_cognee_configured():
        try:
            cognee_result = ingest_transcript_to_cognee(
                transcript,
                cognee_dataset_name(payload.dataset_name),
            )
        except Exception as exc:
            cognee_result = {"ingested": False, "error": str(exc)}

    return {"result": result, "cognee": cognee_result}
