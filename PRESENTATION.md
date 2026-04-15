# BrainSync Auditor Presentation

## Slide 1: Title

**BrainSync Auditor**

Turn meeting agreement into verified understanding.

Subtitle:

- Meeting memory validation for high-stakes decisions
- React + FastAPI + Dify + OpenAI + Cognee REST

Speaker note:

- BrainSync is for meetings where people say yes too quickly and move on with false confidence.

---

## Slide 2: Problem

**Agreement is not the same as understanding**

- teams approve under pressure
- details get lost while people are coding or multitasking
- the wrong memory becomes the team’s operating truth

Speaker note:

- The core problem is not note-taking. It is memory drift after soft approval.

---

## Slide 3: Product Flow

**What the product does**

1. Input transcript or audio
2. Execute workflow to generate quiz cards
3. Verify memory through interactive questions
4. Review what was right, wrong, and risky

Speaker note:

- The quiz is the key. It checks what people retained, not just what was said.

---

## Slide 4: Current Implementation

**What is implemented now**

- audio upload and Whisper transcription
- workflow execution through Dify
- quiz card interaction
- final review screen with feedback
- Cognee REST search for evidence
- graph rendering in feedback
- fallback graph when native Cognee graph is unavailable

Speaker note:

- This is important for the demo. We are showing the implemented product, not a roadmap-only prototype.

---

## Slide 5: Demo Scenario

**2026 Berlin Hackathon conflict case**

Ground truth:

- maximum 4 team members
- repository must stay public under MIT
- demo is strictly 5 minutes
- both Cognee and Dify must appear

Demo assets:

- audio: `demo_assets/berlin_hackathon_conflict.wav`
- script: `demo_assets/berlin_hackathon_conflict_script.txt`

Speaker note:

- The audience immediately understands these rules, so the demo lands faster.

---

## Slide 6: What Goes Wrong In The Audio

**Three failure modes happen in one conversation**

- a fifth member is suggested for better UI
- the repo is made private “for safety”
- a hallway rumor changes the presentation time

And the team response is weak:

- explicit wrong approval
- silence while distracted
- vague “I got it” confidence

Speaker note:

- This is why a post-meeting quiz matters. The conversation sounds productive, but the retained decisions are dangerous.

---

## Slide 7: Why The Quiz Matters

**A summary shows the meeting. A quiz shows the memory.**

- summary = what was said
- quiz = what the user actually retained
- review = what to fix before execution

Speaker note:

- BrainSync turns passive review into active verification.

---

## Slide 8: Review Screen Value

**The final review is the real product**

It shows:

- right / wrong answers
- why this matters
- what to remember next time
- communication risk
- Cognee search query
- Cognee evidence
- graph visualization

Speaker note:

- The goal is not grading. The goal is better future decisions.

---

## Slide 9: Why Cognee Matters

**Cognee is the grounding layer**

- transcript and context can be ingested by REST
- feedback pulls relevant evidence after the quiz
- graph data is fetched when available
- if native graph data is unavailable, BrainSync builds a fallback graph from query and evidence

Speaker note:

- That fallback matters in demo conditions because tenant graph support can vary.

---

## Slide 10: Architecture

**System split**

Frontend:

- React + Vite
- input, quiz, review, graph rendering

Backend:

- FastAPI
- Whisper transcription
- Dify workflow execution
- Cognee REST integration

Speaker note:

- Keys and API handling stay on the backend. The browser only renders ready-to-use data.

---

## Slide 11: Live Demo Script

1. Upload `demo_assets/berlin_hackathon_conflict.wav`
2. Show transcript result
3. Click `Execute workflow`
4. Let Step 1 and Step 2 auto-collapse
5. Answer one question wrong on purpose
6. Open the final review
7. Show:
   - what was wrong
   - what to remember
   - Cognee evidence
   - graph / fallback graph

Speaker note:

- Keep this under 5 minutes. The product flow is already compact, so the demo should be too.

---

## Slide 12: Closing

**BrainSync Auditor**

Verify memory before miscommunication becomes execution.

Speaker note:

- The pitch is simple: not just what was discussed, but whether the team truly remembered the right thing.
