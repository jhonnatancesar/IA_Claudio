# LLM — abstração de raciocínio local

Documentação: docs/ARCHITECTURE.md. TASKs: TASK-014, TASK-016 a TASK-019.

Interface LocalLLMProvider, protocolo JSON modelo ↔ orquestrador, validação dos JSONs internos, prompt-base e composição dinâmica de prompt/contexto. Ollama é apenas o runtime inicial (ver llm/providers/).

- `provider.py` (TASK-014) — `LocalLLMProvider` (classe abstrata),
  `CompletionRequest`/`CompletionResponse`, `LocalLLMProviderError`. Só a
  interface; protocolo JSON por etapa é TASK-016/TASK-017.
- `providers/ollama_provider.py` (TASK-015) — `OllamaProvider`, via SDK
  oficial `ollama` (DEC-008). Ollama instalado e rodando localmente nesta
  máquina; nenhum modelo baixado ainda (`docs/OPEN_QUESTIONS.md`, item 3).
- `protocol.py` (TASK-016) — `ModelStep`, `Action`, `Confidence`,
  `ProtocolDecodeError`. Um JSON por etapa (seção 7 da especificação);
  decodificação básica (campos obrigatórios, valores dentro do enum,
  `parameters` precisa ser objeto — fix da TASK-017).
- `protocol_validator.py` (TASK-017) — `validate_step(raw) -> ModelStep`.
  Checagens semânticas extras (`execution_id` em formato UUID, `reason`
  não-vazio) e tradução de qualquer falha para `ClaudiaoError` (código 4001,
  faixa `MODEL_ORCHESTRATOR`).

Testes em `tests/unit/test_llm_provider.py`, `tests/unit/test_ollama_provider.py`,
`tests/unit/test_llm_protocol.py`, `tests/unit/test_llm_protocol_validator.py`
(unitários, com mock do client onde precisa) e
`tests/integration/test_ollama_provider_integration.py` (integração real
contra o Ollama local; pula automaticamente se indisponível).
