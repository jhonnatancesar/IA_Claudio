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
├── unit/          testes unitários por componente
├── integration/   testes de integração entre componentes
└── scenarios/      cenários fixos (regressão) e variáveis (robustez)
```

Nenhum teste foi escrito ainda — esta é só a estrutura de diretório, criada nesta
organização inicial.
