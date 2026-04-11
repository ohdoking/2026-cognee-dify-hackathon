# BrainSync Auditor Presentation

## Slide 1: Title

**BrainSync Auditor**

Turn meeting agreement into verified understanding.

Subtitle:

- Meeting memory validation for high-stakes decisions
- Built with React, FastAPI, Dify, OpenAI, and Cognee

Speaker note:

- BrainSync Auditor is designed for moments when people say “yes” in meetings without fully validating what that “yes” implies.

---

## Slide 2: The Problem

**Teams often confuse agreement with understanding**

- Meetings move fast.
- People approve decisions under pressure.
- Wrong approvals create compliance risk, project delay, and broken trust.

Examples:

- approving the wrong database
- approving the wrong data residency decision
- approving a delay without the required escalation

Speaker note:

- The real problem is not only bad decisions. It is false confidence in shared understanding.

---

## Slide 3: What BrainSync Does

**BrainSync Auditor checks whether people actually remember the right rules**

It helps teams:

- input a transcript or recording
- run workflow-based policy analysis
- generate quiz cards from the meeting
- review what was remembered correctly
- learn what was misunderstood and why

Speaker note:

- This turns passive meeting review into active verification.

---

## Slide 4: Core Workflow

**Three-step user flow**

1. `Input`
   Paste transcript text, upload a file, or record audio.
2. `Execute workflow`
   The backend sends the transcript through the Dify workflow.
3. `Interactive quiz + review`
   Users answer quiz cards, then receive a summary of correct and incorrect memory.

Speaker note:

- The product is intentionally simple. The value is in the review loop after the quiz.

---

## Slide 5: Why The Quiz Matters

**A meeting summary is not enough**

- Summaries only show what was said.
- Quiz interaction shows what people actually retained.
- BrainSync identifies the gap between:
  - what the team approved
  - what policy actually required

Speaker note:

- This is the difference between documentation and verification.

---

## Slide 6: After The Quiz

**Post-quiz review is the real product value**

BrainSync shows:

- what you got right
- what you got wrong
- the correct answer
- why it matters
- what to remember next time
- communication risk if the wrong approval had been acted on

Speaker note:

- We are not only grading people. We are coaching them to avoid future miscommunication.

---

## Slide 7: Demo Scenario

**2026 Berlin Hackathon survival mode**

Ground truth:

- team size max 4
- repository must stay public under MIT
- presentation is strictly 5 minutes
- both Cognee and Dify must be shown

Demo asset:

- audio: `demo_assets/berlin_hackathon_conflict.wav`
- script: `demo_assets/berlin_hackathon_conflict_script.txt`

Speaker note:

- This scenario is stronger than a generic policy demo because the audience can instantly understand the stakes.

---

## Slide 8: Demo Failure Case

**What happens in the audio**

- Marcus suggests adding a fifth member for better UI
- User agrees immediately
- Dokeun suggests making the repo private
- User agrees again
- Marcus introduces an unverified 10-minute rumor
- Dokeun and User are distracted and do not challenge it

**What BrainSync should catch**

- team size violation
- MIT/public repo violation
- presentation-time misinformation
- false confidence caused by distraction and soft approvals

Speaker note:

- This is the exact value proposition: the conversation sounds productive, but the retained decisions are dangerous.

---

## Slide 9: Why This Demo Works

**The audience sees three failure types at once**

- explicit wrong approval
- unverified rule adoption
- silent memory drift while someone is distracted

Result:

- BrainSync can generate quiz checks immediately after the meeting
- the review screen explains what was wrong and what to remember next time

Speaker note:

- This makes the product feel practical, not theoretical.

---

## Slide 10: Product Experience

**UI flow**

- clean transcript input stage
- workflow execution stage
- interactive quiz cards
- final expandable review cards
- Cognee-backed context and graph area in feedback

**Review UX**

- right / needs review status
- expandable detail per question
- revisit card action

Speaker note:

- The final review is designed for demo clarity and team reflection, not just raw output.

---

## Slide 11: System Architecture

**Frontend**

- React + Vite
- transcript review
- quiz interaction
- final results and coaching

**Backend**

- FastAPI
- OpenAI Whisper transcription
- Dify workflow execution

**Knowledge Layer**

- Cognee for project policy and context grounding

Speaker note:

- The browser handles UX. Sensitive keys stay on the backend.

---

## Slide 12: Why Cognee Matters

**Cognee is the grounding layer for the review**

It supports:

- transcript and context ingestion
- relevant evidence retrieval after the quiz
- comparison between what the user remembered and what the source of truth says
- graph-style visualization in the feedback session

Speaker note:

- Dify creates the quiz flow. Cognee makes the explanation and evidence layer trustworthy.

---

## Slide 13: What Makes This Different

**BrainSync is not just another note-taking tool**

It focuses on:

- decision accuracy
- memory verification
- compliance-sensitive communication
- preventing wrong approvals before they become execution

Speaker note:

- Most tools help you record meetings. BrainSync helps you validate whether the team truly understood them.

---

## Slide 14: Target Use Cases

**Where this is valuable**

- compliance reviews
- architecture meetings
- legal and policy alignment
- project launch decisions
- regulated internal operations

Speaker note:

- Any environment with expensive consequences for a casual “yes” is a good fit.

---

## Slide 15: Demo Flow Recommendation

**Suggested live demo sequence**

1. Show a clean compliant meeting
2. Show a subtle exception mistake
3. Show a major failure case
4. Show the final review screen

What to emphasize:

- actual meeting decision
- expected policy-correct answer
- what the user remembered wrong
- how BrainSync coaches the next better response

---

## Slide 16: Future Roadmap

**Next steps**

- Cognee-backed explanation per wrong answer
- stronger final summary with learning trends
- user/team memory analytics over time
- approval-risk scoring by meeting
- integration with meeting platforms

Speaker note:

- The current prototype proves the interaction model. The next step is deeper contextual feedback and long-term memory improvement.

---

## Slide 17: Closing

**BrainSync Auditor**

From “I think that sounds right” to “I know this decision is aligned.”

Closing line:

- We help teams verify memory before miscommunication becomes execution.
