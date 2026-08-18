# Memória

Fonte: seção 11 da especificação mestre.

Memória é **separada de conhecimento** (ver `KNOWLEDGE.md`) e separada de contexto
imediato.

## Contexto imediato

Estado da conversa atual. **Não é memória permanente** — vive só durante a execução/
conversa corrente (ver `ORCHESTRATOR.md`).

## Memória persistente

Armazena preferências, decisões, fatos pessoais úteis, histórico importante e
informações necessárias à continuidade.

- Escopos mínimos: `USER` e `APPLICATION`.
- Usuários diferentes têm memórias separadas.
- Aplicações podem enviar contexto temporário sem que o agente o persista
  automaticamente — persistência é uma decisão do agente, não um efeito colateral
  automático de receber contexto.

**Implementação (TASK-044):** schema em
`backend/app/db/migrations/0003_memory.sql` — tabela `memories`
(`id`, `owner_type` — `USER`/`APPLICATION` —, `owner_id`, `content`,
`created_at`, `updated_at`). `backend/app/memory/memory_model.py`:
`Memory` (dataclass), `save_memory(owner_type, owner_id, content)` e
`get_memory(memory_id)`, persistência real via `psycopg`, mesmo padrão de
`app.auth.users` (TASK-009). `owner_type`/`owner_id` já existem no schema,
mas garantir que uma consulta só devolve memórias do próprio dono
(separação de fato) é TASK-045, não implementado aqui — `get_memory` busca
só pelo `id`, sem filtrar por dono.

## Limpeza

- A memória pode ser removida automaticamente por idade, baixa relevância, pouco uso e
  limite máximo.
- Se voltar a ser usada antes da limpeza, a vida útil é renovada.
- Quando removida, o conteúdo pode desaparecer, mas fica **auditoria mínima**
  informando que existiu, quando foi removida e por qual regra.
- O limite máximo de memória por usuário/aplicação é **fixo na V1** (valor exato a
  definir durante a implementação da TASK correspondente — TASK-050).
- Ao atingir o limite, remove primeiro as memórias menos relevantes e menos usadas
  recentemente.

## TASKs relacionadas

TASK-044 a TASK-051 (ver `docs/BACKLOG.md`): modelo de memória, separação por
usuário/aplicação, Memory Tool, busca estruturada, relevância/frequência/last used,
política de retenção, limite fixo, auditoria de remoção.
