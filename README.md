# BrainSync Auditor

BrainSync Auditor is a Streamlit app built for the 2026 Cognee + Dify hackathon. It turns meeting transcripts or live recordings into compliance-focused recall checks by combining:

- Whisper transcription for audio input
- Dify workflows for structured quiz generation
- Cognee-backed project knowledge for conflict and consistency checks

## What It Does

- Accepts transcript input from pasted text, live microphone capture, or uploaded `.txt` / audio files
- Transcribes recorded or uploaded audio with OpenAI Whisper
- Sends the prepared transcript into a Dify workflow
- Renders the returned quiz payload as a cleaner audit console instead of a default Streamlit demo layout

## UI Refresh

The current app UI was redesigned to feel more intentional and product-like:

- Editorial hero section with clearer hierarchy
- Warmer visual system with custom surfaces, spacing, and controls
- Transcript review metrics for words, characters, and lines
- Persistent audit results in a dedicated right-side review panel
- Structured quiz cards for questions, options, answers, and insights

## Project Files

- `app.py`: Main Streamlit UI and Dify / Whisper integration
- `ingest_data.py`: Cognee ingestion script using the Python SDK
- `ingest_rest.py`: Cognee ingestion script using REST endpoints
- `search_test.py`: Search test helper
- `test_conversation.md`: Sample meeting conversation

## Requirements

- Python `3.12` to `3.13`
- Poetry
- OpenAI API key
- Dify API key and workflow endpoint configuration
- Optional Cognee API configuration for knowledge ingestion

## Environment Variables

Create a local `.env` file with the values your environment needs:

```env
OPENAI_API_KEY=...
DIFY_API_KEY=...
DIFY_URL=https://api.dify.ai/v1
WORKFLOW_ID=...

COGNEE_API_KEY=...
BASE_URL=...
```

Notes:

- `WORKFLOW_ID` is read by the app, although the current Dify request uses `/workflows/run`.
- `BASE_URL` is used by `ingest_rest.py`.

## Install

```bash
poetry install
```

## Run The App

```bash
poetry run streamlit run app.py
```

## Ingest Background Knowledge

Using the Cognee Python SDK:

```bash
poetry run python ingest_data.py
```

Using the REST flow:

```bash
poetry run python ingest_rest.py
```

## Suggested Demo Flow

1. Ingest the sample background knowledge into Cognee.
2. Start the Streamlit app.
3. Paste a transcript or record a short meeting segment.
4. Review the transcript and run the audit.
5. Use the generated quizzes to validate whether the meeting aligned with the project rules.

## Status

This repo is a hackathon prototype. The core flow works, but it still assumes valid API credentials and a correctly configured Dify workflow response format.
