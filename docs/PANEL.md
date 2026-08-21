# Painel

Fonte: seções 37 e 38 da especificação mestre.

## Painel inicial (somente leitura)

Antes do painel administrativo completo, existe um painel web somente leitura para
acompanhar aplicações e execuções:

- fila
- execução atual
- status
- logs recentes
- erros
- consumo básico
- resultados das execuções

## Painel administrativo completo

- status geral
- logs
- erros
- métricas
- cotas
- usuários
- API keys
- providers
- ordem dos providers
- modelo ativo
- configurações
- manutenção
- reinício
- backups
- restores
- atualizações
- blacklist
- auditoria de reputação de fontes
- métricas de qualidade

## Regras de acesso e segurança

- Ações críticas exigem confirmação explícita, senha do `ADMIN` e registro no banco.
- A sessão administrativa tem logout automático por inatividade com tempo fixo na V1.
- O `ADMIN` pode visualizar a reputação e histórico das fontes, mas **não** editar a
  reputação manualmente (a reputação é calculada dinamicamente — ver
  `TRUST_GUARDRAILS.md`).

## TASKs relacionadas

- Painel read-only: TASK-081 a TASK-083.
- Painel administrativo completo: TASK-115 a TASK-122 (evolução para ADMIN, gestão de
  usuários/API keys/providers/cotas/configurações, reautenticação para ações
  críticas, logout por inatividade).

**Implementação (TASK-081):** `backend/app/panel/routes.py` — router
FastAPI incluído no mesmo `app` de `app.api.app` (sem processo/porta
separados para o painel). `GET /panel` devolve uma página HTML mínima
(sem CSS/framework) mostrando a fila (`app.queue.queue_model.
list_queue_items`, TASK-075 — já tem dado real persistido). Só
`item_id`/`status`/`created_at`/`finished_at` aparecem — nunca `payload`
(pode conter dado arbitrário de quem enfileirou). "Execução atual"/
"resultados das execuções" (TASK-082) e "logs/erros/consumo" (TASK-083)
mostram o resto depois; como `ExecutionTrace` (TASK-078/079) não é
persistido em lugar nenhum ainda, essas duas provavelmente vão exigir
uma decisão de arquitetura nova (onde guardar traces) fora do escopo
desta TASK. Sem autenticação: as regras de acesso descritas acima
(confirmação, senha do `ADMIN`, logout por inatividade) valem para o
painel **administrativo completo** (TASK-115+), não para este painel
inicial somente leitura — nenhuma TASK anterior construiu sessão de
usuário via navegador, então exigir login aqui seria inventar mecanismo
não pedido.
