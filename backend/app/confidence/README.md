# Confidence Engine

Documentação: docs/TRUST_GUARDRAILS.md. TASKs: TASK-031 a TASK-033.

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

Testes em `tests/unit/test_model_confidence.py`, `tests/unit/test_volatility.py`.
