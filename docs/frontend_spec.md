# ConflictSense Frontend Specification

## Research Inputs Used
- research/ConflictSense_UI.jsx
- research/Pasted text(47).txt

## Frozen Decisions Applied
- Two-panel layout.
- Human Approval Gate mandatory.
- Reasoning Trace must be prominent.

## Assumptions
- None.

---

## 1. Tech Stack
- React
- Vite
- Vanilla CSS / Inline Styles (per provided UI)

## 2. Layout Structure
A two-panel dashboard:
- **Left Panel (Corpus & Conflicts):**
  - Displays the 7 documents as tiles (showing Name, Dept, Updated Date, Size).
  - Displays `ConflictCard` components once conflicts are detected.
- **Right Panel (Reasoning Trace):**
  - A scrollable feed of `TraceStep` components.
  - Features real-time simulation logic for demo purposes.

## 3. Core Components

### 3.1 `DocTile`
- Shows document metadata.
- Applies a visual badge (`NEW`) to recently updated docs (e.g., DPDP_Directive).

### 3.2 `ConflictCard`
- Displays Severity, Title, Affected, Sources (Citations), and Resolution.
- Includes the **Human Approval Gate** buttons:
  - Approve finding
  - Mark false positive
  - Escalate to legal

### 3.3 `TraceStep`
- Must show the agent name, execution time, and query (if applicable).
- Must show citations with Foundry IQ attribution.
- **Crucial:** Must render the `conclusion` as a prose paragraph. No timestamped JSON blobs.

## 4. State Management
- `phase`: "idle" | "scanning" | "done"
- `traceStep`: Integer tracking which step is currently rendering.
- `visibleConflicts`: Array of conflicts revealed in the left panel.
- `approvedIds` & `rejectedIds`: Sets for Human Approval Gate tracking.
