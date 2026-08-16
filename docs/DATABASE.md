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

## Escopo desta fase

Nenhuma migration ou schema é criado nesta organização inicial. `backend/app/db/` e
`backend/app/db/migrations/` existem como esqueleto de diretório para quando as TASKs
TASK-003 e TASK-004 forem executadas (configurar PostgreSQL local e criar o schema
inicial, cobrindo usuários, aplicações, configurações e registros básicos — ver
`docs/tasks/TASK-004.md`).

## TASKs relacionadas

TASK-003 (configurar PostgreSQL local) e TASK-004 (schema inicial). Os demais
domínios de dados (memória, conhecimento, fontes, fila, execuções, etc.) ganham schema
próprio nas TASKs dos respectivos blocos funcionais, conforme `docs/BACKLOG.md`.
