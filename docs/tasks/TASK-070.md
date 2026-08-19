# TASK-070 — Implementar timeout definido pela aplicação

Status: **Concluída em 2026-08-19**

## Objetivo

Implementar timeout definido pela aplicação, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Aplicações") e `docs/API.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Aplicações" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/API.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-069 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/API.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários e de integração da API para aplicações (payload válido/inválido, timeout, execution_id, resposta final), conforme docs/TESTING.md.

## Documentação afetada

`docs/API.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-19. `timeout_seconds` do payload agora é um limite de
verdade em `POST /v1/executions` (`backend/app/api/executions.py`), não só
um valor guardado na política (TASK-069). `orchestrator.run_until_response`
roda num worker de um `ThreadPoolExecutor` de módulo; a requisição HTTP
espera o resultado com `future.result(timeout=payload.timeout_seconds)` —
isso garante um limite real mesmo quando a chamada ao modelo local em si
está travada numa única etapa `RESPOND` (cenário em que não existe outro
ponto de checagem cooperativa antes dela). Ao estourar, o
`CancellationToken` (TASK-030) compartilhado é cancelado (satisfaz "ao
estourar, o Claudião cancela a execução") e a rota devolve um erro
padronizado novo: `APPLICATION_TIMEOUT_EXCEEDED`, código `4009`, HTTP
`504` (`docs/ERROR_CATALOG.md`). Se o orquestrador estiver entre etapas
num fluxo `USE_TOOL` no momento do timeout, ele mesmo observa o
cancelamento (mecanismo já existente da TASK-030) e chama
`execution.cancel(...)` em sua própria thread — `execution` nunca é
escrita por duas threads ao mesmo tempo: a thread da requisição para de
tocá-la assim que segue pelo caminho de timeout.

Formato específico do erro (etapa atual/ferramenta ativa nos `details`) é
TASK-071, não implementado aqui — o erro desta TASK carrega só
`timeout_seconds` nos `details`.

Também corrigida uma lacuna de documentação parecida com a da TASK-069
(código `2002`): os códigos `4006`/`4007`/`4008` (guardrails de confiança,
TASK-034/035/036) já existiam em `backend/app/errors/catalog.py` mas
nunca tinham sido adicionados à tabela de `docs/ERROR_CATALOG.md` —
adicionados junto com o novo `4009` nesta TASK.

2 testes de integração novos em
`tests/integration/test_api_executions_integration.py`: um provider fake
que demora mais que `timeout_seconds` confirma que a resposta HTTP não
espera o provider travado terminar (retorna `504`/`4009` bem antes do
atraso configurado no fake); outro confirma que uma resposta mais rápida
que o timeout continua completando normalmente (sem falso positivo).
Suíte completa: 562/562 testes aprovados, zero pulados (Ollama local
verificado rodando antes da execução).
