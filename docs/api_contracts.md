# ConflictSense API Contracts

## Research Inputs Used
- research/Pasted text(47).txt
- research/ConflictSense_UI.jsx

## Frozen Decisions Applied
- FastAPI backend structure.

## Assumptions
- Standard RESTful conventions applied based on FastAPI constraints.

---

## 1. GET `/analyze/stream`
Triggers the multi-agent pipeline analysis and streams results to the client.
**Protocol:** Server-Sent Events (SSE)
**Request Body:** `None` (uses the 7 pre-defined policy documents)
**Response Stream:**
Yields events as they happen:
```json
// Event: trace_step
data: { "agent": "DocumentAnalyzer", "time": "0.3s", ... }

// Event: conflict_detected
data: { "id": "1", "severity": "CRITICAL", ... }

// Event: done
data: { "status": "complete" }
```

## 2. POST `/approve`
Approves a specific conflict finding for resolution workflow.
**Request Body:**
```json
{
  "conflict_id": "string"
}
```
**Response Body:**
```json
{
  "status": "approved"
}
```

## 3. POST `/reject`
Marks a specific conflict finding as a false positive.
**Request Body:**
```json
{
  "conflict_id": "string"
}
```
**Response Body:**
```json
{
  "status": "rejected"
}
```
