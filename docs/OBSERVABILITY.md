# Observabilidade

Fonte: seções 35 e 44 da especificação mestre.

## Logs

- Níveis: `DEBUG / INFO / WARNING / ERROR`. `DEBUG` desativado por padrão.
- Logs são gravados em **arquivo local e PostgreSQL**. Arquivos usam rotação
  automática; banco usa retenção cíclica.

### Logging local em arquivo (TASK-005)

Implementado em `backend/app/observability/logging_config.py`:
`configure_logging()` configura o logger raiz `claudiao` (nível via
`CLAUDIAO_LOG_LEVEL`, padrão `INFO` — `DEBUG` só se definido explicitamente);
`get_logger(nome)` retorna um logger filho. Rotação por tamanho: 10 MB por arquivo,
5 backups (`RotatingFileHandler`), diretório configurável via `CLAUDIAO_LOG_DIR`
(padrão `logs/`, criado automaticamente se não existir).

### Logging estruturado no PostgreSQL (TASK-006)

Implementado em `backend/app/observability/postgres_log_handler.py`
(`PostgresLogHandler`) e gravado na tabela `logs`
(`backend/app/db/migrations/0002_logs.sql`: `timestamp`, `level`, `logger`,
`message`, `context jsonb`). `configure_logging()` anexa esse handler
automaticamente quando `CLAUDIAO_POSTGRES_*` está disponível no ambiente
(`build_dsn_from_env()`); sem essas variáveis, o logging segue normalmente só em
arquivo — nunca é um requisito rígido. Uma conexão nova é aberta por mensagem
(sem pool — otimização futura, se o volume exigir); falhas de escrita no banco não
derrubam a aplicação nem o arquivo local.

**Lacuna conhecida:** a especificação (seção 35) descreve retenção cíclica para os
logs em banco, mas não há TASK numerada dedicada a essa limpeza no backlog — não
implementada ainda. Registrado aqui para não ser esquecida quando uma TASK futura
tratar de retenção/limpeza de dados operacionais.

## Execution Trace

Cada execução tem um Execution Trace com: `execution_id`, origem, usuário/aplicação,
horário, duração, intenção, plano, etapas, ferramentas, erros, códigos, consumo,
número de passos, resultado, versão do prompt e versão das regras do orquestrador.

**Implementação (TASK-078):** `backend/app/observability/execution_trace.py`
— `ExecutionTrace` (dataclass, mesmo espírito do modelo de `Execution`,
TASK-020): `execution_id`/`origin`/`requester`/`objective`/`started_at`/
`finished_at`/`steps`/`errors`/`error_codes`/`usage`/`result`/
`prompt_version`/`orchestrator_rules_version` armazenados;
`step_count`/`tools_used`/`duration_seconds` são propriedades derivadas
de `steps`/`started_at`/`finished_at`, nunca guardadas em duplicidade.
`add_step(step)`/`record_error(error, code=None)`/`finish(result=None)`
registram o ciclo de vida. "Plano" e "etapas" da especificação viraram um
único campo (`steps`) — o orquestrador desta V1 não mantém um objeto de
plano separado da sequência de etapas decidida reativamente
(`docs/ARCHITECTURE.md`). `prompt_version` reaproveita `PROMPT_VERSION`
(`app.llm.prompt`, TASK-018); `orchestrator_rules_version` fica `None`
por padrão — não existe hoje nenhum esquema de versionamento para "as
regras do orquestrador" (lacuna conhecida, registrada aqui, mesmo
espírito da lacuna de retenção de logs já anotada acima).

**Implementação (TASK-079):** o trace agora é conectado ao
`ExecutionOrchestrator` de verdade — `run_step`/`run_until_response`
(`app.orchestrator.orchestrator`) ganharam um parâmetro `trace:
ExecutionTrace | None = None`, mesmo padrão de `cancellation_token`
(TASK-030), repassado também por `plan_initial_step`
(`app.orchestrator.planner`) e `replan`
(`app.orchestrator.replanner`). Cada chamada ao modelo e cada execução de
ferramenta são cronometradas de verdade e registradas: `step_durations`
(novo campo, alinhado por índice com `steps`) e `tool_durations` (novo
campo, alinhado por índice com `tools_used` — só etapas `USE_TOOL` que
chegaram a executar geram entrada). `POST /v1/executions`
(`backend/app/api/executions.py`) cria um `ExecutionTrace` a cada
requisição e passa para `run_until_response` — o trace é populado de
verdade durante a execução real, mas não é persistido nem devolvido na
resposta HTTP (nenhuma TASK do bloco pede isso ainda). Registro de erros
(`record_error`, já existente desde a TASK-078) **não** foi conectado —
fora do escopo literal desta TASK ("ferramentas/passos/tempos", não
erros).

## Métricas

- taxa de sucesso
- uso correto/incorreto de ferramentas
- falhas por ferramenta/provider
- respostas bloqueadas por baixa confiança
- falhas de validação
- replanejamentos
- tempo médio
- número de passos
- consumo
- erros por provider

As métricas aparecem no painel administrativo (ver `PANEL.md`).

## TASKs relacionadas

TASK-078 a TASK-083: Execution Trace, registro de ferramentas/passos/tempos, métricas
básicas, painel web read-only e sua exibição de execuções/erros/logs/consumo.
TASK-005/TASK-006: logging local e logging estruturado no PostgreSQL. TASK-145:
métricas finais de qualidade.
