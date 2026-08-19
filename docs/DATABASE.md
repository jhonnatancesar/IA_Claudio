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

## Conhecimento (TASK-052, TASK-054, TASK-055, TASK-056)

`backend/app/db/migrations/0006_knowledge.sql` — tabela `knowledge`
(`id`, `status` — `RAW`/`PROVISIONAL`/`CONFIRMED` —, `content`,
`created_at`, `updated_at`).
`backend/app/db/migrations/0007_knowledge_versioning.sql` — colunas
`root_id`/`version`/`is_current`/`previous_version_id`/`change_reason`,
índice único parcial garantindo uma única versão atual por linhagem
(`root_id`), TASK-054.
`backend/app/db/migrations/0008_knowledge_scope.sql` — colunas
`scope_type`/`scope_id`, `CHECK` garantindo `scope_id` presente só quando
`scope_type = 'APPLICATION'`, TASK-055.
`backend/app/db/migrations/0009_knowledge_evidence.sql` — colunas
`confidence`/`volatility` (nulas por padrão) em `knowledge` e tabela
`knowledge_evidence` (`knowledge_id` com `ON DELETE CASCADE`,
`description`, `created_at`), TASK-056. Ver `docs/KNOWLEDGE.md` para o
módulo (`app.knowledge.knowledge_model`) que lê/grava nelas.

## Fontes (TASK-059, TASK-060, TASK-061, TASK-063, TASK-064)

`backend/app/db/migrations/0010_sources.sql` — tabela `sources` (`id`,
`identifier` único, `created_at`).
`backend/app/db/migrations/0011_source_type.sql` — coluna `source_type`
(`PRIMARY`/`SECONDARY`/`UNKNOWN`, padrão `UNKNOWN`), TASK-060.
`backend/app/db/migrations/0012_source_reputation.sql` — coluna
`reputation` (`LOW`/`MEDIUM`/`HIGH`, padrão `MEDIUM`), TASK-061.
`backend/app/db/migrations/0013_source_reputation_history.sql` — tabela
`source_reputation_history` (`source_id` com `ON DELETE CASCADE`,
`previous_reputation`, `new_reputation`, `changed_at`), TASK-063.
`backend/app/db/migrations/0014_source_blacklist.sql` — coluna
`is_blocked` em `sources` e tabela `source_blacklist_entries`
(`source_id` com `ON DELETE CASCADE`, `action`, `origin`, `responsible`,
`reason`, `created_at`), TASK-064. Ver `docs/TRUST_GUARDRAILS.md` para o
módulo (`app.sources.source_registry`) que lê/grava nelas.

## Rastreio de consumo (TASK-073)

`backend/app/db/migrations/0015_usage_records.sql` — tabela
`usage_records` (`id`, `application_id` com `ON DELETE CASCADE`,
`execution_id` — texto, sem FK, já que `Execution` ainda não é
persistida em tabela própria —, `status`, `created_at`), índice em
`application_id`. Ver `docs/QUOTAS.md` e `backend/app/usage/README.md`
para o módulo (`app.usage.usage_model`) que lê/grava nela — só o registro
mínimo de consumo; o sistema de cotas completo (medição de tokens/volume,
ciclo, alertas, bloqueio) é TASK-108 a TASK-114.

Os demais domínios de dados (conversas, resumos, execuções, fila,
auditoria, cotas completas, atualizações, backups) ainda não têm schema —
cada um ganha o seu na TASK do bloco funcional correspondente, conforme
`docs/BACKLOG.md`.

## TASKs relacionadas

TASK-003 (configurar PostgreSQL local) e TASK-004 (schema inicial). Os demais
domínios de dados (memória, conhecimento, fontes, fila, execuções, etc.) ganham schema
próprio nas TASKs dos respectivos blocos funcionais, conforme `docs/BACKLOG.md`.
