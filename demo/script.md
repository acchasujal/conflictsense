# ConflictSense Hackathon Demo Script

## 1. Introduction (1 min)
- **Speaker:** "Welcome to ConflictSense. As enterprises grow, their policy documents become massive and inherently contradictory. Human compliance teams cannot manually cross-reference 1000-page documents to find structural impossibilities."
- **Visual:** Show the ConflictSense Landing Page.

## 2. Live Document Analysis (2 mins)
- **Speaker:** "We have 7 synthetic enterprise policy documents from Nexora. Let's run the analysis."
- **Action:** Click "Run Analysis".
- **Visual:** Show the progress bar streaming Server-Sent Events (SSE) live from the backend.
- **Speaker:** "ConflictSense is using Azure Foundry IQ under the hood. It parallelizes the document search to rapidly find contradictions."

## 3. Reviewing Conflicts (1.5 mins)
- **Speaker:** "Here are the detected conflicts. Notice that these aren't simple keyword overlaps; they are logical impossibilities."
- **Action:** Expand the "Whistleblower Anonymity vs. IT Security Logging" conflict.
- **Speaker:** "The Whistleblower policy guarantees total anonymity, but the IT Security policy mandates full identity logging. This is a severe compliance risk that a keyword search would miss."

## 4. Reliability and Fallback (1 min)
- **Speaker:** "What happens if Azure goes down? ConflictSense has an automated mock fallback."
- **Action:** Show the "Mock Mode" indicator or simulate an API failure to trigger Tier 3.
- **Speaker:** "The system instantly falls back to a pre-computed mock trace, ensuring the demo and system resilience are uninterrupted."

## 5. Conclusion (0.5 mins)
- **Speaker:** "ConflictSense brings true reasoning to compliance, saving hundreds of hours and averting regulatory fines. Thank you."
