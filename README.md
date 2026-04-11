# Misstery

Misstery is an AI-powered verification service that helps users catch missed information, hidden gaps, and overlooked context before those misses turn into mistakes.

Misstery is structured as a small full-stack app:

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
3. `Interactive quiz and review`
   The frontend renders one quiz at a time with answer selection, reveal, navigation, and a final review stage with expandable feedback cards.

## Current UX

The current frontend includes:

- input stage for text, audio upload, and live recording
- explicit workflow loading state while the Dify response is pending
- interactive quiz cards with answer reveal
- final overview screen showing:
  - correct, wrong, answered, and unanswered totals
  - overall feedback on alignment risk
  - a checklist for what to remember next time
  - expandable review cards per question

Each review card shows:

- your answer
- correct answer
- why it matters
- feedback
- what to remember next time
- communication risk
- revisit-card action

## Stack

- React 18
- Vite 5
- FastAPI
- OpenAI Whisper transcription
- Dify workflow execution
- Cognee ingestion scripts for knowledge preparation
- React-based quiz review and post-quiz coaching

## Planned Cognee Integration

The next backend iteration is to connect the quiz feedback stage directly to Cognee through REST APIs instead of the Python SDK.

Target direction:

- ingest new meeting context into Cognee through REST
- trigger graph updates through REST
- query relevant policy context during the quiz feedback session
- show supporting evidence and memory guidance in the final review screen

Intended use:

- Dify generates the quiz structure
- Cognee provides relevant context, policy grounding, and explanation support

## Project Structure

- `frontend/src/App.jsx`: Main React workflow UI
- `frontend/src/styles.css`: Frontend styling and theme system
- `api/main.py`: FastAPI routes for health, transcription, and audit execution
- `app.py`: Previous Streamlit prototype
- `ingest_data.py`: Cognee SDK ingestion script
- `ingest_rest.py`: Cognee REST ingestion script
- `test_conversation.md`: Demo transcripts and expected outcomes
- `PRESENTATION.md`: Presentation script and slide outline

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
- `COGNEE_API_KEY` and `BASE_URL` are currently used by the ingestion/search helper scripts and are intended to be reused for the REST-based quiz feedback integration.

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

## Demo Assets

For presentation and demo preparation:

- `test_conversation.md` contains multiple meeting scenarios with:
  - transcript
  - actual result
  - expected result
  - what Misstery should flag
- `PRESENTATION.md` contains a presentation-ready explanation of the service, architecture, workflow, and demo flow
- `slides/slides.md` is a Slidev deck for presenting to an audience in the browser

## Presentation Deck

The repo includes a Slidev presentation so you can present directly from Markdown.

Install slide dependencies:

```bash
cd slides
npm install
```

Run the presentation locally:

```bash
cd slides
npm run dev
```

Build static presentation assets:

```bash
cd slides
npm run build
```

## Status

The Streamlit prototype is retained in the repo as the older version, but the intended path is now the React + FastAPI application with Cognee REST-backed feedback in the post-quiz review stage.
