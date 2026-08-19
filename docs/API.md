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

## TASKs relacionadas

TASK-067 a TASK-073: API local, validação de payload, execução síncrona, timeout,
erro de timeout, resposta JSON final, rastreio de consumo.
