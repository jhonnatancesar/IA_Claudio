# Atualização e rollback

Fonte: seção 43 da especificação mestre.

## Atualização do software

- Sempre pelo painel administrativo.
- Origem: repositório Git.
- Atualizações disponibilizadas por flags/tags controladas; `ADMIN` escolhe
  manualmente a atualização.
- Execução agendada em janela noturna, inicialmente **00:00–03:00**.
- Atualização entra em modo de manutenção (ver `OPERATIONS.md`).
- **Health check obrigatório** após aplicar.

## Falha e rollback

- Falha ou health check reprovado gera **rollback automático**.
- A versão que falhou fica `BLOCKED` até liberação manual do `ADMIN`.
- O painel mostra etapa, erro e health check da falha.

## Histórico

Registra versão anterior, nova versão, resultado, rollback, data e `ADMIN`
responsável.

## TASKs relacionadas

TASK-131 a TASK-137: updater Git, flags/tags de versão, agendamento 00h–03h, health
check pós-update, rollback automático, bloqueio de versão com falha, histórico de
atualizações.
