# API para aplicações

Fonte: seções 24, 25 e 26 da especificação mestre.

## Aplicações e autenticação

- Cada aplicação tem sua própria API key/token. Usuários humanos usam usuário e senha
  (ver `AUTHENTICATION.md`).
- A aplicação envia contexto, tipo de uso, política (`ExecutionPolicy`), permissão de
  pesquisa, timeout, limites e dados necessários.
- O agente valida os campos obrigatórios antes de iniciar. **Se faltar campo
  obrigatório, retorna erro imediatamente, sem inferir ou preencher.**
- A comunicação com aplicações usa JSON.

## Execução das aplicações

- Execução **síncrona** na V1: a aplicação envia a requisição e espera o JSON final.
  Sem eventos intermediários para a aplicação.
- Cada requisição recebe um `execution_id` único.
- Reenvios e retries manuais sempre geram **novo** `execution_id`.

## Timeout das aplicações

- O timeout é definido pela própria aplicação.
- Ao estourar, o Claudião cancela a execução, registra etapa atual e ferramenta ativa,
  e retorna erro JSON padronizado com HTTP e código interno próprio (ver
  `ERROR_CATALOG.md`).
- A aplicação deve refazer a solicitação como **nova execução**.

## Resposta

Formato de sucesso e de erro seguem o contrato descrito em `ERROR_CATALOG.md`.

**Implementação (TASK-067):** `backend/app/api/` — FastAPI (`app.py`,
`DEC-009`), com `uvicorn` como servidor ASGI (nenhuma das duas rodada em
produção ainda; só a aplicação FastAPI existe). `auth.py`:
`get_current_application(authorization)`, dependência que extrai a API
key do header `Authorization: Bearer <api_key>` e reaproveita
`app.auth.api_keys.authenticate_application` (TASK-011) — nunca
reimplementa a verificação. Levanta `ClaudiaoError` (`INVALID_API_KEY`,
código 2002, 401) se ausente/malformada/desconhecida; um handler global
em `app.py` converte qualquer `ClaudiaoError` de uma rota para o formato
JSON de erro padrão do projeto (TASK-008), em vez do formato default do
FastAPI. `executions.py`: `POST /v1/executions`, autentica e cria uma
`Execution` (TASK-020) nova, devolvendo `execution_id`/`status`
(`PENDING`) — corpo da requisição aceito como objeto JSON genérico, sem
validação de schema (isso é TASK-068); a execução nunca é processada de
fato aqui (TASK-069), nem tem timeout (TASK-070/071), nem o formato final
de resposta de sucesso (TASK-072), nem rastreio de consumo (TASK-073).

**Implementação (TASK-068):** `backend/app/api/schemas.py` —
`ExecutionRequest` (Pydantic): `objective`/`usage_type`/
`web_search_allowed`/`timeout_seconds` obrigatórios ("a aplicação envia
contexto, tipo de uso, política, permissão de pesquisa, timeout, limites
e dados necessários... se faltar campo obrigatório, retorna erro
imediatamente, sem inferir ou preencher"); `context`/`max_steps`
opcionais, `None` por padrão explícito, nunca inferidos de outro campo.
`POST /v1/executions` agora recebe `payload: ExecutionRequest` em vez de
`dict` genérico — o FastAPI rejeita automaticamente um corpo que não
bate com o schema. Um novo handler em `app.py` converte
`RequestValidationError` para o formato JSON de erro padrão do projeto,
reaproveitando os códigos genéricos já existentes desde a fundação
(`MISSING_REQUIRED_FIELD`, 1001; `INVALID_FIELD_VALUE`, 1002 — TASK-007),
em vez de criar códigos novos só para isto. Montar a `ExecutionPolicy`
de fato a partir do payload validado é TASK-069, não implementado aqui.

**Implementação (TASK-069):** `POST /v1/executions` agora executa de
fato, de forma síncrona: monta `ExecutionPolicy.for_application`
(TASK-022) a partir dos campos já validados do payload
(`timeout_seconds`/`web_search_allowed`/`max_steps`) e roda
`ExecutionOrchestrator.run_until_response` (TASK-023/026) até uma
resposta final — "a aplicação envia a requisição e espera o JSON final,
sem eventos intermediários". `backend/app/api/dependencies.py`:
`get_local_llm_provider`/`get_active_model`, dependências do FastAPI
(substituíveis por fakes em teste via `app.dependency_overrides`, já que
nenhum modelo Ollama real foi baixado). `get_active_model` lê
`CLAUDIAO_ACTIVE_MODEL` (`config/.env.example`, já previsto desde a
TASK-002) — se ausente, erro claro (`NO_ACTIVE_MODEL_CONFIGURED`, código
3001) em vez de tentar completar com nome de modelo vazio.
`LocalLLMProviderError`/`ToolExecutorNotConfiguredError` (falhas de
runtime do orquestrador que não são `ClaudiaoError`) são convertidas para
erros com código próprio (`3002`/`3003`) em vez de vazar como 500 não
tratado.

O envelope de sucesso desta TASK é o mínimo (`execution_id`/`status`/
`result`) — o contrato final formal (`"success": true`, à semelhança do
`"success": false` de erro) e rastreio de consumo são TASK-072/TASK-073,
não implementados aqui.

**Implementação (TASK-070):** `timeout_seconds` agora é um limite de
verdade, não só um valor guardado na política. `POST /v1/executions` roda
`ExecutionOrchestrator.run_until_response` num worker de um
`ThreadPoolExecutor` de módulo e espera com
`future.result(timeout=payload.timeout_seconds)` — a resposta HTTP
retorna assim que o prazo estoura, mesmo que a chamada ao modelo local em
si esteja travada (uma única etapa `RESPOND` não tem outro ponto de
checagem cooperativa antes dela). Ao estourar, o `CancellationToken`
(TASK-030) compartilhado é cancelado ("ao estourar, o Claudião cancela a
execução") e a rota devolve `APPLICATION_TIMEOUT_EXCEEDED` (código 4009,
HTTP 504, `docs/ERROR_CATALOG.md`). Se o orquestrador estiver entre
etapas de um fluxo `USE_TOOL`, ele mesmo observa o cancelamento (o mesmo
mecanismo cooperativo da TASK-030) e chama `execution.cancel(...)` — só
uma thread por vez escreve em `execution`.

**Implementação (TASK-071):** os `details` de `APPLICATION_TIMEOUT_EXCEEDED`
agora trazem "etapa atual e ferramenta ativa", como a seção acima exige —
`_timeout_error_details(execution, timeout_seconds)`
(`backend/app/api/executions.py`), função pura testável isoladamente:
`current_step` é `execution.step_count + 1` (1-indexado — a etapa que
estava em andamento quando o prazo estourou); `active_tool` é o `tool` da
última etapa já registrada em `execution.steps`, ou `None` se nenhuma
etapa foi registrada ainda ou a última não usava ferramenta. Como nenhum
`tool_executor` está configurado ainda (Tool Registry, TASK-088+), na
prática hoje o endpoint real quase sempre reporta `current_step: 1` e
`active_tool: null` (o timeout costuma travar na primeira chamada ao
modelo, antes de qualquer etapa ser registrada) — o valor cresce em
utilidade conforme fluxos com `USE_TOOL` passarem a existir de ponta a
ponta.

**Implementação (TASK-072):** a resposta de sucesso de `POST
/v1/executions` agora segue o mesmo envelope `{"success": bool, ...}` do
erro — `build_success_response(data)` (`backend/app/api/responses.py`)
monta `{"success": true, "data": data}`. Antes desta TASK a resposta de
sucesso era o dict cru (`execution_id`/`status`/`result` direto no nível
superior, sem `success`), inconsistente com o formato de erro já em uso
desde a TASK-008. Ver `docs/ERROR_CATALOG.md`, "Formato padrão de
resposta", para o contrato completo (erro e sucesso).

**Implementação (TASK-073):** a cada desfecho de `POST /v1/executions`
(sucesso, timeout, falha de modelo/ferramenta),
`record_usage(application.id, execution.execution_id, status)`
(`app.usage.usage_model`, `docs/QUOTAS.md`) grava uma linha em
`usage_records` — o registro mínimo de que a aplicação consumiu uma
requisição. Requisições rejeitadas antes de chegar à execução (401 de
autenticação, 400 de validação) não geram registro, já que nunca chegam a
criar uma `Execution`. Medição de tokens/volume, ciclo de renovação e
aplicação de limites continuam TASK-108 a TASK-114, não implementados
aqui — ver `docs/QUOTAS.md`.

## TASKs relacionadas

TASK-067 a TASK-073: API local, validação de payload, execução síncrona, timeout,
erro de timeout, resposta JSON final, rastreio de consumo.
