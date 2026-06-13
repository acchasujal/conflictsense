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

## ⏱️ 3-Minute Demo Script

**[Screen recording: Chrome, 1920×1080, conflictsense.vercel.app, incognito mode.]**

---

**[0:00–0:15]** *Screen: Idle state. Document grid visible. No narration yet. Let the UI sit for 2 seconds. Then speak.*

> "There's a company called Nexora. And they've done everything right, at least on paper. Seven policy documents. A compliance team. A legal review cycle. And a promise they made to every single employee:
>
> *'If you see something wrong, you can report it. Anonymously. We will never know it was you.'*"

---

**[0:15–0:28]** *Action: Click "Whistleblower Anonymity Conflict" in the scenario dropdown. Click Run Analysis. Do not narrate during the click.*

*[Pause 3 seconds as the analysis begins.]*

> "ConflictSense reads their policies. All of them. Not to summarize them. To find whether the promises inside them can actually be kept."

---

**[0:28–0:52]** *Screen: Agent cards begin appearing in the left panel one by one. Each card shows a conclusion sentence — not a loading spinner. Let the first two agent cards arrive before continuing.*

> "Five agents work through the documents in sequence. Each one checks whether the obligations in one policy can coexist with the obligations in another — for the same employee, at the same company.
>
> A data residency gap appears. Expected. The kind of thing every compliance audit finds."

*[First conflict card arrives — DPDP. 2-second pause.]*

> "Then something else."

*[Second conflict card arrives with ⚡ badge. 4 full seconds of silence.]*

---

**[0:52–1:22]** *Action: Click the ⚡ conflict card to expand it. The side-by-side contradiction view opens. Left panel: Whistleblower Policy §4.2, text highlighted in green. Right panel: IT Security Policy §12.1, text highlighted in red.*

*[Read the citations aloud, slowly.]*

> "Whistleblower Policy. Section 4.2. *'Employee identity is never logged or traceable by any internal party. The ethics portal does not capture IP addresses, session tokens, device identifiers, or any metadata that could be used to identify the reporter.'*
>
> IT Security Policy. Section 12.1. *'All system access is logged with full user identity for security audit purposes. No exceptions permitted. Logs are retained for a minimum of seven years.'*
>
> These two policies cannot both be true. For the same employee. On the same network.
>
> Nexora's anonymity guarantee has never been technically possible. Every report they received was traceable. And nobody knew."

*[Hold on the expanded card for 3 seconds. No narration.]*

---

**[1:22–1:45]** *Action: Click "Request Legal Review." Modal opens, pre-filled with the conflict title and severity. Complete the form and click Submit. Governance ticket injects into the reasoning trace timeline.*

> "No system takes action on its own. The finding goes to a human. A legal review is opened. The ticket is logged in the audit trail.
>
> The employees who filed those reports — they deserve to know that the protection failed. And the people responsible deserve to fix it before the next report comes in."

---

**[1:45–2:10]** *Action: Click the Accessibility Demo toggle in the header. Keyboard shortcuts overlay appears. Navigate one conflict card using only Tab and Enter.*

> "One more thing. The employees most at risk from a policy like this — the ones most likely to need an anonymous reporting channel — are often the same employees who need accessibility tools to use any tool at all.
>
> ConflictSense is built for them. Screen reader announcements. Keyboard navigation. No mouse required. The protection should reach everyone it's meant to protect."

---

**[2:10–2:45]** *Action: Switch to the upload tab. Show the interface. If abstention is available, show it. If not, hold on the architecture diagram or the upload interface briefly.*

> "The demo scenarios you've seen are pre-validated runs — real pipeline output, replayed reliably so nothing breaks during judging. For live documents, the pipeline connects to Azure AI Search. Hybrid retrieval, semantic ranking, grounded citations.
>
> When it finds something, it cites the exact line. When it doesn't find enough to be certain, it says so. It doesn't guess."

---

**[2:45–3:00]** *Action: Return to the expanded anonymity conflict card. Hold on the citation highlighting.*

> "I built this alone, in ten days, because I kept thinking about that employee. The one who trusted the promise. The one who reported something — a safety issue, a financial irregularity, someone above them abusing power — and who believed, the whole time, that no one would ever know it was them.
>
> ConflictSense exists so that someone checks whether that belief is actually true."

*[Hold 3 seconds. Fade. conflictsense.vercel.app visible in the final frame.]*

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
