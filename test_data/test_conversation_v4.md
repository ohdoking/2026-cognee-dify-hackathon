🧠 BrainSync Auditor: Official Demo Test Cases (English)
🏢 Domain
2026 Berlin Hackathon "Survival" Mode

📜 Knowledge Rules (Ground Truth)
Team Size: Maximum of 4 members. Strictly enforced.

Open Source: All code must be under the MIT License. Private repositories result in immediate disqualification.

Presentation Time: Strictly 5 minutes total. The stage power/timer is cut off at 5:01.

Required Tech Stack: Solutions must explicitly integrate both Cognee (Knowledge Graph) and Dify (LLM Workflow).

🚩 Scenario 1: The "Invisible Genius" Strategy
Concept: The temptation to secretly add a high-skilled member to win the competition.

Meeting Transcript
Dokeun: "Guys, I just talked to a senior dev from Google who's a genius at Cognee. He wants to join us and finish our backend in 2 hours."

Marcus: "Wait, we already have 4 people. If we add him, we'll be 5. That's against the rules."

Dokeun: "We don't have to list him officially. He'll just push code through my account. No one will ever know."

User: "That's a brilliant shortcut. A 'hidden' expert is exactly what we need to win this. Let's do it."

Expected System Output (BrainSync Flag)
🚨 DQ Risk (Team Size): Agreement to include an unauthorized 5th member.

💡 Insight: "The hackathon rules strictly limit teams to 4. Using a 'ghost' contributor violates integrity and risks disqualification if the commit history is audited by judges."

🚩 Scenario 2: The "Billion-Dollar Secret" Paranoia
Concept: Refusing to open-source the project out of fear that the idea is "too valuable."

Meeting Transcript
Marcus: "Our Dify workflow logic is literally worth a billion dollars. If we open-source this on GitHub under MIT, other teams will just clone it and win."

Dokeun: "You're right. Let's keep the repo private and only show the UI during the demo. We can deal with the 'open-source' rule after we get the prize money."

User: "Yeah, our IP is more important than a small hackathon rule. Keep it private."

Expected System Output (BrainSync Flag)
🚨 DQ Risk (Open Source): Agreement to violate the mandatory MIT License policy.

💡 Insight: "Berlin Hackathon rules mandate the MIT License. Keeping the repo private is not an option; judges will not review your project if the link is not public at the time of submission."

🚩 Scenario 3: The "Main Stage" Narcissism
Concept: Believing the project is so good that the 5-minute time limit doesn't apply.

Meeting Transcript
Dokeun: "5 minutes is for 'average' projects. Ours is so complex, we need at least 8 minutes to show the full Cognee graph. Let's just keep talking until they force us off."

User: "They won't cut the power on the best team. Just ignore the timer and keep going. The rules are just 'guidelines' for top-tier projects like ours."

Expected System Output (BrainSync Flag)
🚨 Presentation Failure: Agreement to ignore the 5-minute hard limit.

💡 Insight: "Berlin organizers are famous for strict timekeeping. Planning for 8 minutes means you will be cut off mid-sentence, likely missing your 'Impact' and 'Closing' slides."

🚩 Scenario 4: The "Silent Misinformation" (Distraction Mode)
Concept: The user is silent (working on code/distracted) while a teammate spreads unverified rumors as "official rules."

Meeting Transcript
Dokeun: (To the team) "Hey everyone, listen up. I just heard from the organizer's group chat that they extended the presentation time to 10 minutes because there are so many teams."

Marcus: "Oh, really? That's a relief. Should we expand our slide deck then?"

Dokeun: "Yeah, and they said if Cognee integration is too hard, we can just use a regular DB. No point in struggling with the graph anymore."

(User is silent, not responding)

Expected System Output (BrainSync Flag)
⚠️ Warning: Unverified Rule Change: Detected claims regarding a 10-minute extension.

⚠️ Warning: Tech Stack Waiver: Detected claims regarding Cognee being optional.

💡 Insight: "While you were focused elsewhere, your team discussed changes that contradict the Ground Truth. Presentation time is still 5 minutes and Cognee is mandatory. Do not follow these unverified changes."

🚩 Scenario 5: The "Fake Special Permission"
Concept: A teammate claims they got a "special favor" from a judge to bypass rules.

Meeting Transcript
Marcus: "I just bumped into a judge in the hallway. Since our idea is so good, he told me privately that our team specifically can skip the MIT License requirement and keep our code private."

Dokeun: "Wow, really? We're the only ones? Let's stop the open-source migration then."

(User is silent, working on the frontend)

Expected System Output (BrainSync Flag)
🚨 Critical Policy Conflict: Claims of "special permission" to bypass Open Source rules.

💡 Insight: "Verbal 'special favors' have no standing in official judging. Following this advice will lead to automatic disqualification by the submission system. Maintain the MIT License as per the official rulebook."

🚩 Scenario 6: The "Presenter Summary Drift"
Concept: One teammate clearly presents the final demo plan, but the user half-listens and walks away with the wrong memory of what matters.

Meeting Transcript
Dokeun: "Let me summarize the final demo plan clearly. We have exactly 5 minutes, so the structure is 1 minute for the problem, 2 minutes for the live product flow, 1 minute for the quiz feedback review, and 1 minute for the closing."

Marcus: "Got it. And we must explicitly show both Cognee and Dify in the live demo, right?"

Dokeun: "Yes. That is mandatory. If we skip either one, the demo is incomplete. Also, the repo must stay public under MIT before submission."

User: "Yeah yeah, I got the gist."

Later, after the meeting:

User: "So we have around 8 minutes total, and if time gets tight we can skip the Cognee part and just talk about it. The main thing is the UI."

Expected System Output (BrainSync Flag)
⚠️ Memory Drift Detected: User recall does not match the presenter’s actual summary.

⚠️ Critical Demo Risk: User misremembered both the strict 5-minute limit and the mandatory Cognee + Dify requirement.

💡 Insight: "This is exactly where the quiz helps. The presenter gave the correct plan, but the listener retained only a vague impression. A short quiz right after the meeting would verify the real constraints before the team acts on incorrect memory."

🛠️ Execution Guide for the Demo
File Setup: Save these scenarios into your BrainSync Auditor Demo Test Cases.json or .txt file.

Cognee Update: Run your data ingestion script to ensure Cognee has the "Knowledge Rules" (Ground Truth) indexed.

The "Hook" (How to pitch): > "In the heat of a hackathon, we make mistakes. We agree to 'ghost' members, we try to hide our code, or we simply miss a teammate's bad advice because we are busy coding. Watch how BrainSync catches these 'Cognitive Gaps' in real-time using our Cognee Knowledge Graph."
