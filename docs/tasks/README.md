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
  — ver `docs/tasks/TASK-007.md`).
- **TASK-008** — concluída (formato JSON padrão de erro,
  `backend/app/errors/response.py`, `ClaudiaoError` — ver
  `docs/tasks/TASK-008.md`). **Com esta TASK, o bloco "Fundação" (TASK-001 a
  TASK-008) está completo.**
- **TASK-009** — concluída (autenticação de usuários,
  `backend/app/auth/password.py` + `users.py`, PBKDF2 sem dependência nova — ver
  `docs/tasks/TASK-009.md`).
- **TASK-010** — concluída (autorização por papel, `backend/app/auth/roles.py`,
  `Role`/`is_admin`/`require_admin`, novo código de erro 2001 — ver
  `docs/tasks/TASK-010.md`). Suíte completa: 60/60 testes aprovados.

**Checkpoint de 10 TASKs (AGENTS.md):** com a TASK-010, a `main` local foi
enviada ao GitHub e `docs/HANDOFF.md` criado para permitir que outra IA
continue o trabalho.

- **TASK-011** — concluída (autenticação de aplicações via API key,
  `backend/app/auth/api_keys.py` — ver `docs/tasks/TASK-011.md`).
- **TASK-012** — concluída (criptografia de segredos, `backend/app/auth/crypto.py`,
  `Fernet`/`cryptography` — DEC-007 — ver `docs/tasks/TASK-012.md`).
- **TASK-013** — concluída (chave mestra externa ao banco,
  `backend/app/auth/master_key.py` — ver `docs/tasks/TASK-013.md`). **Com esta
  TASK, o bloco "Segurança e identidade" (TASK-009 a TASK-013) está
  completo.**
- **TASK-014** — concluída (interface `LocalLLMProvider`,
  `backend/app/llm/provider.py` — ver `docs/tasks/TASK-014.md`). Suíte
  completa: 91/91 testes aprovados.

As demais 133 TASKs permanecem com status **Pendente**.

Próxima TASK executável: **TASK-015 — Implementar OllamaProvider**.

Este documento é atualizado a cada TASK concluída (etapa "Encerramento" do workflow
em `AGENTS.md`), registrando data de conclusão e um resumo curto — no mesmo espírito
de rastreabilidade do AIShoppingAgent, mas sem copiar conteúdo daquele projeto.
