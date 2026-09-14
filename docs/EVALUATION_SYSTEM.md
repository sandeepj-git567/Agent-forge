# Automated AI Agent Evaluation Framework Architecture

AgentForge AI includes a comprehensive, automated evaluation framework that measures agent performance across 5 quality dimensions: Correctness, Relevance, Groundedness, Citation Quality, and Retrieval Precision/Recall.

## 1. Evaluation Metrics Specifications

| Metric | Score Range | Description & Calculation Method |
|---|---|---|
| **Correctness** | `0.0` - `1.0` | Measures alignment of actual agent output against expected ground truth using sequence matching and key phrase overlap. |
| **Relevance** | `0.0` - `1.0` | Measures prompt intent match based on keyword intersection density. |
| **Groundedness** | `0.0` - `1.0` | Evaluates reliance on retrieved RAG evidence snippets and structural headers (`summary`, `evidence`, `based on`). |
| **Citation Quality** | `0.0` - `1.0` | Verifies presence of explicit source URLs, document IDs, or inline brackets (`[1]`, `source:`, `doc_id`). |
| **Retrieval Precision / Recall** | `0.0` - `1.0` | Calculates Precision@K, Recall@K, and F1 score for vector database search results. |

---

## 2. Overall Score Calculation

$$\text{Overall Score} = (0.3 \times \text{Correctness}) + (0.3 \times \text{Relevance}) + (0.2 \times \text{Groundedness}) + (0.2 \times \text{Citation Quality})$$

---

## 3. Evaluation API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/evaluations/run` | `POST` | Evaluate a single agent output against prompt & expected criteria. Persists result to database. |
| `/api/v1/evaluations/benchmark/run` | `POST` | Execute batch evaluation run across the entire benchmark dataset. Computes aggregate averages. |
| `/api/v1/evaluations` | `GET` | Retrieve historical evaluation runs from database. |
| `/api/v1/evaluations/benchmarks` | `GET` | List pre-packaged benchmark dataset test cases. |

---

## 4. Benchmark Datasets

Pre-packaged test cases defined in `agentforge/eval/datasets.py`:
- `bench-001`: Multi-agent research framework prompt evaluation.
- `bench-002`: Safe Python code generation evaluation.
- `bench-003`: RAG question answering and document citation evaluation.
- `bench-004`: DAG workflow decomposition evaluation.
- `bench-005`: Static AST security code audit evaluation.
