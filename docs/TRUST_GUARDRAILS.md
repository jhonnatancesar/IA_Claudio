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

## Confiança final

Também usa `LOW / MEDIUM / HIGH`. O orquestrador calcula a confiança final usando
confiança do modelo, evidências, reputação das fontes, contradições e volatilidade.

- Pode **rebaixar** `HIGH` quando a evidência for fraca.
- Pode **elevar** `MEDIUM` quando houver evidência externa `HIGH` e consistente.
- `HIGH`: responde normalmente.
- `MEDIUM`: pode responder, mas sinaliza incerteza.
- `LOW`: **não** apresenta conclusão como fato; entrega somente o que conseguiu
  verificar.

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

## TASKs relacionadas

- Confiança/guardrails: TASK-031 a TASK-036.
- Fontes: TASK-059 a TASK-066.
