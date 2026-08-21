# API para aplicações

Documentação: docs/API.md. TASKs: TASK-067 a TASK-073, TASK-079.

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
- `executions.py` (TASK-067 a TASK-073, TASK-079) — `POST /v1/executions`:
  autentica, valida o payload contra `ExecutionRequest` e executa de
  fato, de forma síncrona, via `ExecutionOrchestrator.run_until_response`
  (TASK-069) — monta `ExecutionPolicy.for_application` a partir do
  payload. `LocalLLMProviderError`/`ToolExecutorNotConfiguredError` viram
  erros com código próprio (`3002`/`3003`) em vez de 500 não tratado.
  `timeout_seconds` é aplicado como limite de verdade (TASK-070):
  `run_until_response` roda num worker de um `ThreadPoolExecutor` de
  módulo, e a rota espera com `future.result(timeout=...)` — retorna
  assim que o prazo estoura, sem esperar uma chamada travada ao modelo.
  Ao estourar, cancela o `CancellationToken` (TASK-030) compartilhado e
  devolve `APPLICATION_TIMEOUT_EXCEEDED` (código `4009`, HTTP `504`), com
  `details` no formato específico exigido pela seção 26 (TASK-071):
  `_timeout_error_details(execution, timeout_seconds)` monta
  `current_step` (`execution.step_count + 1`, 1-indexado) e `active_tool`
  (`tool` da última etapa já registrada, ou `None`). A resposta de
  sucesso (TASK-072) usa `build_success_response`.
  Ao chegar a qualquer desfecho (sucesso, timeout, falha de
  modelo/ferramenta), grava rastreio de consumo (TASK-073):
  `record_usage(application.id, execution.execution_id, status)`
  (`app.usage.usage_model`). Um `ExecutionTrace` (TASK-079,
  `app.observability.execution_trace`) é criado a cada requisição e
  passado para `run_until_response`, que o popula de verdade com
  etapas/ferramentas/tempos reais; `trace.finish(...)` fecha o ciclo nos
  desfechos seguros de tocar (não no timeout, mesma razão de
  `execution.status` lá). O trace não é persistido nem devolvido na
  resposta.
- `responses.py` (TASK-072) — `build_success_response(data)`: monta
  `{"success": true, "data": data}`, espelhando `build_error_response`
  (TASK-008, `app.errors.response`) do lado do sucesso.

Testes em `tests/integration/test_api_executions_integration.py`
(autenticação/validação/execução síncrona real, timeout e rastreio de
consumo reais via `fastapi.testclient.TestClient`, com `LocalLLMProvider`
fake — nenhum modelo Ollama real foi baixado), `tests/unit/
test_api_executions.py` (`_timeout_error_details` isolada, sem tocar
rede/banco), `tests/unit/test_api_responses.py` (`build_success_response`
isolada) e `tests/unit/test_api_auth.py`/`tests/unit/test_api_schemas.py`/
`tests/unit/test_api_dependencies.py` (extração do token, validação de
schema, leitura de `CLAUDIAO_ACTIVE_MODEL`, sem tocar o banco).
