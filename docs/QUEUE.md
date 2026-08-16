# Fila

Fonte: seção 27 da especificação mestre.

A V1 tem fila **FIFO** persistida no PostgreSQL.

## Estados

`PENDING / RUNNING / COMPLETED / FAILED`.

## Retenção e falhas

- Registros antigos são removidos conforme política de retenção.
- Em caso de falha, o item é registrado e o processamento segue para a próxima
  tarefa — **sem retry automático**. Retomada de execução interrompida fica fora da
  V1 (ver `OUT_OF_SCOPE.md`).

## Relação com manutenção

Ao entrar em modo de manutenção, todas as tarefas pendentes da fila são descartadas
(ver `OPERATIONS.md`).

## TASKs relacionadas

TASK-074 a TASK-077: criar fila FIFO, persistir no PostgreSQL, estados da fila,
retenção/limpeza.
