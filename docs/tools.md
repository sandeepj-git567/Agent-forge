# Tool Specification & Registry Documentation

## Tool Permission Classifications

All tools registered in `ToolRegistry` are tagged with a `PermissionCategory`:

| Category | Description | Approval Required |
|---|---|---|
| `READ_ONLY` | Read-only inspection of documents or knowledge | No |
| `EXTERNAL_SEARCH` | External web search queries | No |
| `FILE_ANALYSIS` | Static code / file structure analysis | No |
| `WRITE` | In-memory task creation or state updates | No |
| `DESTRUCTIVE` | Destructive database or storage operations | **YES** (Strictly blocked without explicit approval) |

## Phase 1 Registered Tools

1. `web_search`: Interface for web searching (`EXTERNAL_SEARCH`).
2. `document_search`: Interface for internal document corpus search (`READ_ONLY`).
3. `safe_code_analysis`: Static AST python analysis and vulnerability scanning (`FILE_ANALYSIS`).
4. `task_management`: In-memory task graph manager (`WRITE`).

## Safety Rules

- **Zero Shell Execution**: No arbitrary shell execution tools exist or can be registered.
- **Allowlist Filtering**: Execution engines can pass explicit tool allowlists to restrict accessible tools per task.
