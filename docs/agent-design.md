# Agent Design Specification

## Overview

AgentForge AI uses a hierarchical multi-agent pattern powered by **Google ADK 2.9.0**.

## Agent Specifications

### 1. Root Orchestrator Agent (`root_orchestrator`)
- **Role**: Master coordinator of task execution and multi-agent delegation.
- **Model**: Gemini 2.5 Flash
- **Sub-Agents**: `planner`, `researcher`, `reviewer`
- **Responsibility**: Receives user task, orchestrates sub-agents, and compiles final response.

### 2. Strategic Planner Agent (`planner`)
- **Role**: Decomposes user goal into step-by-step task graphs.
- **Tools**: `task_management`
- **Output**: Structured execution plan.

### 3. Researcher Agent (`researcher`)
- **Role**: Gathers factual evidence from web and internal document sources.
- **Tools**: `web_search`, `document_search`
- **Output**: Evidence synthesis with inline citations.

### 4. Quality & Safety Reviewer Agent (`reviewer`)
- **Role**: Validates facts, checks code safety, and verifies prompt guardrail compliance.
- **Tools**: `safe_code_analysis`
- **Output**: Verification verdict and quality check.
