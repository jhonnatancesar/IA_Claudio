# Testes

Ver `docs/TESTING.md` para as categorias obrigatórias na V1.

- `unit/` — testes unitários por componente (orquestrador, memória, conhecimento,
  API, ferramentas, confiança, guardrails).
- `integration/` — testes de integração entre componentes.
- `scenarios/` — cenários reais fixos/repetíveis (critério oficial de regressão) e
  cenários variáveis (robustez), incluindo testes explícitos contra alucinação e uso
  incorreto de ferramentas.

Nenhum teste foi escrito ainda. Framework de teste depende da stack de implementação,
ainda não escolhida (ver `docs/OPEN_QUESTIONS.md`).
