# BrainSync Auditor

BrainSync Auditor is a meeting-memory verification product.

The goal is simple:

- capture what was said
- verify what was actually remembered
- prevent soft approvals and memory drift from becoming execution mistakes

This repository now contains two parallel implementation paths:

- `v1`: web app flow with React + FastAPI, originally built around Dify + Cognee
- `v2`: new hybrid iOS-oriented flow with **Cognee-only backend orchestration** and **local Gemma quiz generation**

The old code is kept. The new code lives under `/api/v2/` and `ios/`.

---

## Current Architecture

### Web / v1

- `frontend/`: React + Vite UI
- `api/`: FastAPI backend
- workflow-based quiz generation
- Cognee-backed feedback and graph/fallback graph rendering

### Hybrid iOS / v2

- iPhone records or imports meeting audio
- FastAPI creates transcript
- FastAPI syncs/searches Cognee Cloud
- iPhone generates quiz locally with Gemma
- FastAPI returns Cognee-backed feedback after quiz completion

This hybrid split is intentional:

- local device handles the private/on-device quiz generation step
- backend handles Cognee Cloud access and hides credentials

---

## v2 Product Flow

The new `v2` flow is:

1. User taps a button in the iOS app and creates a transcript
2. Transcript is synced to Cognee Cloud and relevant context is searched
3. Cognee context is used to prepare an analysis package
4. Gemma 4 runs locally on the iPhone and creates quiz questions
5. After the user solves the quiz, the backend returns feedback and “what to remember” guidance

The v2 flow removes Dify from the quiz-generation pipeline.

---

## API Layout

### Existing routes

The existing API remains in:

- `api/main.py`
- `api/services/cognee.py`

### New v2 routes

Implemented in:

- `api/v2/router.py`
- `api/v2/service.py`
- `api/v2/schemas.py`

Routes:

- `POST /api/v2/transcribe`
- `POST /api/v2/session/prepare`
- `POST /api/v2/session/feedback`

### `POST /api/v2/transcribe`

Creates a transcript from uploaded audio.

### `POST /api/v2/session/prepare`

Takes a transcript and:

- ingests it into Cognee
- searches Cognee for relevant context
- returns:
  - transcript
  - dataset name
  - retrieved contexts
  - analysis query
  - a Gemma-ready prompt package for local generation

### `POST /api/v2/session/feedback`

Takes:

- transcript
- generated quiz list
- user answers

Returns:

- Cognee-backed review items
- evidence per quiz item
- remember highlights

---

## Cognee Graph Handling

BrainSync now handles graph rendering this way:

- first try to use `dataset_id` from Cognee search results
- fetch native dataset graph if available
- filter that graph for relevant nodes/edges
- if native graph is unavailable, build a **fallback graph** from:
  - question
  - user answer
  - correct answer
  - insight
  - evidence contexts

So the frontend always renders a graph through React Flow.

It is either:

- native Cognee graph
- or a BrainSync fallback graph built from Cognee search evidence

---

## iOS App Scaffold

The iOS source scaffold lives in:

- `ios/BrainSyncV2/`

Files:

- `BrainSyncV2App.swift`
- `ContentView.swift`
- `BrainSyncViewModel.swift`
- `APIClient.swift`
- `Models.swift`
- `LocalGemmaQuizGenerator.swift`

Supporting notes:

- `ios/README.md`
- `ios/BrainSyncV2/Info.plist`

Important:

- this repo currently includes a **SwiftUI source scaffold**
- it does **not** yet include a full generated `.xcodeproj`
- the local Gemma integration is abstracted behind a protocol so you can replace the preview generator with a real on-device runtime bridge

---

## Gemma 4 in v2

The intended v2 model flow is:

- Cognee Cloud for retrieval and grounding
- Gemma 4 on-device on iPhone for local quiz generation

Current implementation detail:

- `LocalGemmaQuizGenerating` defines the local quiz generator interface
- `PreviewGemmaQuizGenerator` is currently a placeholder/demo implementation
- the backend returns a `gemmaPrompt` package from `/api/v2/session/prepare`

This means the missing step is **not** prompt construction.

The missing step is wiring that prompt package into your actual local Gemma runtime on iPhone.

---

## Environment Variables

Create a local `.env` file:

```env
OPENAI_API_KEY=...

DIFY_API_KEY=...
DIFY_URL=https://api.dify.ai/v1

COGNEE_API_KEY=...
BASE_URL=...
COGNEE_DATASET_NAME=Project_Aurora_Knowledge

GEMMA_BASE_URL=http://127.0.0.1:11434
GEMMA_MODEL=gemma4
```

Notes:

- `OPENAI_API_KEY` is used for transcription in the current backend
- `DIFY_*` is still needed for the older v1 path
- `COGNEE_*` is required for v1 feedback and the new v2 hybrid path
- `GEMMA_*` is reserved for future local/server Gemma wiring

---

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

Slide deck dependencies:

```bash
cd slides
npm install
```

---

## Run

### Backend

```bash
poetry run uvicorn api.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm run dev
```

The web app uses the existing v1 React experience.

---

## iOS Setup

1. Open Xcode
2. Create a new iOS App project named `BrainSyncV2`
3. Copy the files from `ios/BrainSyncV2/` into the new project
4. Use `ios/BrainSyncV2/Info.plist` as your starting plist
5. Point the app to your backend base URL in `APIClient.swift`

The current iOS scaffold is enough to demonstrate:

- transcript text flow
- Cognee session preparation
- quiz rendering
- feedback rendering

It still needs a real local Gemma runtime bridge for production on-device generation.

---

## Demo Assets

Demo assets are stored in:

- `demo_assets/`
- `test_data/`
- `PRESENTATION.md`
- `slides/slides.md`

Useful files:

- `demo_assets/berlin_hackathon_conflict.wav`
- `demo_assets/berlin_hackathon_conflict_script.txt`
- `test_data/test_conversation_v3.md`
- `test_data/berlin_hackathon_demo_test_cases.json`

---

## Verification Status

Verified in this repository:

- Python compile for the current backend modules
- frontend production build
- route-level checks for `/api/v2/*`

Not fully verified yet:

- a real local Gemma 4 runtime integration inside the custom iOS app
- a generated and buildable Xcode project file in this repo

---

## Repo Structure

- `api/main.py`: existing API entrypoint
- `api/services/cognee.py`: Cognee REST integration and graph/fallback graph logic
- `api/v2/`: new Cognee-only hybrid flow for iOS
- `frontend/`: current web product
- `ios/`: new SwiftUI app scaffold for v2
- `slides/`: Slidev presentation deck
- `demo_assets/`: audio and script assets for demo
- `test_data/`: presentation/demo test scenarios
