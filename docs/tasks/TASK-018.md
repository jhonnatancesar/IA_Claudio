# TASK-018 — Criar prompt-base do Claudião

Status: **Concluída em 2026-08-16**

## Objetivo

Criar prompt-base do Claudião, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "LLM") e `docs/ARCHITECTURE.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "LLM" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/ARCHITECTURE.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-017 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/ARCHITECTURE.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do provider e do protocolo JSON (parser/validator contra JSON malformado ou fora do contrato), conforme docs/TESTING.md.

## Documentação afetada

`docs/ARCHITECTURE.md`, `docs/tasks/README.md`, `backend/app/llm/README.md`

## Encerramento

Concluída em 2026-08-16. Criado `backend/app/llm/prompt.py`: `BASE_PROMPT`
(texto fixo), `get_base_prompt()`, `PROMPT_VERSION`. Cobre identidade do
Claudião, independência de IA externa, princípios (offline-first,
inteligência local, orquestração controlada), hierarquia de prioridade na
ordem correta, regras de confiança (LOW/MEDIUM/HIGH) e o contrato do
protocolo JSON por etapa (TASK-016), incluindo a exigência de responder
sempre em português do Brasil. 10 testes unitários novos verificando a
presença e a ordem desses elementos no texto (não testa qualidade de
linguagem natural — isso não é determinístico). Suíte completa: 136/136
testes aprovados. Composição dinâmica com contexto/memória/conhecimento por
requisição é escopo da TASK-019, não implementada aqui.
