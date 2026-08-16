# LLM — abstração de raciocínio local

Documentação: docs/ARCHITECTURE.md. TASKs: TASK-014, TASK-016 a TASK-019.

Interface LocalLLMProvider, protocolo JSON modelo ↔ orquestrador, validação dos JSONs internos, prompt-base e composição dinâmica de prompt/contexto. Ollama é apenas o runtime inicial (ver llm/providers/).

- `provider.py` (TASK-014) — `LocalLLMProvider` (classe abstrata),
  `CompletionRequest`/`CompletionResponse`, `LocalLLMProviderError`. Só a
  interface — `OllamaProvider` (implementação concreta) é TASK-015; protocolo
  JSON por etapa é TASK-016/TASK-017.

Testes em `tests/unit/test_llm_provider.py`.
