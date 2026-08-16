# Conhecimento

Fonte: seção 12 da especificação mestre.

Conhecimento é **separado da memória** (ver `MEMORY.md`) e **nunca é apagado
automaticamente**.

## Ciclo de maturidade

```
RAW → PROVISIONAL → CONFIRMED
```

Fluxo desejado: **NÃO SEI → PESQUISO → VALIDO → CONFIRMO → AVALIO UTILIDADE → SALVO.**

## Versionamento

Se um fato confirmado mudar, o sistema:

- mantém a versão anterior;
- registra a nova versão;
- marca qual é a atual;
- preserva fontes, contexto e motivo da mudança.

Isto é o mesmo princípio de não reescrita silenciosa aplicado a conhecimento: uma
mudança de fato é uma **nova versão**, não uma edição da anterior.

## Escopos

`GLOBAL` e `APPLICATION:<id>`. Conhecimento específico de uma aplicação **não pode ser
promovido automaticamente para global** — promoção exige avaliação explícita (ver
regra de promoção, TASK-057).

## Relação com fontes e confiança

Conhecimento provisório/confirmado se apoia em evidências e fontes (ver
`TRUST_GUARDRAILS.md`) e carrega os mesmos níveis de confiança (LOW/MEDIUM/HIGH) e a
marca de volatilidade quando aplicável.

## TASKs relacionadas

TASK-052 a TASK-058 (ver `docs/BACKLOG.md`): modelo RAW/PROVISIONAL/CONFIRMED,
Knowledge Tool, versionamento, escopo GLOBAL/APPLICATION, evidências/fontes, regra de
promoção para CONFIRMED, avaliação de utilidade pelo orquestrador.
