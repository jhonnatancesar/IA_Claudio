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

**Implementação (TASK-085):** `backend/app/observability/health_check.py`
— `run_health_check()` roda as cinco checagens acima e devolve um
`HealthCheckResult` (`healthy` + lista de `HealthCheckItem`,
`OK`/`FAILED`/`SKIPPED` por item). `modelo/runtime`
(`OllamaProvider().is_available()`, TASK-015), `postgresql` (`SELECT 1`
de verdade), `fila` (`list_queue_items()` não levanta, TASK-075) e
`configurações críticas` (`CLAUDIAO_ACTIVE_MODEL` definida + chave
mestra carregável, TASK-013) têm checagem real hoje.
`ferramentas/providers principais` fica `SKIPPED` (não `FAILED`) —
nenhuma ferramenta existe ainda (Tool Registry, TASK-088+), não há o
que checar.

Chamada uma vez no evento de inicialização
(`_lifespan`/`app.api.app`, TASK-085) — o único dos quatro eventos da
especificação alcançável hoje (saída de manutenção/atualização/
restore são TASK-123+) — e exposta sob demanda em `GET /health`
(`app.api.health`), sem autenticação (mesmo padrão do painel,
TASK-081), para quando as TASKs futuras precisarem chamá-la de novo.
HTTP `200` se saudável, `503` caso contrário. Cada item `FAILED` é
registrado via `logger.error` (primeira conexão real de código de
aplicação ao logging estruturado — até aqui nada chamava
`logger.error`/`warning` em nenhum ponto real, lacuna registrada na
TASK-083).

Ao ligar a máquina de desenvolvimento pela primeira vez com este
health check, ele expôs uma lacuna real: `CLAUDIAO_MASTER_KEY_PATH`
nunca tinha sido configurada em `config/.env` (TASK-013 previa geração
automática no primeiro uso, mas o caminho em si nunca foi definido) —
corrigido nesta TASK. `CLAUDIAO_ACTIVE_MODEL` continua deliberadamente
não configurado (`docs/OPEN_QUESTIONS.md`, item 3, decisão do usuário
ainda pendente) — por isso `configurações críticas` reporta `FAILED` e
o health check geral fica `healthy: false` nesta máquina até essa
decisão ser tomada; comportamento correto, não um defeito.

## Reinício

O painel tem botão de reinício controlado. Exige confirmação, senha do `ADMIN` e
auditoria (mesmas regras de ação crítica descritas em `PANEL.md`).

## TASKs relacionadas

TASK-085 (health check inicial), TASK-123 a TASK-125 (modo manutenção,
cancelamento/limpeza de fila em manutenção, reinício pelo painel).
