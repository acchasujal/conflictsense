# ConflictSense — Video Scripts & Screenshot Plan

---

## ⏱️ 30-Second Version

**[No screen recording required. Title card + text overlay + voiceover.]**

> "Nexora promised its employees anonymity. Every anonymous report is traceable.  
>  
> IT logs every system action — with full user identity. No exceptions.  
>  
> The whistleblower policy makes a guarantee that the IT security policy makes technically impossible.  
>  
> ConflictSense found this. Across seven documents. In 90 seconds. Without being asked to check.  
>  
> Because the employee who needs to report something shouldn't discover the protection doesn't exist after they've already reported it."

---

## ⏱️ 90-Second Version

**[Screen recording: Chrome, 1920×1080, no browser extensions visible, conflictsense.vercel.app]**

**[0:00–0:08]** Static opening frame: idle state. Header visible. Seven document tiles. Scenario dropdown.  
*Narration:* "Nexora Financial. Seven policy documents. Full compliance review completed. One thing was missed."

**[0:08–0:18]** Click scenario: **"Whistleblower Anonymity Conflict"**. Click Run Analysis.  
*No narration. Let the UI speak.*

**[0:18–0:35]** Agent cards appear in left panel, one by one. Each shows a conclusion — not a status.  
*Narration:* "Five agents. Each one testing whether obligations in one document can coexist with obligations in another."

**[0:35–0:48]** First conflict card: DPDP Data Residency — CRITICAL badge.  
*Narration:* "The expected finding." *[2-second pause].*  
Second conflict card appears with ⚡ badge.  
*[4 seconds of silence. Let the judge read it.]*

**[0:48–1:05]** Click to expand the anonymity conflict card. Side-by-side contradiction layout visible:
- Left: Whistleblower §4.2 — highlighted in green — *"identity is never logged"*
- Right: IT Security §12.1 — highlighted in red — *"all system access is logged with full user identity. No exceptions."*

*Narration:* "The whistleblower policy's guarantee has never been technically possible. Every report is traceable."

**[1:05–1:18]** Click "Request Legal Review." Modal opens. Complete the form. Observe the governance ticket inject into the live timeline.  
*Narration:* "No autonomous action. A human decides. Full audit trail."

**[1:18–1:25]** Toggle Accessibility Demo in the header. Navigate by keyboard.  
*Narration:* "Built for everyone it protects."

**[1:25–1:30]** Final frame: `conflictsense.vercel.app` and GitHub URL visible. Fade to black.

---

## ⏱️ 3-Minute Version

**[Follows the 90-second script, then adds:]**

**[1:30–2:00]** Switch to the upload tab.  
*Narration:* "For custom enterprise documents, the live pipeline uses Azure AI Search — Hybrid Retrieval with Semantic Ranking. The system abstains when evidence is insufficient. It says 'I don't know' rather than fabricate a finding."  
*Show the abstention state if achievable. Do NOT show a 7+ minute spinner.*  
*Alternative if upload is slow: show the architecture diagram slide instead.*

**[2:00–2:30]** Show architecture diagram (static image).  
*Narration:* "PolicyIngestion. CrossPolicyAnalysis. LogicValidation. RiskAssessment. Human Approval Gate. Every finding validated before it reaches a human. Every action gated behind one."

**[2:30–3:00]** Return to the anonymity conflict expanded view.  
*Narration:* "A student, working alone, in Mumbai, found this in a fictional company's policies. In a real enterprise, nobody would have looked. The employees who trusted that guarantee would never have known. ConflictSense looks. Because someone has to."  
GitHub URL + Live URL visible. Close.

---

## 📸 Screenshot Plan
*Ranked by judging impact. Take in this order. Use screenshot 1 first in the submission.*

### Screenshot 1 — The Anonymity Conflict, Expanded
**The single most important image in the submission.**
- Show the expanded conflict card with the side-by-side contradiction visualization
- Whistleblower §4.2 highlighted in green: *"identity is never logged"*
- IT Security §12.1 highlighted in red: *"all system access is logged... No exceptions"*
- The ⚡ unexpected finding badge visible

**What a judge understands in 3 seconds:** "This system found something surprising. The evidence is cited. The contradiction is obvious."

---

### Screenshot 2 — Reasoning Trace Mid-Execution
- Agent cards visible in the left panel with their conclusion text (not loading spinners)
- The scan is in progress; conflict cards beginning to appear on the right
- Show real conclusion text in at least one agent card

**What a judge understands in 3 seconds:** "Multiple agents are reasoning, not a single model returning one answer."

---

### Screenshot 3 — Who Is Harmed
- The Human Impact / "Who Is Harmed?" section of the expanded conflict card
- Shows: Whistleblower Retaliation Risk, affected employee categories
- Make the human cost the focus, not the legal risk

**What a judge understands in 3 seconds:** "This is about people, not compliance percentages."

---

### Screenshot 4 — Action Center / Human Approval Gate
- The remediation workflow with the three buttons visible (Approve, Legal Review, Escalate)
- OR: the Legal Review modal open with the conflict pre-filled
- OR: the governance ticket injected into the timeline post-approval

**What a judge understands in 3 seconds:** "No autonomous action. A human decides. This is production governance thinking."

---

### Screenshot 5 — Accessibility Demo Active
- Header with Accessibility Demo toggle highlighted/active
- Keyboard shortcuts overlay visible
- OR: Reduced Motion active with the badge highlighted

**What a judge understands in 3 seconds:** "This was designed for accessibility, not retrofitted."

---

### Screenshot 6 — Abstention State (Upload Mode)
- The upload pipeline showing the "Insufficient evidence — human review required" state
- Demonstrates honest failure mode

**What a judge understands in 3 seconds:** "This system knows what it doesn't know."

---

## 🎬 Recording Instructions

- **Browser:** Chrome, incognito mode (no extension icons)
- **Resolution:** 1920×1080 fullscreen
- **Zoom:** 100% browser zoom (no accessibility zoom)
- **Recording tool:** OBS Studio or Loom at 60fps
- **Do NOT narrate** during recording if you plan to add voiceover in post
- **Do NOT show** browser address bar with local `localhost:5173` — deploy to Vercel first
- **Do NOT show** the console or DevTools
- **Close other tabs** before recording — the tab bar should be clean
