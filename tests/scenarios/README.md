# tests/scenarios/

Cenários fixos (regressão) e variáveis (robustez), incluindo alucinação e uso
incorreto de ferramentas. Ver `docs/TESTING.md` e `../README.md`.

- `test_minimum_usable_scenario.py` (TASK-086) — cenários fixos
  cobrindo o mínimo utilizável (`docs/V1_SCOPE.md`) de ponta a ponta:
  execução completa de uma aplicação cadastrada aparecendo em
  consumo/execuções/painel juntos, e rejeição sem rastro de uma
  aplicação não autenticada. Testes de alucinação e uso incorreto de
  ferramentas continuam pendentes — TASK-142/TASK-144, exigem modelo
  Ollama real baixado e Tool Registry (TASK-088+), Tool Registry ainda
  não existe.
  - `test_scenario_real_model_completes_a_real_objective` (TASK-087,
    marco do primeiro Claudião utilizável): único cenário desta suíte
    que usa `OllamaProvider` real contra `CLAUDIAO_ACTIVE_MODEL` de
    verdade (`docs/DECISION_LOG.md`, DEC-011), sem `dependency_overrides`
    — demora minutos em CPU. Pula automaticamente se
    `CLAUDIAO_ACTIVE_MODEL` não estiver configurado no ambiente do
    processo do `pytest` (ex.: `config/.env` não carregado).
