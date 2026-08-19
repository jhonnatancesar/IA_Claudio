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
- `executions.py` (TASK-067, TASK-068) — `POST /v1/executions`: autentica,
  valida o payload contra `ExecutionRequest` e cria uma `Execution`
  (TASK-020) nova, sem processar de fato (TASK-069).

Testes em `tests/integration/test_api_executions_integration.py`
(autenticação/validação/criação de execução reais via
`fastapi.testclient.TestClient`) e `tests/unit/test_api_auth.py`/
`tests/unit/test_api_schemas.py` (extração do token, validação de schema,
sem tocar o banco).
