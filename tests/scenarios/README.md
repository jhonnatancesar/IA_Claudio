# tests/scenarios/

Cenários fixos (regressão) e variáveis (robustez), incluindo alucinação e uso
incorreto de ferramentas. Ver `docs/TESTING.md` e `../README.md`.

- `test_minimum_usable_scenario.py` (TASK-086) — cenários fixos
  cobrindo o mínimo utilizável (`docs/V1_SCOPE.md`) de ponta a ponta:
  execução completa de uma aplicação cadastrada aparecendo em
  consumo/execuções/painel juntos, e rejeição sem rastro de uma
  aplicação não autenticada. Testes de alucinação e uso incorreto de
  ferramentas continuam pendentes — TASK-142/TASK-144, exigem modelo
  Ollama real baixado e Tool Registry (TASK-088+), nenhum dos dois
  existe ainda.
