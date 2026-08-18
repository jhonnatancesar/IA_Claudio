# Banco de dados

Fonte: seção 23 da especificação mestre. Ver `docs/OPEN_QUESTIONS.md` para o que ainda
não foi decidido (linguagem/ORM/ferramenta de migration).

## Decisão já aprovada

Um único **PostgreSQL local**, na mesma máquina do agente, com **separação lógica**
por tabelas/estruturas e uso de **JSONB** onde fizer sentido.

## Domínios de dados

- usuários
- aplicações
- memória
- conhecimento
- fontes
- histórico de fontes
- blacklist
- conversas
- resumos
- execuções
- fila
- logs
- auditoria
- cotas
- configurações
- atualizações
- backups

## Instância local (TASK-003)

PostgreSQL 17 instalado localmente (serviço Windows `postgresql-x64-17`, porta 5432).
Banco do projeto: `claudiao`, de propriedade do role de aplicação `claudiao_app`
(login próprio, sem privilégio de superusuário). O superusuário `postgres` existe
apenas para uso administrativo/manutenção, não para a aplicação.

Credenciais reais ficam **somente** em `config/.env` (nunca versionado — ver
`.gitignore`); `config/.env.example` documenta os nomes das variáveis, sem valores
reais.

## Schema inicial (TASK-004)

Aplicado em `backend/app/db/migrations/0001_initial_schema.sql` (SQL puro via
`psql`, sem ferramenta de migration dedicada — ver `docs/OPEN_QUESTIONS.md`, item 1):

- `schema_migrations` — registro básico das migrations aplicadas.
- `users` — usuários humanos, com `role` (`ADMIN`/`USER`, seção 31 da especificação)
  e hash de senha.
- `applications` — aplicações externas, com hash da API key.
- `settings` — configurações administráveis em runtime pelo painel (`docs/PANEL.md`),
  distintas do arquivo de bootstrap `config/.env*` (TASK-002).

## Logs (TASK-006)

`backend/app/db/migrations/0002_logs.sql` — tabela `logs` (`timestamp`, `level`,
`logger`, `message`, `context jsonb`), índices em `timestamp` e `level`. Ver
`docs/OBSERVABILITY.md` para o handler que grava nela.

## Memória (TASK-044, TASK-048, TASK-051)

`backend/app/db/migrations/0003_memory.sql` — tabela `memories` (`id`,
`owner_type` — `USER`/`APPLICATION` —, `owner_id`, `content`, `created_at`,
`updated_at`), índice em `(owner_type, owner_id)`.
`backend/app/db/migrations/0004_memory_usage.sql` — colunas `use_count`
(frequência) e `last_used_at` (last used), TASK-048.
`backend/app/db/migrations/0005_memory_removal_audit.sql` — tabela
`memory_removal_audit` (`memory_id`, `owner_type`, `owner_id`, `reason`,
`removed_at`, sem `content`), índice em `(owner_type, owner_id)`, TASK-051.
Ver `docs/MEMORY.md` para o módulo (`app.memory.memory_model`) que
lê/grava nelas.

## Conhecimento (TASK-052, TASK-054)

`backend/app/db/migrations/0006_knowledge.sql` — tabela `knowledge`
(`id`, `status` — `RAW`/`PROVISIONAL`/`CONFIRMED` —, `content`,
`created_at`, `updated_at`).
`backend/app/db/migrations/0007_knowledge_versioning.sql` — colunas
`root_id`/`version`/`is_current`/`previous_version_id`/`change_reason`,
índice único parcial garantindo uma única versão atual por linhagem
(`root_id`), TASK-054. Ver `docs/KNOWLEDGE.md` para o módulo
(`app.knowledge.knowledge_model`) que lê/grava nela.

Os demais domínios de dados (fontes, histórico de fontes, blacklist,
conversas, resumos, execuções, fila, auditoria, cotas, atualizações,
backups) ainda não têm schema — cada um ganha o seu na TASK do bloco funcional
correspondente, conforme `docs/BACKLOG.md`.

## TASKs relacionadas

TASK-003 (configurar PostgreSQL local) e TASK-004 (schema inicial). Os demais
domínios de dados (memória, conhecimento, fontes, fila, execuções, etc.) ganham schema
próprio nas TASKs dos respectivos blocos funcionais, conforme `docs/BACKLOG.md`.
