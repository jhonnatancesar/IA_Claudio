# Backup, restore e rollback

Fonte: seção 42 da especificação mestre.

O painel permite backup manual e agendado, backup completo ou seletivo (memória,
conhecimento e configurações), e destino alternativo, inclusive outro banco.

## Integridade

Todo backup passa por verificação de integridade. Estados sugeridos:

```
CREATED → VERIFYING → VALID / FAILED
```

## Restore / rollback

- Exige confirmação e senha do `ADMIN`.
- Entra automaticamente em modo de manutenção (ver `OPERATIONS.md`).
- Antes de restaurar, o sistema faz **backup automático do estado atual** e valida
  esse backup — nunca restaura sem uma rede de segurança do estado corrente.
- Health check obrigatório depois de restore/rollback (ver `OPERATIONS.md`).

## TASKs relacionadas

TASK-126 a TASK-130: backup manual, backup agendado, verificação de integridade,
restore, backup pré-restore.
