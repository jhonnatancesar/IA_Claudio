# TASK-085 — Criar health check inicial

Status: **Concluída em 2026-08-21**

## Objetivo

Criar health check inicial, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Marco utilizável inicial") e `docs/OPERATIONS.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Marco utilizável inicial" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/OPERATIONS.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-084 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/OPERATIONS.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Cenário real fixo cobrindo o fluxo ponta a ponta envolvido; ver detalhamento específico abaixo.

## Documentação afetada

`docs/OPERATIONS.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-21. Novo `backend/app/observability/health_check.py`
— `run_health_check()` checa `modelo/runtime`
(`OllamaProvider().is_available()`, TASK-015), `postgresql` (`SELECT 1`
real), `fila` (`list_queue_items()`, TASK-075), `ferramentas/providers
principais` (`SKIPPED` — nada existe ainda, Tool Registry TASK-088+) e
`configurações críticas` (`CLAUDIAO_ACTIVE_MODEL` + chave mestra
carregável, TASK-013). `HealthCheckResult.healthy` é `False` só se
algum item `FAILED` (`SKIPPED` não conta como problema). Cada `FAILED`
vira `logger.error`; um resumo vira `INFO`/`WARNING` — primeira conexão
real de código de aplicação ao logging estruturado (TASK-005/006, até
aqui só exercitado pelos próprios testes de observabilidade).

Chamada uma vez no evento de inicialização — novo `_lifespan`
(`backend/app/api/app.py`, substitui `@app.on_event("startup")`,
obsoleto no FastAPI desta versão) — e exposta sob demanda em `GET
/health` (novo `backend/app/api/health.py`, sem autenticação, mesmo
padrão do painel TASK-081) para os outros eventos da especificação
(saída de manutenção/atualização/restore, TASK-123+) chamarem de novo
quando existirem. HTTP `200` se saudável, `503` caso contrário.

**Lacuna real descoberta e corrigida:** rodar o health check pela
primeira vez contra o ambiente de desenvolvimento revelou que
`CLAUDIAO_MASTER_KEY_PATH` nunca tinha sido configurada em
`config/.env` (a TASK-013 previu geração automática da chave no
primeiro uso, mas o caminho em si nunca foi definido) — corrigido,
`config/.env` agora aponta para `config/master.key` (gerado sozinho no
primeiro load). Usei barra normal (`C:/IA/...`), não invertida — barra
invertida some ao carregar `.env` via `source` no bash (caractere de
escape), o que descobri na hora ao verificar manualmente e corrigi
antes de fechar a TASK. `CLAUDIAO_ACTIVE_MODEL` continua
deliberadamente não configurado (`docs/OPEN_QUESTIONS.md`, item 3,
decisão do usuário ainda pendente) — por isso `configurações críticas`
reporta `FAILED` e o health check geral fica `healthy: false` nesta
máquina até essa decisão ser tomada; comportamento correto do check,
não um defeito.

Verificado manualmente contra um servidor `uvicorn` real: `GET /health`
respondeu `503` com `modelo/runtime`/`postgresql`/`fila` em `OK`,
`ferramentas/providers principais` em `SKIPPED` e só `configurações
críticas` em `FAILED` (por `CLAUDIAO_ACTIVE_MODEL`); o arquivo
`config/master.key` foi criado no caminho certo.

18 testes novos: 4 unitários em `tests/unit/test_health_check.py`
(`HealthCheckResult.healthy` isolada), 6 de integração em
`tests/integration/test_health_check_integration.py` (cada checagem
real, com e sem configuração crítica) e 4 em
`tests/integration/test_health_endpoint_integration.py` (`GET /health`
real, 200/503, e o `lifespan` de inicialização rodando o health check
de verdade — via `caplog`, não a tabela `logs`, por uma lacuna
pré-existente de ordenação de import em `logging_config.py`, TASK-005,
não desta TASK). Suíte completa: 732/732 testes aprovados, zero
pulados (Ollama verificado rodando antes da execução).
