# Azure Architecture

Factual description of the ConflictSense production retrieval and reasoning stack.

## 1. Azure AI Search Index

Index name: `rag-1781022790838` (configurable via `AZURE_SEARCH_INDEX`).

Documents are indexed from `knowledge_base/*.md` by `scripts/build_azure_search_index.py`:

- `chunk_id` — unique chunk key
- `parent_id` — section identifier (e.g. `§4.2`)
- `title` — source document filename
- `chunk` — searchable text
- `text_vector` — 1024-dimension embedding (`Collection(Edm.Single)`)

Schema export: `data/azure_schema_export.json`.

## 2. Hybrid Retrieval

At query time, `AzureSearchRetriever` sends:

- keyword search on `chunk` and `title`
- vector query on `text_vector` (when `OPENROUTER_API_KEY` is set)

Both signals are combined in a single Azure AI Search request.

## 3. Semantic Ranking

Search requests use `queryType: semantic` with configuration `rag-1781022790838-semantic-configuration`.

Prioritized fields: `title` (title field), `chunk` (content field).

## 4. AzureSearchRetriever

File: `agents/azure_search_retriever.py`.

- Reads `AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_KEY`, `AZURE_SEARCH_INDEX`
- POSTs to `/indexes/{index}/docs/search`
- Maps results to `Chunk` objects consumed by `DocumentAnalyzer`
- Raises on zero results or HTTP failure so fallback can activate

## 5. ProviderChain

File: `agents/llm_provider.py`.

`ChunkExtractor` calls `ProviderChain.complete_json()` for citation extraction. Provider order:

1. Gemini
2. OpenRouter
3. Groq
4. NVIDIA NIM
5. Mock (Tier 3, `iq_mock_data.py`)

Azure OpenAI is not in this chain.

## 6. Fallback Architecture

Retrieval fallback (`DocumentAnalyzer`):

```
AzureSearchRetriever.search()
  -> on failure or zero results -> LocalRetriever.search()
```

Reasoning fallback (`ChunkExtractor`):

```
ProviderChain (Gemini -> OpenRouter -> Groq -> NVIDIA)
  -> on total failure -> _mock_result() (Tier 3)
```

Pipeline-level fallback (`ConflictSenseOrchestrator`): Tier 3 mock data guarantees completion.

## 7. Reasoning Pipeline

Execution order:

```
Knowledge Base
  -> Azure AI Search (hybrid + semantic retrieval)
  -> AzureSearchRetriever
  -> DocumentAnalyzer
  -> ChunkExtractor
  -> ProviderChain
  -> Conflict Detection (ConflictDetector)
  -> Validation (ConflictValidator)
  -> Impact Assessment (ImpactAssessor)
  -> Risk Quantification (RiskQuantifier)
  -> Resolution Recommendation (ResolutionRecommender)
```

`agents/foundry_iq_client.py` retains `Citation`, `FoundryIQResult`, and `_mock_result()` only. It is a compatibility layer, not a runtime client.
