# Confidence Engine

Documentação: docs/TRUST_GUARDRAILS.md. TASKs: TASK-031 a TASK-034.

Confiança do modelo (LOW/MEDIUM/HIGH), volatilidade (VOLATILE/NON_VOLATILE) e cálculo da confiança final combinando evidências, reputação de fontes e contradições.

- `model_confidence.py` (TASK-031) — `CONFIDENCE_ORDER`/`is_at_least()`/
  `get_model_confidence(execution)`. Reaproveita `Confidence` de
  `app.llm.protocol` (TASK-016), não duplica. Cálculo da confiança final é
  TASK-033; guardrails que agem sobre a confiança (bloquear `LOW`, revalidar
  volátil, ambiguidade) são TASK-034/TASK-035/TASK-036.
- `volatility.py` (TASK-032) — `Volatility` (`VOLATILE`/`NON_VOLATILE`),
  `requires_revalidation(volatility)`. Só o enum e a regra — onde a
  volatilidade é registrada (Knowledge Tool, TASK-052+) e onde é aplicada
  como guardrail (TASK-035) não são desta TASK.
- `confidence_engine.py` (TASK-033) — `EvidenceStrength`
  (`NONE`/`WEAK`/`STRONG`), `calculate_final_confidence(model_confidence,
  evidence)` e `calculate_final_confidence_for_execution(execution,
  evidence)`. Combina confiança do modelo com um resumo abstrato de
  evidência (reputação de fontes real é TASK-059+, evidências reais de
  pesquisa são TASK-088+). Bloquear resposta em `LOW` é TASK-034.
- `response_guardrail.py` (TASK-034) — `ensure_conclusive_response_allowed
  (final_confidence)`, código de erro `4006`. Bloqueia resposta conclusiva
  quando a confiança final é `LOW`. Onde essa guarda é acionada no fluxo real
  do orquestrador não é desta TASK.

Testes em `tests/unit/test_model_confidence.py`, `tests/unit/test_volatility.py`,
`tests/unit/test_confidence_engine.py`, `tests/unit/test_response_guardrail.py`.
