# ConflictSense — Policy Conflict Intelligence

> AI-powered structural impossibility detection for enterprise policy documents.
> Powered by Azure Foundry IQ. Built for the Microsoft Agents League Hackathon.

**Status:** Phase 3 Implementation Complete. Core Reasoning Engine Hardened.

---

## Implemented Features & Completed Milestones
- [x] Phase 1: Frontend MVP, Backend SSE, Test Corpus, Initial Data Contracts.
- [x] Phase 2: DocumentAnalyzer, ConflictDetector, Mock Fallback System, Full Test Suite.
- [x] Phase 3: Reasoning Loop Hardening (Removed contaminated fallback, eliminated blind pairing fabrication, parallel document retrieval).
- [ ] Phase 4: Downstream Agents (`ImpactAssessor`, `RiskQuantifier`, `ResolutionRecommender`).

---

## Quick Start

### Backend
```bash
cp .env.example .env
# Fill in AZURE_FOUNDRY_ENDPOINT and AZURE_API_KEY
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Upload Knowledge Base to Foundry IQ
```bash
python scripts/upload_to_foundry_iq.py
```

---

## Repository Structure

```
conflictsense/
├── docs/               ← Authoritative specification (read before touching code)
├── frontend/           ← React + Vite dashboard
├── backend/            ← FastAPI server (SSE streaming)
├── agents/             ← 5-agent pipeline + orchestrator
├── knowledge_base/     ← 7 synthetic Nexora policy documents
├── mock_data/          ← Tier 3 pre-computed fallback responses
├── prompts/            ← Frozen system prompts (one file per agent)
├── tests/              ← Unit + integration + E2E tests
├── scripts/            ← Upload to Foundry IQ, ablation test
├── .env.example
└── requirements.txt
```

---

## Architecture

See `docs/system_architecture.md`.

---

## Responsible AI

See `docs/reliability_spec.md` and `docs/acceptance_criteria.md`.

- All findings require human approval before any action is taken.
- Low-confidence findings (< 65%) never appear on the main dashboard.
- All assertions are grounded in Foundry IQ citations.
