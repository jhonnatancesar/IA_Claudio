# Conhecimento

Fonte: seção 12 da especificação mestre.

Conhecimento é **separado da memória** (ver `MEMORY.md`) e **nunca é apagado
automaticamente**.

## Ciclo de maturidade

```
RAW → PROVISIONAL → CONFIRMED
```

Fluxo desejado: **NÃO SEI → PESQUISO → VALIDO → CONFIRMO → AVALIO UTILIDADE → SALVO.**

**Implementação (TASK-057):** `backend/app/knowledge/promotion_rule.py`
— `advance_knowledge_status` (TASK-052) só aplica a transição mecânica;
esta TASK acrescenta a regra de negócio para `PROVISIONAL → CONFIRMED`
("CONFIRMO"): `is_eligible_for_confirmation(knowledge, evidence_count)`
(função pura) exige confiança `HIGH` **e** pelo menos
`MIN_EVIDENCE_COUNT_FOR_CONFIRMATION` (`1`) evidência registrada —
critério mais simples e defensável, já que a especificação não detalha
uma fórmula. `promote_to_confirmed(knowledge_id)` busca o conhecimento e
suas evidências, verifica elegibilidade e só então chama
`advance_knowledge_status`; levanta
`KnowledgePromotionNotEligibleError` sem alterar nada quando não
elegível. Reputação real de fontes (TASK-059+) pode refinar esse
critério depois, sem mudar sua forma. Promoção `RAW → PROVISIONAL` não é
desta TASK. Exposta na Knowledge Tool como `operation:
"PROMOTE_TO_CONFIRMED"` (distinta de `"ADVANCE"`, que continua sem
julgamento).

## Versionamento

Se um fato confirmado mudar, o sistema:

- mantém a versão anterior;
- registra a nova versão;
- marca qual é a atual;
- preserva fontes, contexto e motivo da mudança.

Isto é o mesmo princípio de não reescrita silenciosa aplicado a conhecimento: uma
mudança de fato é uma **nova versão**, não uma edição da anterior.

**Implementação (TASK-052):** `backend/app/knowledge/knowledge_model.py`
— `KnowledgeStatus` (`RAW`/`PROVISIONAL`/`CONFIRMED`), `Knowledge`
(dataclass), `save_knowledge(content)` (sempre começa em `RAW`),
`get_knowledge(knowledge_id)`, `advance_knowledge_status(knowledge_id,
new_status)`. Persistência real no PostgreSQL local (schema em
`backend/app/db/migrations/0006_knowledge.sql`, tabela `knowledge`), mesmo
padrão de `app.memory.memory_model` (TASK-044) — mas sem função de
remoção, já que conhecimento nunca é apagado automaticamente.
`advance_knowledge_status` só aplica a transição *mecânica* (um passo por
vez, sempre para frente, nunca pulando nem voltando —
`InvalidKnowledgeStatusTransitionError` caso contrário); decidir *quando*
promover (com base em evidências/fontes) é a regra de promoção, TASK-057,
não implementada aqui. Versionamento de fato (TASK-054), escopo
`GLOBAL`/`APPLICATION` (TASK-055) e evidências/fontes (TASK-056) também
não são desta TASK.

**Implementação (TASK-053):** `backend/app/tools/knowledge_tool.py` —
`execute_knowledge_tool(step)`, assinatura compatível com
`ExecutionOrchestrator.tool_executor` (`Callable[[ModelStep], str]`,
TASK-026), mesmo padrão de `app.tools.memory_tool` (TASK-046). Traduz
`step.parameters["operation"]` (`"SAVE"`/`"GET"`/`"ADVANCE"`) em chamadas
a `save_knowledge`/`get_knowledge`/`advance_knowledge_status`. `ADVANCE`
só aplica a transição mecânica já validada por `advance_knowledge_status`
— decidir *quando* promover (regra de promoção baseada em evidências) é
TASK-057, não implementada aqui. Cadastro no Tool Registry (catálogo fixo)
é TASK-088 em diante.

**Implementação (TASK-054):** `create_new_version(knowledge_id,
new_content, reason)` — cria uma linha nova (`version` seguinte,
`is_current=True`, `previous_version_id`/`change_reason` preenchidos),
marca a versão anterior como não-atual, na mesma transação; nunca faz
`UPDATE` em `content`. Exige que `knowledge_id` seja a versão atual da
linhagem (`KnowledgeVersionConflictError` caso contrário). Uma versão
nova sempre começa em `RAW`, mesmo que a anterior estivesse `CONFIRMED` —
conteúdo novo ainda não foi revalidado. `get_current_version(root_id)` e
`list_version_history(root_id)` consultam a linhagem. Unicidade de "uma
versão atual por linhagem" garantida por índice único parcial no schema
(`backend/app/db/migrations/0007_knowledge_versioning.sql`). Exposta na
Knowledge Tool como `operation: "NEW_VERSION"`. Preservar fontes
(TASK-056) não é desta TASK.

## Escopos

`GLOBAL` e `APPLICATION:<id>`. Conhecimento específico de uma aplicação **não pode ser
promovido automaticamente para global** — promoção exige avaliação explícita (ver
regra de promoção, TASK-057).

**Implementação (TASK-055):** `KnowledgeScope` (`GLOBAL`/`APPLICATION`) e
`scope_id` (`str | None`) em `Knowledge`/`save_knowledge` — `GLOBAL` por
padrão; `APPLICATION` exige `scope_id` não vazio
(`InvalidKnowledgeScopeError` caso contrário, ou se `GLOBAL` vier com
`scope_id`), reforçado por `CHECK` no schema
(`backend/app/db/migrations/0008_knowledge_scope.sql`). `create_new_version`
(TASK-054) herda o escopo da versão anterior. `list_knowledge_for_scope
(scope_type, scope_id=None)` lista as versões atuais de um escopo, nunca
misturando `GLOBAL` com `APPLICATION` nem aplicações diferentes entre si.
Nenhuma função troca o escopo de um conhecimento existente — "não pode ser
promovido automaticamente para global" é satisfeito por omissão. Exposta
na Knowledge Tool: `scope_type`/`scope_id` opcionais em `SAVE`, nova
operação `"LIST_SCOPE"`.

## Relação com fontes e confiança

Conhecimento provisório/confirmado se apoia em evidências e fontes (ver
`TRUST_GUARDRAILS.md`) e carrega os mesmos níveis de confiança (LOW/MEDIUM/HIGH) e a
marca de volatilidade quando aplicável.

**Implementação (TASK-056):** `confidence`/`volatility` opcionais
(`None` por padrão — um fato `RAW` recém-capturado pode não ter nenhum
avaliado ainda) em `Knowledge`, reaproveitando `Confidence`
(`app.llm.protocol`, TASK-016) e `Volatility` (`app.confidence.volatility`,
TASK-032) — vocabulário já existente, não duplicado.
`set_knowledge_confidence`/`set_knowledge_volatility` definem cada um.
`Evidence`/`add_evidence`/`list_evidence` guardam evidências como texto
livre associado a uma versão — o cadastro real de fontes (reputação, tipo
`PRIMARY`/`SECONDARY`/`UNKNOWN`) é TASK-059 em diante; vincular evidências
a uma fonte cadastrada de verdade fica para quando esse sistema existir.
Exposto na Knowledge Tool: `"SET_CONFIDENCE"`, `"SET_VOLATILITY"`,
`"ADD_EVIDENCE"`, `"LIST_EVIDENCE"`.

## TASKs relacionadas

TASK-052 a TASK-058 (ver `docs/BACKLOG.md`): modelo RAW/PROVISIONAL/CONFIRMED,
Knowledge Tool, versionamento, escopo GLOBAL/APPLICATION, evidências/fontes, regra de
promoção para CONFIRMED, avaliação de utilidade pelo orquestrador.
