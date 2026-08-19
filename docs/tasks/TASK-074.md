# TASK-074 — Criar fila FIFO

Status: **Concluída em 2026-08-19**

## Objetivo

Criar fila FIFO, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Fila") e `docs/QUEUE.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Fila" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/QUEUE.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-073 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/QUEUE.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários e de integração da fila (estados, persistência, retenção), conforme docs/TESTING.md.

## Documentação afetada

`docs/QUEUE.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-19. Criado o módulo `backend/app/queue/` — só a fila
em memória, sem banco ainda (persistência real é TASK-075, escopo
explícito da própria QUEUE.md/TASK-075). `queue_model.py`:
`QueueItemStatus` (`PENDING`/`RUNNING`/`COMPLETED`/`FAILED`, exatamente o
conjunto de `docs/QUEUE.md`); `QueueItem` (dataclass com transições
validadas — `start()`/`complete()`/`fail(error)`,
`InvalidQueueItemStateError` para transição inválida — mesmo espírito do
modelo de `Execution`, TASK-020); `FifoQueue` (`enqueue(payload)`/
`dequeue()` em ordem FIFO, `QueueEmptyError` ao tirar de fila vazia).
`dequeue()` já chama `start()` no item antes de devolvê-lo. Sem retry
automático (seção 27): uma vez `FAILED`, o item não aceita nova
transição — testado explicitamente.

`payload` é genérico (`Any`) — a fila não precisa saber o que está
enfileirando. Nenhuma TASK conecta esta fila a `POST /v1/executions`
(que continua síncrono ponta a ponta, TASK-069) — não fazia parte do
objetivo declarado.

18 testes novos em `tests/unit/test_queue_model.py` (estados de
`QueueItem`, transições inválidas, sem retry, ordem FIFO de `FifoQueue`,
fila vazia, ciclo completo). Suíte completa: 589/589 testes aprovados,
zero pulados (Ollama local verificado rodando antes da execução).
