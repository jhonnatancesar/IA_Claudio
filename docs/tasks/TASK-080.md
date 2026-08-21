# TASK-080 — Criar métricas básicas

Status: **Concluída em 2026-08-21**

## Objetivo

Criar métricas básicas, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Observabilidade inicial") e `docs/OBSERVABILITY.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Observabilidade inicial" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/OBSERVABILITY.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-079 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/OBSERVABILITY.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do Execution Trace/métricas e, quando aplicável, teste manual do painel read-only, conforme docs/TESTING.md.

## Documentação afetada

`docs/OBSERVABILITY.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-21. Novo `backend/app/observability/metrics.py`:
funções puras agregando sobre `list[ExecutionTrace]`
(TASK-078/079) ou `list[UsageRecord]` (TASK-073), sem ler o banco
sozinhas. Cinco funções com fonte de dado real hoje: `success_rate`
(taxa de sucesso), `average_duration_seconds` (tempo médio),
`average_step_count` (número de passos), `tool_usage_counts` (uso de
ferramentas, por frequência) e `request_count_by_status` (consumo —
número de requisições por status). `failure_counts_by_error_code`
existe e está correta, mas hoje devolve sempre `{}` na prática, já que
nada chama `ExecutionTrace.record_error` (decisão de escopo da
TASK-079).

Da lista de 10 métricas em `docs/OBSERVABILITY.md`, 5 (mais uma
genérica de erros por código) ficaram com implementação real; as outras
5 — "uso correto/incorreto de ferramentas" (só frequência é medida, não
correção), "falhas por ferramenta/provider", "respostas bloqueadas por
baixa confiança" (guardrails de confiança ainda não acoplados ao
orquestrador real, TASK-088+), "replanejamentos" e "erros por
provider" — não têm hoje nenhuma fonte de dado real no sistema
(nenhuma TASK anterior gravou esse sinal em lugar nenhum), documentadas
como lacunas conhecidas explícitas no módulo e em `docs/OBSERVABILITY.md`,
mesmo espírito da lacuna de retenção de logs já registrada antes.
Construir essa coleta de dado é trabalho de conexão futuro (mesmo tipo
de trabalho que a TASK-079 fez para etapas/tempos) — inventá-la agora
seria adiantar funcionalidade não pedida por esta TASK.

14 testes unitários novos em `tests/unit/test_metrics.py` (cada função
isolada — lista vazia, casos normais, agregação através de múltiplos
traces/registros). Suíte completa: 668/668 testes aprovados, zero
pulados (Ollama verificado rodando antes da execução).
