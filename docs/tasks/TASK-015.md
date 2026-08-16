# TASK-015 — Implementar OllamaProvider

Status: **Concluída em 2026-08-16**

## Objetivo

Implementar OllamaProvider, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "LLM") e `docs/ARCHITECTURE.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "LLM" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/ARCHITECTURE.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-014 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/ARCHITECTURE.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do provider e do protocolo JSON (parser/validator contra JSON malformado ou fora do contrato), conforme docs/TESTING.md.

## Documentação afetada

`docs/ARCHITECTURE.md`, `docs/OPEN_QUESTIONS.md` (item 3),
`docs/DECISION_LOG.md` (DEC-008), `docs/tasks/README.md`,
`backend/app/llm/README.md`

## Encerramento

Concluída em 2026-08-16. Com confirmação explícita do usuário, o runtime
**Ollama** foi instalado de verdade nesta máquina (`winget install
Ollama.Ollama`, serviço em `http://localhost:11434`) — nenhum modelo baixado
(`docs/OPEN_QUESTIONS.md`, item 3, continua aberto). Criado
`backend/app/llm/providers/ollama_provider.py`: `OllamaProvider`, usando o SDK
oficial `ollama` (DEC-008). `complete()` chama `Client.generate()`, mapeia
`temperature`/`max_tokens`, converte `ollama.ResponseError`/`ConnectionError`
em `LocalLLMProviderError`; `is_available()` via `Client.list()`.

9 testes unitários com mock do client (sem depender do Ollama real) + 2 de
integração real (servidor disponível; modelo inexistente levanta o erro
esperado — confirmado rodando de verdade, não pulado). Suíte completa:
101/101 testes aprovados.
