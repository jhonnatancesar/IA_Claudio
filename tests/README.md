# Testes

Ver `docs/TESTING.md` para as categorias obrigatórias na V1. Framework: `pytest`
(`backend/pyproject.toml`, `[tool.pytest.ini_options]`) — Python escolhido na
TASK-005 (`DEC-005`, `docs/DECISION_LOG.md`).

- `conftest.py` (TASK-006, movido para cá na TASK-086) — fixtures
  compartilhadas: `postgres_dsn` (PostgreSQL local real, pula o teste se
  indisponível) e `ollama_provider` (Ollama local real, idem). Vale para
  `integration/` e `scenarios/`.
- `unit/` — testes unitários por componente (orquestrador, memória, conhecimento,
  API, ferramentas, confiança, guardrails). Sem tocar rede/banco.
- `integration/` — testes de integração entre componentes, contra PostgreSQL/
  Ollama locais de verdade.
- `scenarios/` — cenários reais fixos/repetíveis (critério oficial de regressão,
  `test_minimum_usable_scenario.py`, TASK-086) e cenários variáveis (robustez,
  ainda não escritos), incluindo testes explícitos contra alucinação e uso
  incorreto de ferramentas (TASK-142/TASK-144, ainda não alcançáveis — exigem
  modelo Ollama real baixado e Tool Registry, respectivamente).

Rodar a suíte completa: `python -m pytest tests/ -v --basetemp=".pytest_tmp" -rs`
(a partir de `backend/`) — o Ollama local precisa estar rodando para não pular
os testes que dependem dele.
