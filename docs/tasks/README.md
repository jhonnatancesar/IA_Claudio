# TASKs

Cada arquivo `TASK-XXX.md` descreve uma unidade de trabalho: objetivo, escopo, fora
de escopo, dependências, critérios de aceite, testes esperados, documentação afetada
e status. Antes de executar uma TASK, leia os documentos obrigatórios definidos em
`AGENTS.md`.

A numeração e a ordem (TASK-001 a TASK-147) vêm da seção 51 da especificação mestre
(`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`) e não devem ser alteradas sem
antes apresentar uma auditoria e uma justificativa ao usuário.

Ver `docs/BACKLOG.md` para a lista agrupada por bloco funcional e `docs/ROADMAP.md`
para as fases e marcos.

## Marcos

- **TASK-087** — primeiro Claudião utilizável em produção controlada (mínimo
  utilizável seguro).
- **TASK-147** — V1 completa.

## Estado atual

Todas as 147 TASKs foram cadastradas nesta organização inicial.

- **TASK-001** — concluída (estrutura de diretórios, `.gitignore`, `git init` e
  primeiro commit — ver `docs/tasks/TASK-001.md` e `docs/DECISION_LOG.md`, DEC-003).
- **TASK-002** — concluída (`config/.env.example` expandido com os parâmetros
  previstos na especificação, todos como placeholder — ver `docs/tasks/TASK-002.md`).
- **TASK-003** — concluída (PostgreSQL 17 local instalado, banco `claudiao` criado
  com role de aplicação próprio — ver `docs/tasks/TASK-003.md` e `docs/DATABASE.md`).
- **TASK-004** — concluída (schema inicial aplicado: `users`, `applications`,
  `settings`, `schema_migrations` — ver `docs/tasks/TASK-004.md` e
  `docs/DATABASE.md`).
- **TASK-005** — concluída (linguagem do backend decidida: Python —
  `docs/DECISION_LOG.md`, DEC-005; logging local rotativo em
  `backend/app/observability/logging_config.py`, 7 testes aprovados — ver
  `docs/tasks/TASK-005.md`).
- **TASK-006** — concluída (logging estruturado no PostgreSQL, tabela `logs`,
  `postgres_log_handler.py`, driver psycopg — DEC-006; 13/13 testes aprovados,
  incluindo integração real com o banco — ver `docs/tasks/TASK-006.md`).
- **TASK-007** — concluída (catálogo interno de erros,
  `backend/app/errors/catalog.py`, 9 faixas de domínio, 3 erros seed da fundação
  — ver `docs/tasks/TASK-007.md`).
- **TASK-008** — concluída (formato JSON padrão de erro,
  `backend/app/errors/response.py`, `ClaudiaoError` — ver
  `docs/tasks/TASK-008.md`). **Com esta TASK, o bloco "Fundação" (TASK-001 a
  TASK-008) está completo.**
- **TASK-009** — concluída (autenticação de usuários,
  `backend/app/auth/password.py` + `users.py`, PBKDF2 sem dependência nova — ver
  `docs/tasks/TASK-009.md`).
- **TASK-010** — concluída (autorização por papel, `backend/app/auth/roles.py`,
  `Role`/`is_admin`/`require_admin`, novo código de erro 2001 — ver
  `docs/tasks/TASK-010.md`). Suíte completa: 60/60 testes aprovados.

**Checkpoint de 10 TASKs (AGENTS.md):** com a TASK-010, a `main` local foi
enviada ao GitHub e `docs/HANDOFF.md` criado para permitir que outra IA
continue o trabalho.

- **TASK-011** — concluída (autenticação de aplicações via API key,
  `backend/app/auth/api_keys.py` — ver `docs/tasks/TASK-011.md`).
- **TASK-012** — concluída (criptografia de segredos, `backend/app/auth/crypto.py`,
  `Fernet`/`cryptography` — DEC-007 — ver `docs/tasks/TASK-012.md`).
- **TASK-013** — concluída (chave mestra externa ao banco,
  `backend/app/auth/master_key.py` — ver `docs/tasks/TASK-013.md`). **Com esta
  TASK, o bloco "Segurança e identidade" (TASK-009 a TASK-013) está
  completo.**
- **TASK-014** — concluída (interface `LocalLLMProvider`,
  `backend/app/llm/provider.py` — ver `docs/tasks/TASK-014.md`).
- **TASK-015** — concluída (`OllamaProvider`,
  `backend/app/llm/providers/ollama_provider.py`, SDK oficial `ollama` —
  DEC-008 — ver `docs/tasks/TASK-015.md`). Ollama instalado e rodando
  localmente; nenhum modelo baixado.
- **TASK-016** — concluída (protocolo JSON modelo ↔ orquestrador,
  `backend/app/llm/protocol.py`, `ModelStep`/`Action`/`Confidence` — ver
  `docs/tasks/TASK-016.md`).
- **TASK-017** — concluída (validação semântica,
  `backend/app/llm/protocol_validator.py`, novo código de erro 4001 — ver
  `docs/tasks/TASK-017.md`).
- **TASK-018** — concluída (prompt-base, `backend/app/llm/prompt.py` — ver
  `docs/tasks/TASK-018.md`).
- **TASK-019** — concluída (composição dinâmica de prompt/contexto,
  `backend/app/llm/prompt_composer.py` — ver `docs/tasks/TASK-019.md`). **Com
  esta TASK, o bloco "LLM" (TASK-014 a TASK-019) está completo.**
- **TASK-020** — concluída (modelo de `Execution`,
  `backend/app/orchestrator/execution.py` — ver `docs/tasks/TASK-020.md`).

**Checkpoint de 10 TASKs (AGENTS.md):** com a TASK-020, a `main` local foi
enviada ao GitHub, `docs/HANDOFF.md` atualizado, e as branches `task-003` a
`task-020` (até então só locais) foram sincronizadas com o remoto a pedido do
usuário.

- **TASK-021** — concluída (`execution_id`,
  `backend/app/orchestrator/execution_id.py`, `Execution.new()` — ver
  `docs/tasks/TASK-021.md`).
- **TASK-022** — concluída (`ExecutionPolicy`,
  `backend/app/policies/execution_policy.py` — ver
  `docs/tasks/TASK-022.md`).
- **TASK-023** — concluída (`ExecutionOrchestrator`,
  `backend/app/orchestrator/orchestrator.py`, primeiro ciclo real de um
  passo — ver `docs/tasks/TASK-023.md`).
- **TASK-024** — concluída (planejamento inicial,
  `backend/app/orchestrator/planner.py` — ver `docs/tasks/TASK-024.md`).
- **TASK-025** — concluída (validação de plano,
  `backend/app/orchestrator/plan_validator.py`, novos códigos de erro
  4002/4003 — ver `docs/tasks/TASK-025.md`).
- **TASK-026** — concluída (execução por etapas,
  `Execution.observations`/`set_last_observation`,
  `ExecutionOrchestrator.run_until_response` — ver
  `docs/tasks/TASK-026.md`).
- **TASK-027** — concluída (replanejamento completo,
  `backend/app/orchestrator/replanner.py` — ver `docs/tasks/TASK-027.md`).
- **TASK-028** — concluída (`max_steps` aplicado em `run_step`, novo código
  de erro 4004 — ver `docs/tasks/TASK-028.md`).
- **TASK-029** — concluída (detecção de loop,
  `backend/app/orchestrator/loop_detector.py`, novo código de erro 4005 —
  ver `docs/tasks/TASK-029.md`).
- **TASK-030** — concluída (cancelamento, `ExecutionStatus.CANCELLED`,
  `backend/app/orchestrator/cancellation.py` — ver
  `docs/tasks/TASK-030.md`). Suíte completa: 247/247 testes aprovados.
  **Com esta TASK, o bloco "Orquestração" (TASK-020 a TASK-030) está
  completo.**

**Checkpoint de 10 TASKs (AGENTS.md):** próximo checkpoint automático de
push da `main` + atualização de `docs/HANDOFF.md` é na TASK-040.

- **TASK-031** — concluída (confiança do modelo,
  `backend/app/confidence/model_confidence.py` — ver
  `docs/tasks/TASK-031.md`).
- **TASK-032** — concluída (volatilidade,
  `backend/app/confidence/volatility.py` — ver `docs/tasks/TASK-032.md`).
  Suíte completa: 263/263 testes aprovados.
- **TASK-033** — concluída (confidence engine,
  `backend/app/confidence/confidence_engine.py`,
  `EvidenceStrength`/`calculate_final_confidence` — ver
  `docs/tasks/TASK-033.md`). Suíte completa: 275/275 testes aprovados.
- **TASK-034** — concluída (bloqueio de resposta conclusiva em LOW,
  `backend/app/confidence/response_guardrail.py`,
  `ensure_conclusive_response_allowed`, novo código de erro 4006 — ver
  `docs/tasks/TASK-034.md`). Suíte completa: 278/278 testes aprovados.
- **TASK-035** — concluída (regra obrigatória para informação volátil,
  `backend/app/confidence/revalidation_guardrail.py`,
  `ensure_volatile_information_revalidated`, novo código de erro 4007 — ver
  `docs/tasks/TASK-035.md`). Suíte completa: 282/282 testes aprovados.
- **TASK-036** — concluída (tratamento de ambiguidade,
  `backend/app/confidence/ambiguity_guardrail.py`,
  `ensure_ambiguity_resolved_before_response`, novo código de erro 4008 —
  ver `docs/tasks/TASK-036.md`). Suíte completa: 286/286 testes aprovados.
  **Com esta TASK, o bloco "Confiança e guardrails" (TASK-031 a TASK-036)
  está completo.**

**Checkpoint de 10 TASKs (AGENTS.md):** próximo checkpoint automático de
push da `main` + atualização de `docs/HANDOFF.md` é na TASK-040.

- **TASK-037** — concluída (`ContextManager`,
  `backend/app/context/context_manager.py` — ver `docs/tasks/TASK-037.md`).
  Suíte completa: 290/290 testes aprovados.
- **TASK-038** — concluída (assunto principal,
  `ContextManager.set_active_topic` — ver `docs/tasks/TASK-038.md`). Suíte
  completa: 294/294 testes aprovados.
- **TASK-039** — concluída (rastreamento de entidades/referências,
  `ContextManager.track_entity`/`set_implicit_reference`/
  `resolve_reference` — ver `docs/tasks/TASK-039.md`). Suíte completa:
  303/303 testes aprovados.
- **TASK-040** — concluída (correção de contexto,
  `ContextManager.record_correction` — ver `docs/tasks/TASK-040.md`). Suíte
  completa: 306/306 testes aprovados.

**Checkpoint de 10 TASKs (AGENTS.md):** com a TASK-040, a `main` local foi
enviada ao GitHub e `docs/HANDOFF.md` atualizado.

- **TASK-041** — concluída (detecção de troca de assunto,
  `ContextManager.detect_topic_switch` — ver `docs/tasks/TASK-041.md`).
  Suíte completa: 311/311 testes aprovados.
- **TASK-042** — concluída (monitor de janela de contexto,
  `backend/app/context/context_window.py`, `ContextWindowMonitor` — ver
  `docs/tasks/TASK-042.md`). Suíte completa: 318/318 testes aprovados.
- **TASK-043** — concluída (aviso em 80%,
  `ContextWindowMonitor.requires_warning` — ver `docs/tasks/TASK-043.md`).
  Suíte completa: 323/323 testes aprovados. **Com esta TASK, o bloco
  "Contexto" (TASK-037 a TASK-043) está completo.**
- **TASK-044** — concluída (modelo de memória persistente, schema
  `backend/app/db/migrations/0003_memory.sql`,
  `backend/app/memory/memory_model.py` — ver `docs/tasks/TASK-044.md`).
  Suíte completa: 327/327 testes aprovados.
- **TASK-045** — concluída (separação de memória por usuário/aplicação,
  `list_memories_for_owner` — ver `docs/tasks/TASK-045.md`). Suíte
  completa: 331/331 testes aprovados.
- **TASK-046** — concluída (Memory Tool,
  `backend/app/tools/memory_tool.py`, `execute_memory_tool` — ver
  `docs/tasks/TASK-046.md`). Suíte completa: 341/341 testes aprovados.
- **TASK-047** — concluída (busca estruturada de memória,
  `search_memories`, operação `SEARCH` na Memory Tool — ver
  `docs/tasks/TASK-047.md`). Suíte completa: 353/353 testes aprovados.
- **TASK-048** — concluída (relevância/frequência/last used,
  `record_memory_usage`/`relevance_score` — ver `docs/tasks/TASK-048.md`).
  Suíte completa: 361/361 testes aprovados.
- **TASK-049** — concluída (política de retenção,
  `backend/app/memory/retention_policy.py`, `apply_retention_policy` — ver
  `docs/tasks/TASK-049.md`). Suíte completa: 370/370 testes aprovados.
- **TASK-050** — concluída (limite fixo de memória,
  `MAX_MEMORIES_PER_OWNER = 500`, `enforce_memory_limit` — ver
  `docs/tasks/TASK-050.md`). Suíte completa: 373/373 testes aprovados.
- **TASK-051** — concluída (auditoria de memória removida, tabela
  `memory_removal_audit`, `delete_memory(reason)`/
  `list_removal_audit_for_owner` — ver `docs/tasks/TASK-051.md`). Suíte
  completa: 379/379 testes aprovados. **Com esta TASK, o bloco "Memória"
  (TASK-044 a TASK-051) está completo.**
- **TASK-052** — concluída (modelo RAW/PROVISIONAL/CONFIRMED,
  `backend/app/knowledge/knowledge_model.py`, `KnowledgeStatus`/
  `advance_knowledge_status` — ver `docs/tasks/TASK-052.md`). Suíte
  completa: 391/391 testes aprovados.
- **TASK-053** — concluída (Knowledge Tool,
  `backend/app/tools/knowledge_tool.py`, `execute_knowledge_tool` — ver
  `docs/tasks/TASK-053.md`). Suíte completa: 402/402 testes aprovados.
- **TASK-054** — concluída (versionamento de conhecimento,
  `create_new_version`/`get_current_version`/`list_version_history` — ver
  `docs/tasks/TASK-054.md`). Suíte completa: 419/419 testes aprovados.
- **TASK-055** — concluída (escopo GLOBAL/APPLICATION,
  `KnowledgeScope`/`list_knowledge_for_scope` — ver
  `docs/tasks/TASK-055.md`). Suíte completa: 434/434 testes aprovados.
- **TASK-056** — concluída (evidências/confiança/volatilidade,
  `set_knowledge_confidence`/`set_knowledge_volatility`/`add_evidence` —
  ver `docs/tasks/TASK-056.md`). Suíte completa: 456/456 testes
  aprovados.
- **TASK-057** — concluída (regra de promoção para CONFIRMED,
  `backend/app/knowledge/promotion_rule.py`, `promote_to_confirmed` —
  ver `docs/tasks/TASK-057.md`). Suíte completa: 470/470 testes
  aprovados.
- **TASK-058** — concluída (avaliação de utilidade pelo orquestrador,
  `backend/app/knowledge/usefulness.py`, `is_useful_for_orchestrator` —
  ver `docs/tasks/TASK-058.md`). Suíte completa: 471/471 testes
  aprovados. **Com esta TASK, o bloco "Conhecimento" (TASK-052 a
  TASK-058) está completo.**
- **TASK-059** — concluída (cadastro de fontes,
  `backend/app/sources/source_registry.py`, `register_source` — ver
  `docs/tasks/TASK-059.md`). Suíte completa: 482/482 testes aprovados.
- **TASK-060** — concluída (tipo de fonte PRIMARY/SECONDARY/UNKNOWN,
  `SourceType`/`set_source_type` — ver `docs/tasks/TASK-060.md`). Suíte
  completa: 487/487 testes aprovados.

**Checkpoint de 10 TASKs (AGENTS.md):** com a TASK-060, a `main` local foi
enviada ao GitHub e `docs/HANDOFF.md` atualizado.

- **TASK-061** — concluída (reputação LOW/MEDIUM/HIGH,
  `SourceReputation`/`set_source_reputation` — ver
  `docs/tasks/TASK-061.md`). Suíte completa: 492/492 testes aprovados.
- **TASK-062** — concluída (atualização de reputação,
  `backend/app/sources/reputation_rule.py`, `update_source_reputation` —
  ver `docs/tasks/TASK-062.md`). Suíte completa: 502/502 testes
  aprovados.
- **TASK-063** — concluída (histórico de reputação,
  `ReputationHistoryEntry`/`list_reputation_history` — ver
  `docs/tasks/TASK-063.md`). Suíte completa: 508/508 testes aprovados.
- **TASK-064** — concluída (blacklist de fontes,
  `block_source`/`unblock_source`/`list_blacklist_entries` — ver
  `docs/tasks/TASK-064.md`). Suíte completa: 522/522 testes aprovados.
- **TASK-065** — concluída (bloqueio automático,
  `backend/app/sources/auto_block_rule.py`,
  `auto_block_after_validation` — ver `docs/tasks/TASK-065.md`). Suíte
  completa: 529/529 testes aprovados.
- **TASK-066** — concluída (desbloqueio somente ADMIN,
  `backend/app/sources/unblock_rule.py`, `admin_unblock_source` — ver
  `docs/tasks/TASK-066.md`). Suíte completa: 536/536 testes aprovados.
  **Com esta TASK, o bloco "Fontes" (TASK-059 a TASK-066) está
  completo.**
- **TASK-067** — concluída (API local do Claudião, `backend/app/api/`,
  FastAPI — DEC-009 — ver `docs/tasks/TASK-067.md`). Suíte completa:
  543/543 testes aprovados.
- **TASK-068** — concluída (validação de payload,
  `backend/app/api/schemas.py`, `ExecutionRequest` — ver
  `docs/tasks/TASK-068.md`). Suíte completa: 556/556 testes aprovados.
- **TASK-069** — concluída (execução síncrona,
  `backend/app/api/dependencies.py`, `ExecutionOrchestrator.
  run_until_response` conectado a `POST /v1/executions` — ver
  `docs/tasks/TASK-069.md`). Suíte completa: 560/560 testes aprovados.
- **TASK-070** — concluída (timeout definido pela aplicação aplicado de
  fato, `backend/app/api/executions.py`, `ThreadPoolExecutor` +
  `future.result(timeout=...)` cancelando o `CancellationToken`
  compartilhado — código `APPLICATION_TIMEOUT_EXCEEDED`, `4009`, HTTP
  `504` — ver `docs/tasks/TASK-070.md`). Suíte completa: 562/562 testes
  aprovados.
- **TASK-071** — concluída (erro de timeout com formato específico,
  `_timeout_error_details` em `backend/app/api/executions.py` —
  `current_step`/`active_tool` nos `details` de
  `APPLICATION_TIMEOUT_EXCEEDED` — ver `docs/tasks/TASK-071.md`). Suíte
  completa: 565/565 testes aprovados.
- **TASK-072** — concluída (resposta JSON final, `build_success_response`
  em novo `backend/app/api/responses.py`, espelhando `build_error_response`
  — `{"success": true, "data": {...}}` — ver `docs/tasks/TASK-072.md`).
  Suíte completa: 567/567 testes aprovados.
- **TASK-073** — concluída (rastreio de consumo, novo
  `backend/app/usage/usage_model.py`, `record_usage`/
  `list_usage_for_application`, tabela `usage_records` — ver
  `docs/tasks/TASK-073.md`). Suíte completa: 571/571 testes aprovados.
  **Com esta TASK, o bloco "Aplicações" (TASK-067 a TASK-073) está
  completo.**
- **TASK-074** — concluída (fila FIFO em memória, novo
  `backend/app/queue/queue_model.py`, `QueueItem`/`FifoQueue` — ver
  `docs/tasks/TASK-074.md`). Suíte completa: 589/589 testes aprovados.
- **TASK-075** — concluída (fila persistida no PostgreSQL,
  `save_queue_item`/`get_queue_item`/`list_queue_items`, tabela
  `queue_items` — ver `docs/tasks/TASK-075.md`). Suíte completa:
  597/597 testes aprovados.
- **TASK-076** — concluída (estados da fila aplicados a um item já
  persistido, `start_queue_item`/`complete_queue_item`/
  `fail_queue_item`/`list_queue_items_by_status` — ver
  `docs/tasks/TASK-076.md`). Suíte completa: 610/610 testes aprovados.
- **TASK-077** — concluída (retenção/limpeza da fila, novo
  `backend/app/queue/retention_policy.py`,
  `is_eligible_for_retention_removal`/`apply_retention_policy`,
  `DEFAULT_MAX_AGE_DAYS = 7.0` — ver `docs/tasks/TASK-077.md`). Suíte
  completa: 624/624 testes aprovados. **Com esta TASK, o bloco "Fila"
  (TASK-074 a TASK-077) está completo.**
- **TASK-078** — concluída (Execution Trace, novo
  `backend/app/observability/execution_trace.py`, `ExecutionTrace` — ver
  `docs/tasks/TASK-078.md`). Suíte completa: 640/640 testes aprovados.
- **TASK-079** — concluída (Execution Trace conectado ao
  `ExecutionOrchestrator` de verdade, `trace` opcional em
  `run_step`/`run_until_response`, `step_durations`/`tool_durations` —
  ver `docs/tasks/TASK-079.md`). Suíte completa: 654/654 testes
  aprovados.
- **TASK-080** — concluída (métricas básicas, novo
  `backend/app/observability/metrics.py` —
  `success_rate`/`average_duration_seconds`/`average_step_count`/
  `tool_usage_counts`/`request_count_by_status`, 5 lacunas conhecidas
  documentadas sem fonte de dado real ainda — ver
  `docs/tasks/TASK-080.md`). Suíte completa: 668/668 testes aprovados.
- **TASK-081** — concluída (painel web read-only, novo
  `backend/app/panel/routes.py`, `GET /panel` mostrando a fila real —
  ver `docs/tasks/TASK-081.md`). Suíte completa: 676/676 testes
  aprovados.
- **TASK-082** — concluída (execuções no painel; Execution Trace
  persistido no PostgreSQL — `DEC-010`, decisão pedida ao usuário via
  `AskUserQuestion` — tabela `execution_traces`,
  `save_execution_trace`/`get_execution_trace`/`list_execution_traces`
  — ver `docs/tasks/TASK-082.md`). Suíte completa: 688/688 testes
  aprovados.
- **TASK-083** — concluída (erros/logs/consumo no painel —
  `list_failed_execution_traces`/`list_recent_logs`/
  `list_recent_usage_records` — ver `docs/tasks/TASK-083.md`). Suíte
  completa: 707/707 testes aprovados. **Com esta TASK, o bloco
  "Observabilidade inicial" (TASK-078 a TASK-083) está completo.**
- **TASK-084** — concluída (CLI/chat de teste, novo `scripts/chat.py` —
  cliente HTTP puro de `POST /v1/executions`, `create-application`/`chat`
  — ver `docs/tasks/TASK-084.md`). Suíte completa: 718/718 testes
  aprovados.
- **TASK-085** — concluída (health check inicial, novo
  `backend/app/observability/health_check.py`, `GET /health`
  (`backend/app/api/health.py`), rodado também no `lifespan` de
  inicialização — ver `docs/tasks/TASK-085.md`). Suíte completa:
  732/732 testes aprovados.
- **TASK-086** — concluída (suíte mínima de testes críticos, novo
  `tests/scenarios/test_minimum_usable_scenario.py`; `tests/integration/
  conftest.py` movido para `tests/conftest.py` — ver
  `docs/tasks/TASK-086.md`). Suíte completa: 734/734 testes aprovados.
- **TASK-087** — concluída (**marco: primeiro Claudião utilizável em
  produção controlada**. Modelo `qwen3:8b` baixado via `ollama pull`
  — `DEC-011`, decisão pedida ao usuário via `AskUserQuestion` — e
  configurado em `CLAUDIAO_ACTIVE_MODEL`; validação real de ponta a
  ponta com servidor/PostgreSQL/Ollama reais, sem fakes: health check
  saudável, aplicação criada via `scripts/chat.py`, execução completa
  com resposta real do modelo (~52s), conferida em `usage_records`/
  `execution_traces`/painel; caminho de timeout real também exercitado.
  Novo cenário fixo `test_scenario_real_model_completes_a_real_objective`
  em `tests/scenarios/test_minimum_usable_scenario.py`. Bug real
  encontrado e corrigido em 3 testes de logging que assumiam
  incorretamente que `CLAUDIAO_POSTGRES_*` nunca estaria presente na
  coleta do pytest — ver `docs/tasks/TASK-087.md`). Suíte completa:
  735/735 testes aprovados (0 pulados) com `config/.env` carregado;
  734 aprovados + 1 pulado sem ele (portabilidade esperada).

- **TASK-088** — concluída (interface `WebSearchProvider`, novo
  `backend/app/web_search/provider.py` — `SearchRequest`/
  `SearchResponse`/`SearchResult`/`SearchPurpose`/
  `WebSearchProviderError`, mesmo padrão de `LocalLLMProvider`
  (TASK-014); só a interface, sem provider concreto — ver
  `docs/tasks/TASK-088.md`). Suíte completa: 742/742 testes aprovados.
  **Com esta TASK, o bloco "Web" (TASK-088 a TASK-094) começa.**

As demais 59 TASKs permanecem com status **Pendente**.

Próxima TASK executável: **TASK-089 — Implementar primeiro provider de
busca**. Com o marco do primeiro Claudião utilizável certificado
(TASK-087), o restante da V1 (TASK-088 a TASK-147) completa o escopo —
ver `docs/V1_SCOPE.md`.

Este documento é atualizado a cada TASK concluída (etapa "Encerramento" do workflow
em `AGENTS.md`), registrando data de conclusão e um resumo curto — no mesmo espírito
de rastreabilidade do AIShoppingAgent, mas sem copiar conteúdo daquele projeto.
