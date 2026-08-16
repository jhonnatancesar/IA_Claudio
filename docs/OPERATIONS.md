# Operação: manutenção, health check e reinício

Fonte: seções 39, 40 e 41 da especificação mestre.

## Modo de manutenção

- Ao ativar, cancela imediatamente a execução atual.
- Descarta todas as tarefas pendentes da fila na V1 (sem retomada — ver
  `QUEUE.md`/`OUT_OF_SCOPE.md`).
- Informa o usuário para reenviar depois; aplicações recebem erro estruturado.
- Novas tarefas são bloqueadas.
- Ao sair da manutenção, **health check obrigatório** antes de liberar uso.

## Health check

Na V1, roda apenas em eventos importantes: **inicialização, saída de manutenção,
atualização e restore/rollback**. Verifica:

- modelo/runtime
- PostgreSQL
- fila
- ferramentas/providers principais
- configurações críticas

**Sem health check periódico em background na V1.**

## Reinício

O painel tem botão de reinício controlado. Exige confirmação, senha do `ADMIN` e
auditoria (mesmas regras de ação crítica descritas em `PANEL.md`).

## TASKs relacionadas

TASK-085 (health check inicial), TASK-123 a TASK-125 (modo manutenção,
cancelamento/limpeza de fila em manutenção, reinício pelo painel).
