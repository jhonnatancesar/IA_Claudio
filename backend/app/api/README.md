# API para aplicações

Documentação: docs/API.md. TASKs: TASK-067 a TASK-073.

Camada de entrada HTTP usada por aplicações externas: autenticação por API key, validação de payload, execução síncrona, timeout, resposta JSON final e rastreio de consumo.

- `app.py` (TASK-067) — aplicação FastAPI (`DEC-009`), com handler global
  convertendo qualquer `ClaudiaoError` para o formato JSON de erro padrão
  do projeto (TASK-008).
- `auth.py` (TASK-067) — `get_current_application(authorization)`:
  dependência do FastAPI que autentica via header `Authorization: Bearer
  <api_key>`, reaproveitando `app.auth.api_keys.authenticate_application`
  (TASK-011). Código de erro `2002` (`INVALID_API_KEY`).
- `executions.py` (TASK-067) — `POST /v1/executions`: autentica e cria
  uma `Execution` (TASK-020) nova, sem validar o payload (TASK-068) nem
  processar de fato (TASK-069).

Testes em `tests/integration/test_api_executions_integration.py`
(autenticação/criação de execução reais via `fastapi.testclient.TestClient`)
e `tests/unit/test_api_auth.py` (extração do token, casos sem tocar o
banco).
