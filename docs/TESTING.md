# Testes

Fonte: seção 45 da especificação mestre.

## Obrigatórios na V1

- Testes unitários do orquestrador, memória, conhecimento, API, ferramentas,
  confiança e guardrails.
- Testes de integração entre componentes.
- Cenários reais fixos/repetíveis como **critério oficial de regressão**.
- Cenários variáveis como complemento de robustez.
- Testes explícitos contra **alucinação** e **uso incorreto de ferramentas**.

## Como isso aparece no backlog

Cada TASK de implementação declara, no campo "Testes esperados" do seu arquivo em
`docs/tasks/`, quais destas categorias se aplicam. O bloco final do backlog
(TASK-138 a TASK-147) consolida a suíte completa:

- TASK-138 — testes unitários completos
- TASK-139 — testes de integração
- TASK-140 — cenários fixos de regressão
- TASK-141 — cenários variáveis
- TASK-142 — testes de alucinação
- TASK-143 — testes de confiança e volatilidade
- TASK-144 — testes de segurança das tools
- TASK-145 — métricas finais de qualidade
- TASK-146 — checklist de itens críticos
- TASK-147 — checklist V1 completa

## Estrutura de diretório

```
tests/
├── conftest.py    fixtures compartilhadas (postgres_dsn/ollama_provider)
├── unit/          testes unitários por componente
├── integration/   testes de integração entre componentes
└── scenarios/      cenários fixos (regressão) e variáveis (robustez)
```

**Implementação (TASK-086):** `tests/scenarios/test_minimum_usable_scenario.py`
— primeiros cenários fixos escritos, cobrindo o **mínimo utilizável**
(`docs/V1_SCOPE.md`, marco TASK-087) de ponta a ponta, não peça por
peça: (1) uma aplicação cadastrada executa via `POST /v1/executions` e o
resultado aparece em `usage_records`, `execution_traces` **e** no
painel (`GET /panel`), tudo na mesma história — prova que a fiação
entre API, orquestrador, rastreio de consumo, Execution Trace e painel
continua íntegra; (2) uma aplicação sem API key válida é rejeitada
**sem deixar rastro nenhum** (nem consumo, nem trace) — prova que a
autenticação é a primeira barreira real. Testes de alucinação (exigem
modelo Ollama real baixado) e de uso incorreto de ferramentas (exigem
Tool Registry, TASK-088+) continuam fora de escopo aqui — são TASK-142/
TASK-144, dedicadas, mais adiante.

`tests/integration/conftest.py` (`postgres_dsn`/`ollama_provider`,
TASK-006) foi movido para `tests/conftest.py` nesta TASK — um
`conftest.py` só alcança o próprio diretório e subdiretórios; os
cenários de `tests/scenarios/` também precisam dessas fixtures, e
`tests/scenarios/` é diretório irmão de `tests/integration/`, não
descendente. Nenhuma mudança de comportamento, só de local.
