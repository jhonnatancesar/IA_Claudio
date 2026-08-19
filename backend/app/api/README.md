# API para aplicações

Documentação: docs/API.md. TASKs: TASK-067 a TASK-073.

Camada de entrada HTTP usada por aplicações externas: autenticação por API key, validação de payload, execução síncrona, timeout, resposta JSON final e rastreio de consumo.

- `app.py` (TASK-067, TASK-068) — aplicação FastAPI (`DEC-009`), com
  handlers globais convertendo `ClaudiaoError` (TASK-008) e
  `RequestValidationError` (TASK-068, reaproveitando os códigos `1001`/
  `1002` já existentes) para o formato JSON de erro padrão do projeto.
- `auth.py` (TASK-067) — `get_current_application(authorization)`:
  dependência do FastAPI que autentica via header `Authorization: Bearer
  <api_key>`, reaproveitando `app.auth.api_keys.authenticate_application`
  (TASK-011). Código de erro `2002` (`INVALID_API_KEY`).
- `schemas.py` (TASK-068) — `ExecutionRequest` (Pydantic):
  `objective`/`usage_type`/`web_search_allowed`/`timeout_seconds`
  obrigatórios; `context`/`max_steps` opcionais, sem inferência.
- `dependencies.py` (TASK-069) — `get_local_llm_provider`/
  `get_active_model`: dependências do FastAPI, substituíveis por fakes
  em teste. `get_active_model` lê `CLAUDIAO_ACTIVE_MODEL`
  (`config/.env.example`); código de erro `3001`
  (`NO_ACTIVE_MODEL_CONFIGURED`) se ausente.
- `executions.py` (TASK-067, TASK-068, TASK-069, TASK-070) — `POST
  /v1/executions`: autentica, valida o payload contra `ExecutionRequest`
  e executa de fato, de forma síncrona, via `ExecutionOrchestrator.
  run_until_response` (TASK-069) — monta `ExecutionPolicy.for_application`
  a partir do payload. `LocalLLMProviderError`/
  `ToolExecutorNotConfiguredError` viram erros com código próprio
  (`3002`/`3003`) em vez de 500 não tratado. `timeout_seconds` agora é
  aplicado como limite de verdade (TASK-070): `run_until_response` roda
  num worker de um `ThreadPoolExecutor` de módulo, e a rota espera com
  `future.result(timeout=...)` — retorna assim que o prazo estoura, sem
  esperar uma chamada travada ao modelo. Ao estourar, cancela o
  `CancellationToken` (TASK-030) compartilhado e devolve
  `APPLICATION_TIMEOUT_EXCEEDED` (código `4009`, HTTP `504`). Formato
  específico do erro (etapa atual/ferramenta ativa) é TASK-071.

Testes em `tests/integration/test_api_executions_integration.py`
(autenticação/validação/execução síncrona real e timeout reais via
`fastapi.testclient.TestClient`, com `LocalLLMProvider` fake — nenhum
modelo Ollama real foi baixado) e `tests/unit/test_api_auth.py`/
`tests/unit/test_api_schemas.py`/`tests/unit/test_api_dependencies.py`
(extração do token, validação de schema, leitura de
`CLAUDIAO_ACTIVE_MODEL`, sem tocar o banco).
