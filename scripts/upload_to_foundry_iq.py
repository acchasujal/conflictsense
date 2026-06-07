#!/usr/bin/env python3
"""
scripts/upload_to_foundry_iq.py
Uploads all 7 synthetic policy documents in knowledge_base/ to Azure Foundry IQ.

Spec reference: docs/foundry_iq_spec.md, docs/implementation_plan.md (Day 1)

Usage:
  python scripts/upload_to_foundry_iq.py

Prerequisites:
  - AZURE_FOUNDRY_ENDPOINT set in .env
  - AZURE_API_KEY set in .env
  - All 7 knowledge_base/*.md files populated with content

Do NOT implement functionality here. This is a placeholder.
"""

# TODO: Load credentials from .env
# TODO: Iterate over knowledge_base/*.md
# TODO: Upload each file to Foundry IQ as a named knowledge source
# TODO: Print the knowledge_source_id for each uploaded document (needed by agents)
