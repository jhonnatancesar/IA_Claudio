# TASK-026 — Implementar execução por etapas

Status: **Concluída em 2026-08-16**

## Objetivo

Implementar execução por etapas, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Orquestração") e `docs/ORCHESTRATOR.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Orquestração" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/ORCHESTRATOR.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-025 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/ORCHESTRATOR.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do orquestrador para este passo do ciclo de execução, incluindo casos de erro/limite; teste de integração cobrindo o ciclo completo quando aplicável, conforme docs/TESTING.md.

## Documentação afetada

`docs/ORCHESTRATOR.md`, `docs/tasks/README.md`, `backend/app/orchestrator/README.md`

## Encerramento

Concluída em 2026-08-16. Fecha o ciclo "executa etapa → resultado volta ao
modelo → modelo interpreta" (seção 6 da especificação). Estendido
`Execution` (TASK-020): novo campo `observations` (paralelo a `steps`) e
`set_last_observation()`. `run_step` (TASK-023) passou a incluir observações
no histórico do prompt. Novo `ExecutionOrchestrator.run_until_response()`:
loop que chama `run_step`, executa `USE_TOOL` via `tool_executor`
(`ToolExecutor = Callable[[ModelStep], str]`, novo parâmetro do construtor)
e realimenta o resultado, até `RESPOND`; `ToolExecutorNotConfiguredError` se
nenhum executor foi passado. Nenhuma ferramenta real ainda — Tool Registry é
TASK-046 em diante. Sem `max_steps`/detecção de loop (TASK-028/TASK-029):
um `tool_executor` mal comportado pode gerar laço sem fim, aceito nesta
TASK. 5 testes de `Execution.observations`/`set_last_observation` + 6 de
`run_until_response` com provider e tool_executor fakes (resposta direta,
uma ferramenta, múltiplas ferramentas, observação realimentada no prompt,
executor ausente, executor que falha). Sem teste de integração novo — o
único caminho testável contra o Ollama real sem modelo baixado (erro de
modelo inexistente) já está coberto pelas TASK-023/024. Suíte completa:
212/212 testes aprovados.
