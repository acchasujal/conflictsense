# ConflictSense UI State Machine

## Research Inputs Used
- research/ConflictSense_UI.jsx

## Frozen Decisions Applied
- Human Approval Gate
- Reasoning Trace phases

## Assumptions
- Standard React state patterns map directly to these UI states.

---

## 1. UI States

### `idle`
- **Trigger:** Application loads.
- **Display:** 7 policy documents visible. "Run Analysis" button enabled.
- **Transitions:** User clicks "Run Analysis" -> `scanning`

### `scanning`
- **Trigger:** "Run Analysis" clicked.
- **Display:** Pulse animation on button. "Analyzing..." text. Trace panel starts streaming steps sequentially. Left panel reveals conflicts progressively.
- **Transitions:** All TraceSteps completed -> `done`

### `done` (Analysis Complete)
- **Trigger:** All TraceSteps rendered.
- **Display:** All ConflictCards visible. "Run Analysis" button changes to "Re-run Analysis".
- **Transitions:** 
  - User selects ConflictCard -> `conflict_selected`
  - User clicks "Re-run Analysis" -> `scanning`

### `conflict_selected` (Review Required)
- **Trigger:** User clicks a specific ConflictCard.
- **Display:** Expands card to show Resolution text, Deadline, and Action buttons (Approve, Reject, Escalate).
- **Transitions:**
  - Click "Approve finding" -> `approved`
  - Click "Mark false positive" -> `rejected`
  - Click "Escalate to legal" -> `escalated`
  - Click another card -> `conflict_selected` (different ID)

### `approved`
- **Trigger:** User clicks "Approve finding".
- **Display:** Card collapses action buttons. Displays `✓ approved` badge and green approval status bar.
- **Transitions:** None (terminal state for the conflict in this UI scope).

### `rejected` (False Positive)
- **Trigger:** User clicks "Mark false positive".
- **Display:** Card collapses action buttons. Displays `false positive` badge and greyed out status.
- **Transitions:** None.

### `escalated`
- **Trigger:** User clicks "Escalate to legal".
- **Display:** Escalation modal/status (Not fully defined in React code, assume visual badge).
- **Transitions:** None.
