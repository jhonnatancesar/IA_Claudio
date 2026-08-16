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

## Escopo desta fase

Nenhuma migration ou schema foi criada ainda. `backend/app/db/` e
`backend/app/db/migrations/` existem como esqueleto de diretório para quando a TASK
TASK-004 for executada (criar o schema inicial, cobrindo usuários, aplicações,
configurações e registros básicos — ver `docs/tasks/TASK-004.md`).

## TASKs relacionadas

TASK-003 (configurar PostgreSQL local) e TASK-004 (schema inicial). Os demais
domínios de dados (memória, conhecimento, fontes, fila, execuções, etc.) ganham schema
próprio nas TASKs dos respectivos blocos funcionais, conforme `docs/BACKLOG.md`.
