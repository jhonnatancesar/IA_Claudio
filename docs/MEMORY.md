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
`app.auth.users` (TASK-009). `owner_type`/`owner_id` já existem no schema;
`get_memory` busca só pelo `id`, sem filtrar por dono.

**Implementação (TASK-045):** `list_memories_for_owner(owner_type,
owner_id)` — garante de fato que "usuários diferentes têm memórias
separadas": filtra por `owner_type`/`owner_id` exatos, nunca mistura
memórias de outro dono nem de outro `owner_type` (uma aplicação e um
usuário com o mesmo `owner_id` têm listas independentes). Ordem: mais
recente primeiro.

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

**Implementação (TASK-046):** `backend/app/tools/memory_tool.py` —
`execute_memory_tool(step)`, assinatura compatível com
`ExecutionOrchestrator.tool_executor` (`Callable[[ModelStep], str]`,
TASK-026). Traduz `step.parameters["operation"]` (`"SAVE"`/`"LIST"`/
`"SEARCH"`) em chamadas a `save_memory`/`list_memories_for_owner`/
`search_memories`: `SAVE` exige `owner_type`/`owner_id`/`content` e
devolve confirmação com o `id` gerado; `LIST` exige `owner_type`/
`owner_id` e devolve as memórias desse dono, uma por linha.
`MissingToolParameterError`/`UnknownMemoryOperationError` para parâmetro
ausente/operação desconhecida. Cadastro no Tool Registry (catálogo fixo de
ferramentas conhecidas/autorizadas) é TASK-088 em diante — esta TASK só
cria a função executável, sem se registrar em lugar nenhum.

**Implementação (TASK-047):** `search_memories(owner_type, owner_id,
query)` em `backend/app/memory/memory_model.py` — busca estruturada por
conteúdo (`content ILIKE '%query%'`, sem diferenciar maiúsculas/
minúsculas), dentro do escopo do dono (mesma garantia de separação da
TASK-045), mais recente primeiro. Exposta na Memory Tool como
`operation: "SEARCH"` (exige `owner_type`/`owner_id`/`query`).

**Implementação (TASK-048):** colunas `use_count` (frequência) e
`last_used_at` (last used) em `backend/app/db/migrations/0004_memory_usage.sql`.
`record_memory_usage(memory_id)` incrementa `use_count` e atualiza
`last_used_at` para agora (`MemoryNotFoundError` se o `id` não existir).
`relevance_score(memory, now)` combina os dois numa pontuação heurística
(mais usos + uso mais recente → maior pontuação) — critério mais simples e
defensável, já que a especificação não detalha uma fórmula de relevância.
Nenhuma das duas funções é acionada automaticamente ao ler/buscar memórias
ainda (isso ficaria a critério de quem chama).

**Implementação (TASK-049):** `backend/app/memory/retention_policy.py` —
`is_eligible_for_retention_removal(memory, now, max_age_days=180,
min_relevance=0.05)` (função pura): elegível quando **ambos** valem —
idade desde `created_at` além de `max_age_days` **e** `relevance_score`
abaixo de `min_relevance` (combina "baixa relevância" e "pouco uso" num só
sinal, TASK-048; "idade" é critério separado). `apply_retention_policy
(owner_type, owner_id, now, ...)` remove de fato as memórias elegíveis
desse dono (`delete_memory`, novo em `memory_model.py`) e retorna os `id`s
removidos. Os limiares padrão (180 dias, 0.05) são a escolha mais simples e
defensável, já que a especificação não define números exatos —
configuráveis por parâmetro.

**Implementação (TASK-050):** `MAX_MEMORIES_PER_OWNER = 500` — limite fixo
por dono na V1, mesmo espírito de outros limiares já definidos em código
sem decisão de arquitetura à parte (`DEFAULT_MAX_STEPS`, TASK-028;
`DEFAULT_REPEAT_THRESHOLD`, TASK-029). `enforce_memory_limit(owner_type,
owner_id, now, max_memories=MAX_MEMORIES_PER_OWNER)` — se o dono exceder o
limite, remove as excedentes começando pelas de menor `relevance_score`
("remove primeiro as memórias menos relevantes e menos usadas
recentemente", seção 11).

Auditoria da remoção (TASK-051, "guardar que existiu, quando e por qual
regra") não é desta TASK — nem `apply_retention_policy` nem
`enforce_memory_limit` deixam rastro da remoção.

## TASKs relacionadas

TASK-044 a TASK-051 (ver `docs/BACKLOG.md`): modelo de memória, separação por
usuário/aplicação, Memory Tool, busca estruturada, relevância/frequência/last used,
política de retenção, limite fixo, auditoria de remoção.
