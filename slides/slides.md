---
theme: default
title: BrainSync Auditor
titleTemplate: BrainSync Auditor
info: |
  Demo deck aligned with the current implementation
class: text-left
drawings:
  persist: false
transition: slide-left
mdc: true
colorSchema: auto
layout: cover
background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 48%, #22d3ee 100%)
---

# BrainSync Auditor

Turn meeting agreement into verified understanding.

<div class="pt-6 text-lg opacity-90">
Catch false confidence before it becomes execution.
</div>

<!--
Opening:
- People say yes in meetings very easily.
- BrainSync checks whether that yes was actually informed.
-->

---
layout: center
---

# The Problem

```mermaid
flowchart LR
    A[Fast meeting] --> B[Soft approval]
    B --> C[Wrong shared memory]
    C --> D[Bad execution]
    D --> E[Compliance risk / rework / broken trust]
```

<div class="pt-6 text-xl">
Most tools record meetings.  
<strong>BrainSync verifies what people actually remembered.</strong>
</div>

---

# Current Product Flow

```mermaid
flowchart TD
    A[1. Input transcript or audio] --> B[2. Execute workflow]
    B --> C[3. Interactive quiz cards]
    C --> D[4. Final review and feedback]
```

<div class="pt-6 grid grid-cols-4 gap-4 text-sm">
  <div class="rounded-2xl border border-slate-200 p-4">Whisper turns audio into transcript</div>
  <div class="rounded-2xl border border-slate-200 p-4">Dify returns quiz questions from the conversation</div>
  <div class="rounded-2xl border border-slate-200 p-4">User answers one question at a time</div>
  <div class="rounded-2xl border border-cyan-200 bg-cyan-50 p-4">Review explains what was wrong and what to remember</div>
</div>

---

# Why Quiz Instead Of Summary

<div class="grid grid-cols-2 gap-8 pt-6">
  <div class="rounded-2xl border border-slate-200 p-6">
    <h3>Summary</h3>
    <ul>
      <li>What was said</li>
      <li>Passive review</li>
      <li>Easy to miss wrong assumptions</li>
    </ul>
  </div>
  <div class="rounded-2xl border border-cyan-200 bg-cyan-50 p-6">
    <h3>BrainSync</h3>
    <ul>
      <li>What was retained</li>
      <li>Active verification</li>
      <li>Exposes false confidence quickly</li>
    </ul>
  </div>
</div>

---

# Demo Scenario

## Berlin Hackathon conflict audio

- `demo_assets/berlin_hackathon_conflict.wav`
- `demo_assets/berlin_hackathon_conflict_script.txt`

## Ground truth

- max 4 team members
- repo must stay public under MIT
- demo is strictly 5 minutes
- both Cognee and Dify must appear

---

# What Goes Wrong

<div class="grid grid-cols-3 gap-5 pt-6 text-sm">
  <div class="rounded-2xl border border-slate-200 p-5">
    <h3>Wrong approval</h3>
    <p>A fifth member is accepted to improve the UI.</p>
  </div>
  <div class="rounded-2xl border border-slate-200 p-5">
    <h3>Risky shortcut</h3>
    <p>The repository is made private “for safety.”</p>
  </div>
  <div class="rounded-2xl border border-slate-200 p-5">
    <h3>Memory drift</h3>
    <p>A hallway rumor changes the presentation time.</p>
  </div>
</div>

<div class="pt-6 text-lg">
The conversation sounds efficient.  
<strong>The retained decisions are dangerous.</strong>
</div>

---

# Review Screen Value

```mermaid
flowchart LR
    A[User answer] --> B[Right / Wrong]
    B --> C[Why it matters]
    C --> D[What to remember next time]
    D --> E[Lower communication risk]
```

<div class="pt-6">
The final review is the product differentiator.
</div>

<ul>
  <li>Not just a score</li>
  <li>Not just an explanation</li>
  <li>It coaches better decision behavior</li>
</ul>

---

# Why Cognee Matters

```mermaid
flowchart LR
    A[Transcript / context] --> B[Cognee REST]
    B --> C[Relevant evidence]
    C --> D[Graph or fallback graph]
    D --> E[Feedback screen]
```

<div class="pt-6 grid grid-cols-2 gap-6 text-sm">
  <div class="rounded-2xl border border-slate-200 p-5">
    <h3>Native graph path</h3>
    <p>Use dataset_id from search response, then fetch dataset graph.</p>
  </div>
  <div class="rounded-2xl border border-cyan-200 bg-cyan-50 p-5">
    <h3>Fallback graph path</h3>
    <p>If native graph is unavailable, BrainSync builds a graph from query, answer, and evidence.</p>
  </div>
</div>

---

# Architecture

```mermaid
flowchart LR
    A[React + Vite] --> B[FastAPI]
    B --> C[OpenAI Whisper]
    B --> D[Dify workflow]
    B --> E[Cognee REST]
```

<div class="pt-6 grid grid-cols-3 gap-5 text-sm">
  <div class="rounded-2xl border border-slate-200 p-4">
    <h3>Frontend</h3>
    <p>Input, quiz cards, review, graph rendering</p>
  </div>
  <div class="rounded-2xl border border-slate-200 p-4">
    <h3>Backend</h3>
    <p>Transcription, workflow calls, Cognee integration</p>
  </div>
  <div class="rounded-2xl border border-slate-200 p-4">
    <h3>Security</h3>
    <p>Keys and API handling stay on the server</p>
  </div>
</div>

---

# Live Demo Script

1. Upload `demo_assets/berlin_hackathon_conflict.wav`
2. Show the transcript
3. Click `Execute workflow`
4. Let Step 1 and Step 2 auto-collapse
5. Answer one question wrong on purpose
6. Open the final review
7. Show:
   - what was wrong
   - what to remember
   - Cognee evidence
   - graph or fallback graph

<div class="pt-6 text-lg">
Message to audience:  
<strong>BrainSync turns “I think that sounds right” into “I know this decision is aligned.”</strong>
</div>

---
layout: end
background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 48%, #22d3ee 100%)
---

# BrainSync Auditor

Verify memory before miscommunication becomes execution.
