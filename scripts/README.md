# Scripts operacionais

Scripts de setup, migrations e checks (equivalente ao papel de `scripts/` no
AIShoppingAgent, adaptado ao Claudião — sem nenhum script daquele projeto copiado).

- `_gen/` — scripts usados **apenas** durante a organização inicial deste repositório
  para gerar `docs/BACKLOG.md`, `docs/tasks/TASK-*.md` e os `README.md` de módulo em
  `backend/app/`, a partir dos dados da especificação mestre. Não fazem parte do
  produto; ficam versionados para permitir regenerar esses documentos se a fonte
  mudar.
- `chat.py` (TASK-084) — "chat simples de terminal para teste"
  (`docs/V1_SCOPE.md`, mínimo utilizável). Cliente HTTP puro de `POST
  /v1/executions` (`urllib.request`, biblioteca padrão) — usa a API
  exatamente como qualquer aplicação externa, sem via de entrada
  privilegiada. `python scripts/chat.py create-application <nome>` cria
  uma aplicação de teste e imprime a API key (uma única vez); `python
  scripts/chat.py chat --api-key ...` inicia o laço interativo, contra
  um servidor já rodando (`uvicorn app.api.app:app`) — o script não sobe
  seu próprio servidor.

Demais scripts operacionais do produto (setup de ambiente, pipeline de
checks, migrations) ainda não foram criados.
