# BrainSync Auditor

BrainSync Auditor is now structured as a small full-stack app:

- `frontend/`: React + Vite UI
- `api/`: FastAPI backend for transcription and workflow execution
- `ingest_data.py` / `ingest_rest.py`: Cognee knowledge ingestion scripts

This split is intentional. The browser handles UI only, while API keys stay server-side in FastAPI for OpenAI Whisper and Dify workflow calls.

## Product Flow

The application now follows a strict 3-step workflow:

1. `Input`
   Paste transcript text, record audio in the browser, or upload a text/audio file.
2. `Execute workflow`
   The transcript is sent to the FastAPI backend, which calls Dify and returns quiz data.
3. `Interactive quiz card view`
   The frontend renders one quiz at a time with answer selection, reveal, and navigation.

## Stack

- React 18
- Vite 5
- FastAPI
- OpenAI Whisper transcription
- Dify workflow execution
- Cognee ingestion scripts for knowledge preparation

## Project Structure

- `frontend/src/App.jsx`: Main React workflow UI
- `frontend/src/styles.css`: Frontend styling and theme system
- `api/main.py`: FastAPI routes for health, transcription, and audit execution
- `app.py`: Previous Streamlit prototype
- `ingest_data.py`: Cognee SDK ingestion script
- `ingest_rest.py`: Cognee REST ingestion script

## Environment Variables

Create a local `.env` file:

```env
OPENAI_API_KEY=...
DIFY_API_KEY=...
DIFY_URL=https://api.dify.ai/v1
WORKFLOW_ID=...

COGNEE_API_KEY=...
BASE_URL=...
```

Notes:

- `DIFY_URL` defaults to `https://api.dify.ai/v1`.
- `WORKFLOW_ID` is still present in local config, though the current request uses `/workflows/run`.
- `COGNEE_API_KEY` and `BASE_URL` are only required for the ingestion/search helper scripts.

## Install

Python dependencies:

```bash
poetry install
```

Frontend dependencies:

```bash
cd frontend
npm install
```

## Run

Start the API:

```bash
poetry run uvicorn api.main:app --reload --port 8000
```

Start the frontend:

```bash
cd frontend
npm run dev
```

Open the Vite app in your browser at `http://localhost:5173`.

## Optional Frontend API Override

If you want the frontend to target a different backend URL, create `frontend/.env.local`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Ingest Background Knowledge

Using the Cognee SDK:

```bash
poetry run python ingest_data.py
```

Using the REST ingestion flow:

```bash
poetry run python ingest_rest.py
```

## Status

The Streamlit prototype is retained in the repo as the older version, but the intended path is now the React + FastAPI application.
