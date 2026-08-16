# Contexto permanente do projeto

## Missão

Construir, TASK por TASK, um agente inteligente local (Claudião) cujo raciocínio
principal roda em um modelo local via `LocalLLMProvider`, orquestrado de forma
determinística, sem depender de IA externa para pensar normalmente.

## Separação de projetos

Este repositório é **novo e independente** do AIShoppingAgent. Não reutilizar código,
regras de negócio, TASKs ou documentação de domínio daquele projeto. O AIShoppingAgent
só é usado como referência de organização estrutural (ver `docs/DECISION_LOG.md` para
o registro dessa decisão).

## Arquitetura alvo da V1

- Máquina única, PostgreSQL local, execução direta no sistema operacional (sem Docker
  como requisito).
- Runtime de modelo inicial: Ollama, atrás da abstração `LocalLLMProvider`.
- Orquestrador determinístico controlando policy, contexto, planejamento, confiança,
  guardrails, fila, ferramentas e trace de execução.
- Ferramentas da V1: Memory, Knowledge, Web Search, File, Database, API.

Detalhes completos em `docs/ARCHITECTURE.md` e demais documentos de `docs/`.

## Guardrails

- Não implementar nada além da TASK solicitada.
- Não escolher a stack de implementação nem o modelo LLM definitivo sem decisão
  explícita do usuário (ver `docs/OPEN_QUESTIONS.md`).
- Não transformar IA externa em fallback de raciocínio.
- Preservar RAW/PROVISIONAL/CONFIRMED, LOW/MEDIUM/HIGH, VOLATILE/NON_VOLATILE e o
  marco de uso na TASK-087.
- Toda comunicação e documentação do projeto em PT-BR (ver `AGENTS.md`).

## Fonte de verdade

`docs/` registra arquitetura, escopo e decisões; `docs/ROADMAP.md` registra a ordem de
trabalho; `docs/tasks/` contém o escopo unitário de cada TASK.
