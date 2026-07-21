# FacultyIQ AI Infrastructure Architecture

## 🧠 Overview

FacultyIQ features an **offline-first AI processing engine** designed around **Ollama local LLM inference** (`localhost:11434`). This guarantees that sensitive university candidate data, research proposals, and evaluation metrics remain strictly on-premise.

---

## 🏗 Subsystem Architecture

- **`IOllamaClient`**: Low-level HTTP client executing local model inference via `/api/generate` and discovering models via `/api/tags`.
- **`IModelRegistry`**: Registry service validating model readiness (e.g., `llama3:8b`) before evaluation execution.
- **`IPromptRegistry`**: Version-controlled prompt repository managing prompt templates with runtime variable interpolation.
- **`IAIProvider`**: Multi-provider abstraction preparing the platform for future cloud providers (OpenAI, Gemini, Azure OpenAI) without modifying core domain logic.

---

## ⚡ Resilience & Health

- **Retries**: Resilient HTTP pipeline handling model loading delays and transient inference retries.
- **Health Verification**: `OllamaHealthCheck` verifies local LLM daemon availability and reports discovered model counts to ASP.NET Core `/health`.
