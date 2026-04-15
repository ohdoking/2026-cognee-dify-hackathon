from io import BytesIO

from fastapi import APIRouter, File, HTTPException, UploadFile
from openai import OpenAI

from api.config import OPENAI_API_KEY
from api.v2.schemas import V2FeedbackRequest, V2SessionPrepareRequest
from api.v2.service import build_v2_feedback, prepare_v2_session

router = APIRouter(prefix="/api/v2", tags=["v2"])

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


@router.post("/transcribe")
async def v2_transcribe_audio(file: UploadFile = File(...)):
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


@router.post("/session/prepare")
def v2_prepare_session(payload: V2SessionPrepareRequest):
    return prepare_v2_session(payload)


@router.post("/session/feedback")
def v2_session_feedback(payload: V2FeedbackRequest):
    return build_v2_feedback(payload)
