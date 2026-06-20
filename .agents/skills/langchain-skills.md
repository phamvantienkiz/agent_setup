# LangChain + Deep Agents Development Guide

This project uses skills that contain up-to-date patterns and working reference scripts.

## CRITICAL: Invoke Skills BEFORE Writing Code

**ALWAYS** invoke the relevant skill first - skills have the correct imports, patterns, and scripts that prevent common mistakes.

### Getting Started

- **ecosystem-primer** (`.agents/references/langchain-skills/ecosystem-primer.md`) - Invoke FIRST for any LangChain/LangGraph/Deep Agents project: framework selection, env setup, and which skill to load next
- **langchain-dependencies** (`.agents/references/langchain-skills/langchain-dependencies.md`) - Invoke before installing packages or when resolving version issues (Python + TypeScript)

### LangChain Skills

- **langchain-fundamentals** (`.agents/references/langchain-skills/langchain-fundamentals.md`) - Invoke for create_agent, @tool decorator, middleware patterns
- **langchain-rag** (`.agents/references/langchain-skills/langchain-rag.md`) - Invoke for RAG pipelines, vector stores, embeddings
- **langchain-middleware** - Invoke for structured output with Pydantic

### LangGraph Skills

- **langgraph-cli** (`.agents/references/langchain-skills/langgraph-cli.md`) - Invoke for langgraph CLI commands: new, dev, build, up, deploy, and langgraph.json configuration
- **langgraph-fundamentals** (`.agents/references/langchain-skills/langgraph-fundamentals.md`) - Invoke for StateGraph, state schemas, edges, Command, Send, invoke, streaming, error handling
- **langgraph-persistence** (`.agents/references/langchain-skills/elanggraph-persistence.md`) - Invoke for checkpointers, thread_id, time travel, memory, subgraph scoping
- **langgraph-human-in-the-loop** (`.agents/references/langchain-skills/langgraph-human-in-the-loop.md`) - Invoke for interrupts, human review, error handling, approval workflows

### Deep Agents Skills

- **deep-agents-core** (`.agents/references/langchain-skills/deep-agents-core.md`) - Invoke for Deep Agents harness architecture
- **deep-agents-memory** (`.agents/references/langchain-skills/deep-agents-memory.md`) - Invoke for long-term memory with StoreBackend
- **deep-agents-orchestration** (`.agents/references/langchain-skills/deep-agents-orchestration.md`) - Invoke for multi-agent coordination
- **managed-deep-agents** (`.agents/references/langchain-skills/managed-deep-agents.md`) - Invoke for Managed Deep Agents: deploy with the CLI, use the SDKs, stream runs, connect MCP tools, and build React `useStream` UIs

## Environment Setup

Required environment variables:

```bash
OPENAI_API_KEY=<your-key>  # For OpenAI models
ANTHROPIC_API_KEY=<your-key>  # For Anthropic models
```
