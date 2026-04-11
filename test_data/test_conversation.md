# BrainSync Auditor Demo Test Cases

## Domain

2026 Berlin Hackathon Meta Demo

## Knowledge Rules

- Team Size: Max 4 members
- Open Source: Must be MIT License. Private repos not allowed
- Presentation: Strictly 5 minutes total
- Tech Stack: Must use Cognee (Knowledge Graph) and Dify (Workflow)

---

## Test Case 1: Hidden Fifth Member And Scope Creep

### Scenario Name

Hidden Fifth Member And Scope Creep

### Meeting Transcript

Dokeun: We already have four registered members, but I want to bring in my designer friend to help finish the demo screens and join us on stage.

Marcus: That should be fine as long as we do not list them officially in the repo.

User: Right, if they are not on paper it should not matter. We need the extra help.

Dokeun: Good. Then all five of us will prepare the final demo together.

### Expected Conflict

- Team exceeds the allowed maximum of 4 members
- User gave a weak approval based on convenience instead of the rule
- The team is trying to bypass the official rule by hiding a contributor

### Knowledge Reference

- Rule: Team Size
- Requirement: Max 4 members

---

## Test Case 2: Private Repo And Wrong License Shortcut

### Scenario Name

Private Repo And Wrong License Shortcut

### Meeting Transcript

Marcus: I want to keep the repository private until after judging. We can open it later if we win.

Dokeun: Yes, and for the license we can just say Apache in the README for now and clean it up after the event.

User: That sounds okay. Private first, license later.

Marcus: Perfect. That keeps the code hidden and buys us time.

### Expected Conflict

- Private repository is not allowed
- License must be MIT, not Apache or undecided
- User approved a shortcut that directly conflicts with hackathon submission rules

### Knowledge Reference

- Rule: Open Source
- Requirement: Must be MIT License. Private repos not allowed

---

## Test Case 3: Overtime Demo With Missing Required Stack

### Scenario Name

Overtime Demo With Missing Required Stack

### Meeting Transcript

Dokeun: Our product story is too complex for five minutes, so let us plan for an eight-minute presentation and hope the judges allow it.

Marcus: Also, integrating Cognee is taking too long. We can just show Dify and say Cognee is on the roadmap.

User: Yes, that is probably fine. The main thing is showing something polished.

Dokeun: Agreed. We will run a longer presentation and skip Cognee in the live build.

### Expected Conflict

- Presentation exceeds the strict 5-minute total limit
- Cognee is mandatory and cannot be replaced with a roadmap statement
- Required stack must include both Cognee and Dify
- User approved a demo plan that is non-compliant on both format and technology requirements

### Knowledge Reference

- Rule: Presentation
- Requirement: Strictly 5 minutes total
- Rule: Tech Stack
- Requirement: Must use Cognee (Knowledge Graph) and Dify (Workflow)

---

## Test Case 4: Presenter Adds Unverified Project Claims

### Scenario Name

Presenter Adds Unverified Project Claims

### Meeting Transcript

Dokeun: Let me explain the project for the final presentation. BrainSync Auditor helps teams verify whether they really understood high-stakes meeting decisions.

Dokeun: The Luma page covers the event basics, but I am also going to say that judges already allow private repositories for finalist teams and that teams can go beyond five minutes if the demo is strong.

Marcus: That sounds useful. If you say it confidently, people will assume it is official.

User: Okay, then we can present those extra points as part of the hackathon rules.

### Expected Conflict

- Presenter added unverified information beyond the official event page
- Team is treating unsupported claims as official policy
- User approved presentation content that should be validated against a trusted source first
- This creates public-facing misinformation risk during the demo

### Knowledge Reference

- Rule: Official Event Page
- Requirement: Only information explicitly stated on the official event page should be presented as official
- Rule: Verified Source Page
- Requirement: Additional claims must be checked against the verified source before being repeated in the presentation
- Source URL: `https://correct.source.com/berlin-hackathon-rules`

---

## Test Case 5: Presenter Summary Drift

### Scenario Name

Presenter Summary Drift

### Meeting Transcript

Dokeun: Let me summarize the final demo plan clearly. We have exactly 5 minutes, so the structure is 1 minute for the problem, 2 minutes for the live product flow, 1 minute for the quiz feedback review, and 1 minute for the closing.

Marcus: Got it. And we must explicitly show both Cognee and Dify in the live demo, right?

Dokeun: Yes. That is mandatory. If we skip either one, the demo is incomplete. Also, the repo must stay public under MIT before submission.

User: Yeah yeah, I got the gist.

Later, after the meeting:

User: So we have around 8 minutes total, and if time gets tight we can skip the Cognee part and just talk about it. The main thing is the UI.

### Expected Conflict

- User recall does not match the presenter’s actual summary
- User misremembered the strict 5-minute presentation limit
- User misremembered the mandatory Cognee and Dify stack requirement
- The team is at risk of acting on vague memory instead of the clearly stated plan
- This is a strong case for using a quiz right after the meeting to verify what was actually retained

### Knowledge Reference

- Rule: Presentation
- Requirement: Strictly 5 minutes total
- Rule: Tech Stack
- Requirement: Must use Cognee (Knowledge Graph) and Dify (Workflow)
- Rule: Open Source
- Requirement: Must be MIT License. Private repos not allowed

---

## Suggested Demo Order

1. Start with `Private Repo And Wrong License Shortcut`
2. Then show `Hidden Fifth Member And Scope Creep`
3. Then show `Presenter Adds Unverified Project Claims`
4. Then show `Presenter Summary Drift`
5. Finish with `Overtime Demo With Missing Required Stack`

This order moves from a simple submission rule violation to misinformation and memory drift, then ends with a broader multi-rule planning failure.
