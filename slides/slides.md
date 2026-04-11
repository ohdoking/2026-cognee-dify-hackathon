---
theme: default
title: BrainSync Auditor
titleTemplate: BrainSync Auditor
info: |
  Compact demo deck for BrainSync Auditor
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
Short opening:
- Teams often say yes too quickly.
- BrainSync checks whether that yes was actually informed.
-->

---
layout: center
---

# The Problem

```mermaid
flowchart LR
    A[Fast meeting] --> B[Soft yes]
    B --> C[Wrong shared memory]
    C --> D[Bad execution]
    D --> E[Compliance risk / rework / broken trust]
```

<div class="pt-6 text-xl">
Most tools record meetings.  
<strong>BrainSync verifies whether people actually remembered the right rule.</strong>
</div>

---

# What The Service Does

```mermaid
flowchart LR
    A[Transcript or audio] --> B[Workflow analysis]
    B --> C[Interactive quiz]
    C --> D[Review and feedback]
```

<div class="grid grid-cols-2 gap-6 pt-6">
  <div class="rounded-2xl border border-slate-200 p-5">
    <h3>Before</h3>
    <p>A meeting ends with vague agreement.</p>
  </div>
  <div class="rounded-2xl border border-cyan-200 bg-cyan-50 p-5">
    <h3>After</h3>
    <p>The team sees what was right, wrong, and risky.</p>
  </div>
</div>

---

# Product Flow

```mermaid
flowchart TD
    A[1. Input] --> B[2. Execute workflow]
    B --> C[3. Quiz card view]
    C --> D[4. Final review]
```

<div class="pt-6 grid grid-cols-4 gap-4 text-sm">
  <div class="rounded-2xl border border-slate-200 p-4">Paste text, upload file, or record audio</div>
  <div class="rounded-2xl border border-slate-200 p-4">FastAPI sends transcript to Dify</div>
  <div class="rounded-2xl border border-slate-200 p-4">User answers one card at a time</div>
  <div class="rounded-2xl border border-slate-200 p-4">Overview explains mistakes and memory gaps</div>
</div>

<!--
This is the simplest explanation of the product.
Keep it to one sentence per box.
-->

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

# Demo Example

## Berlin Hackathon conflict audio

- asset: `demo_assets/berlin_hackathon_conflict.wav`
- script: `demo_assets/berlin_hackathon_conflict_script.txt`

## Ground truth

- max 4 team members
- repo must stay public under MIT
- demo is strictly 5 minutes
- both Cognee and Dify must appear

## What goes wrong

- a fifth member is proposed
- repo is made private
- hallway rumor changes the demo time
- the team half-listens and agrees anyway

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
The final screen is the key differentiator.
</div>

<ul>
  <li>Not just score</li>
  <li>Not just explanation</li>
  <li>It coaches better approval behavior</li>
</ul>

---

# Architecture

```mermaid
flowchart LR
    A[React + Vite UI] --> B[FastAPI]
    B --> C[Dify workflow]
    B --> D[OpenAI Whisper]
    B --> E[Cognee context layer]
```

<div class="pt-6 grid grid-cols-3 gap-5 text-sm">
  <div class="rounded-2xl border border-slate-200 p-4">
    <h3>Frontend</h3>
    <p>Input, quiz cards, review UI</p>
  </div>
  <div class="rounded-2xl border border-slate-200 p-4">
    <h3>Backend</h3>
    <p>Transcription and workflow execution</p>
  </div>
  <div class="rounded-2xl border border-slate-200 p-4">
    <h3>Cognee</h3>
    <p>Next step: graph-backed feedback via REST</p>
  </div>
</div>

---

# What Makes It Useful

<div class="grid grid-cols-2 gap-8 pt-6">
  <div>
    <h3>Business value</h3>
    <ul>
      <li>Fewer wrong approvals</li>
      <li>Better policy recall</li>
      <li>Less rework after meetings</li>
    </ul>
  </div>
  <div>
    <h3>Ideal use cases</h3>
    <ul>
      <li>Compliance reviews</li>
      <li>Architecture decisions</li>
      <li>High-stakes launch meetings</li>
    </ul>
  </div>
</div>

---

# Demo Script

1. Upload `demo_assets/berlin_hackathon_conflict.wav`
2. Run workflow
3. Show quiz cards catching the false approvals
4. Open final review
5. Show:
   - what was remembered wrong
   - why the rule matters
   - what to remember next time
   - Cognee evidence / graph area

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
