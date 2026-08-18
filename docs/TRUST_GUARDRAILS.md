# Confiança, volatilidade, fontes e guardrails

Fonte: seções 13, 14 e 15 da especificação mestre.

## Confiança do modelo

`LOW / MEDIUM / HIGH`.

**Implementação (TASK-031):** o enum `Confidence` já existe em
`app.llm.protocol` (TASK-016) — vocabulário compartilhado do protocolo JSON,
reaproveitado aqui, não duplicado. `backend/app/confidence/model_confidence.py`
acrescenta o que faltava: `CONFIDENCE_ORDER` (ordem explícita `LOW < MEDIUM <
HIGH`, já que o `StrEnum` sozinho não é ordenável), `is_at_least(confidence,
minimum)`, e `get_model_confidence(execution)` — lê a confiança que o modelo
declarou na etapa `RESPOND` da execução (`NoRespondStepError` se ainda não
houver uma). O **cálculo da confiança final** (combinando confiança do
modelo, evidências, reputação de fontes e contradições) é a Confidence
Engine, TASK-033 — não implementado aqui.

## Volatilidade

`VOLATILE / NON_VOLATILE`. Informação `VOLATILE` deve ser **revalidada sempre que for
usada**, mesmo se o modelo estiver em `HIGH`.

**Implementação (TASK-032):** `backend/app/confidence/volatility.py` —
`Volatility` (enum) e `requires_revalidation(volatility)`, que retorna
`True` só para `VOLATILE`, independente de qualquer confiança. Onde a
volatilidade de um fato é registrada e consultada de verdade é o Knowledge
Tool (TASK-052 em diante); aplicar isso como guardrail antes de responder é
TASK-035 — nenhum dos dois implementado nesta TASK, só o enum e a regra.

## Confiança final

Também usa `LOW / MEDIUM / HIGH`. O orquestrador calcula a confiança final usando
confiança do modelo, evidências, reputação das fontes, contradições e volatilidade.

- Pode **rebaixar** `HIGH` quando a evidência for fraca.
- Pode **elevar** `MEDIUM` quando houver evidência externa `HIGH` e consistente.
- `HIGH`: responde normalmente.
- `MEDIUM`: pode responder, mas sinaliza incerteza.
- `LOW`: **não** apresenta conclusão como fato; entrega somente o que conseguiu
  verificar.

**Implementação (TASK-033):** `backend/app/confidence/confidence_engine.py`
— `EvidenceStrength` (`NONE`/`WEAK`/`STRONG`, resumo abstrato da qualidade da
evidência), `calculate_final_confidence(model_confidence, evidence)`
(`HIGH` + `WEAK`/`NONE` rebaixa para `MEDIUM`; `MEDIUM` + `STRONG` eleva para
`HIGH`; `LOW` nunca é elevado; demais combinações mantêm a confiança do
modelo) e `calculate_final_confidence_for_execution(execution, evidence)`,
atalho que lê a confiança declarada via `get_model_confidence` (TASK-031).
Reputação de fontes real (TASK-059 em diante) e evidências reais de pesquisa
(Web Search Tool, TASK-088 em diante) ainda não existem — por isso o motor
recebe `EvidenceStrength` já pronto de quem chama, em vez de calculá-lo.
Contradições, citadas na especificação, dependem de conhecimento
confirmado/provisório (TASK-052 em diante) e não têm representação aqui.
Aplicar a confiança final como guardrail antes de responder é TASK-034.

## Fontes e reputação

Tipos de fonte: `PRIMARY / SECONDARY / UNKNOWN`. Confiabilidade: `LOW / MEDIUM / HIGH`.

- Fonte primária/oficial forte pode bastar sozinha (datasheet, fabricante,
  documentação oficial).
- Fontes secundárias podem exigir múltiplas fontes independentes e concordantes.
- O sistema mantém base de reputação de fontes, avaliada dinamicamente e registrada
  para reutilização futura.
- Se uma fonte confiável começar a apresentar dados errados ou contraditórios, pode
  ser rebaixada para `MEDIUM` ou `LOW`.
- Fonte `LOW` só é usada em último caso e com aviso. Fonte `MEDIUM` sempre gera aviso.
- Quando houver pesquisa, o usuário vê as fontes e uma avaliação geral da evidência em
  `LOW/MEDIUM/HIGH`.

## Fontes bloqueadas (blacklist)

- Existe blacklist de fontes.
- O agente pode bloquear uma fonte automaticamente após validação.
- O `ADMIN` pode bloquear e desbloquear manualmente.
- **Se o agente bloquear, ele não pode desbloquear sozinho** — somente o `ADMIN`.
- Todo bloqueio guarda origem, motivo, data e responsável.
- Bloqueio automático gera alerta no painel.

## Guardrails de resposta

- Resposta conclusiva é bloqueada quando a confiança final é `LOW` (TASK-034).
- Informação volátil sempre exige revalidação antes de uso, independentemente da
  confiança anterior (TASK-035).
- Ambiguidade real gera pergunta ao usuário/aplicação em vez de suposição (TASK-036,
  ver também `ORCHESTRATOR.md`).

**Implementação (TASK-036):** `backend/app/confidence/ambiguity_guardrail.py`
— `ensure_ambiguity_resolved_before_response(is_ambiguous,
clarification_requested)`, novo código de erro `4008`
(`UNRESOLVED_AMBIGUITY`). Bloqueia com `ClaudiaoError` quando há ambiguidade
real e nenhuma pergunta de esclarecimento foi feita; uma resposta que é a
própria pergunta (`clarification_requested=True`) passa livre mesmo com
ambiguidade. O protocolo (TASK-016) não tem uma `action` própria de
"pergunta" — perguntar é um `RESPOND` cujo `reason` pergunta em vez de
concluir. Avaliar de fato se há ambiguidade (`ContextManager`, TASK-037+) e
acionar esta guarda no fluxo real do orquestrador não são desta TASK.

**Implementação (TASK-035):**
`backend/app/confidence/revalidation_guardrail.py` —
`ensure_volatile_information_revalidated(volatility, was_revalidated)`, novo
código de erro `4007` (`VOLATILE_INFORMATION_NOT_REVALIDATED`). Usa
`requires_revalidation` (TASK-032) para decidir se a revalidação é exigida;
bloqueia com `ClaudiaoError` quando for `VOLATILE` e `was_revalidated` for
`False`. `NON_VOLATILE` e `VOLATILE` já revalidada passam livres. Executar a
revalidação de fato (reconsultar Knowledge Tool, TASK-052+) e acionar esta
guarda no fluxo real do orquestrador não são desta TASK.

**Implementação (TASK-034):** `backend/app/confidence/response_guardrail.py`
— `ensure_conclusive_response_allowed(final_confidence)`, novo código de erro
`4006` (`LOW_CONFIDENCE_BLOCKED`). Recebe a confiança final já calculada
(Confidence Engine, TASK-033) e levanta `ClaudiaoError` quando for `LOW`;
`MEDIUM` e `HIGH` passam livres. Sinalizar incerteza em `MEDIUM` e o ponto do
fluxo do orquestrador onde essa guarda é efetivamente acionada antes de uma
resposta real (depende de onde a resposta final é montada) não são desta
TASK — só a guarda isolada.

## TASKs relacionadas

- Confiança/guardrails: TASK-031 a TASK-036.
- Fontes: TASK-059 a TASK-066.
