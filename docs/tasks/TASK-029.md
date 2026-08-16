# TASK-029 — Implementar detecção de loop

Status: **Concluída em 2026-08-16**

## Objetivo

Implementar detecção de loop, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Orquestração") e `docs/ORCHESTRATOR.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Orquestração" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/ORCHESTRATOR.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-028 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/ORCHESTRATOR.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do orquestrador para este passo do ciclo de execução, incluindo casos de erro/limite; teste de integração cobrindo o ciclo completo quando aplicável, conforme docs/TESTING.md.

## Documentação afetada

`docs/ORCHESTRATOR.md`, `docs/ERROR_CATALOG.md`, `docs/tasks/README.md`,
`backend/app/orchestrator/README.md`

## Encerramento

Concluída em 2026-08-16. A especificação (seção 30) só lista "detecção de
loop" como limite de execução, sem detalhar o critério — escolhida a
heurística mais simples e defensável: repetir exatamente a mesma decisão
(`action`/`tool`/`parameters`) um número de vezes seguidas (padrão 3) é um
loop; `RESPOND` nunca conta; parâmetros diferentes entre chamadas da mesma
ferramenta não contam (progresso real, não repetição).

Criado `backend/app/orchestrator/loop_detector.py`: `detect_loop(execution,
threshold=3)`. Integrado em `ExecutionOrchestrator.run_step` (novo parâmetro
`loop_repeat_threshold`, checado logo após `add_step` quando a etapa não é
`RESPOND`); se detectado, marca a execução `FAILED` e levanta
`ClaudiaoError` com o novo código `4005` (`LOOP_DETECTED`, HTTP 409).

Ajustados os testes de `max_steps` (TASK-028) que usavam parâmetros
idênticos em chamadas repetidas — agora disparavam detecção de loop antes
de atingir `max_steps`; corrigido variando os parâmetros a cada chamada,
isolando os dois comportamentos.

9 testes unitários do detector + 3 de integração no orquestrador (loop para
antes de `max_steps`, ferramenta com parâmetros variados não é sinalizada
como loop, threshold padrão é 3). Suíte completa: 233/233 testes aprovados.
