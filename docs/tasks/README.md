# TASKs

Cada arquivo `TASK-XXX.md` descreve uma unidade de trabalho: objetivo, escopo, fora
de escopo, dependências, critérios de aceite, testes esperados, documentação afetada
e status. Antes de executar uma TASK, leia os documentos obrigatórios definidos em
`AGENTS.md`.

A numeração e a ordem (TASK-001 a TASK-147) vêm da seção 51 da especificação mestre
(`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`) e não devem ser alteradas sem
antes apresentar uma auditoria e uma justificativa ao usuário.

Ver `docs/BACKLOG.md` para a lista agrupada por bloco funcional e `docs/ROADMAP.md`
para as fases e marcos.

## Marcos

- **TASK-087** — primeiro Claudião utilizável em produção controlada (mínimo
  utilizável seguro).
- **TASK-147** — V1 completa.

## Estado atual

Todas as 147 TASKs foram cadastradas nesta organização inicial.

- **TASK-001** — concluída (estrutura de diretórios, `.gitignore`, `git init` e
  primeiro commit — ver `docs/tasks/TASK-001.md` e `docs/DECISION_LOG.md`, DEC-003).
- **TASK-002** — concluída (`config/.env.example` expandido com os parâmetros
  previstos na especificação, todos como placeholder — ver `docs/tasks/TASK-002.md`).
- **TASK-003** — concluída (PostgreSQL 17 local instalado, banco `claudiao` criado
  com role de aplicação próprio — ver `docs/tasks/TASK-003.md` e `docs/DATABASE.md`).
- **TASK-004** — concluída (schema inicial aplicado: `users`, `applications`,
  `settings`, `schema_migrations` — ver `docs/tasks/TASK-004.md` e
  `docs/DATABASE.md`).
- **TASK-005** — concluída (linguagem do backend decidida: Python —
  `docs/DECISION_LOG.md`, DEC-005; logging local rotativo em
  `backend/app/observability/logging_config.py`, 7 testes aprovados — ver
  `docs/tasks/TASK-005.md`).
- **TASK-006** — concluída (logging estruturado no PostgreSQL, tabela `logs`,
  `postgres_log_handler.py`, driver psycopg — DEC-006; 13/13 testes aprovados,
  incluindo integração real com o banco — ver `docs/tasks/TASK-006.md`).
- **TASK-007** — concluída (catálogo interno de erros,
  `backend/app/errors/catalog.py`, 9 faixas de domínio, 3 erros seed da fundação
  — ver `docs/tasks/TASK-007.md`). Suíte completa: 31/31 testes aprovados.

As demais 140 TASKs permanecem com status **Pendente**.

Próxima TASK executável: **TASK-008 — Implementar resposta padrão de erro JSON**.

Este documento é atualizado a cada TASK concluída (etapa "Encerramento" do workflow
em `AGENTS.md`), registrando data de conclusão e um resumo curto — no mesmo espírito
de rastreabilidade do AIShoppingAgent, mas sem copiar conteúdo daquele projeto.
