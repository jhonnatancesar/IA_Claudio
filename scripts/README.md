# Scripts operacionais

Scripts de setup, migrations e checks (equivalente ao papel de `scripts/` no
AIShoppingAgent, adaptado ao Claudião — sem nenhum script daquele projeto copiado).

- `_gen/` — scripts usados **apenas** durante a organização inicial deste repositório
  para gerar `docs/BACKLOG.md`, `docs/tasks/TASK-*.md` e os `README.md` de módulo em
  `backend/app/`, a partir dos dados da especificação mestre. Não fazem parte do
  produto; ficam versionados para permitir regenerar esses documentos se a fonte
  mudar.

Nenhum script operacional do produto (setup de ambiente, pipeline de checks,
migrations) foi criado ainda — depende da stack de implementação
(`docs/OPEN_QUESTIONS.md`).
