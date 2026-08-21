# TASK-086 — Criar suíte mínima de testes críticos

Status: **Concluída em 2026-08-21**

## Objetivo

Criar suíte mínima de testes críticos, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Marco utilizável inicial") e `docs/TESTING.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Marco utilizável inicial" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/TESTING.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-085 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/TESTING.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Cenário real fixo cobrindo o fluxo ponta a ponta envolvido; ver detalhamento específico abaixo.

## Documentação afetada

`docs/TESTING.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-21. Novo `tests/scenarios/test_minimum_usable_scenario.py`
— primeiros cenários fixos/repetíveis de `tests/scenarios/` (vazio desde
a organização inicial): (1) uma aplicação cadastrada executa via `POST
/v1/executions` e o resultado aparece em `usage_records`,
`execution_traces` **e** no painel (`GET /panel`), tudo verificado na
mesma história — prova que a fiação entre API, orquestrador, rastreio
de consumo, Execution Trace e painel continua íntegra em conjunto, não
só peça por peça (diferente dos testes unitários/integração já
existentes, que testam cada peça isolada); (2) uma aplicação sem API
key válida é rejeitada (`401`) sem deixar rastro nenhum (nem consumo,
nem trace) — prova que a autenticação é a primeira barreira real.

Testes explícitos contra alucinação e uso incorreto de ferramentas
(`docs/TESTING.md`) ficaram deliberadamente fora — exigem um modelo
Ollama real baixado (`docs/OPEN_QUESTIONS.md`, item 3) e o Tool
Registry (TASK-088+), nenhum dos dois existe ainda; são TASK-142/
TASK-144, dedicadas, mais adiante no backlog.

**Mudança estrutural pequena, necessária:** `tests/integration/conftest.py`
(`postgres_dsn`/`ollama_provider`, TASK-006) foi movido para
`tests/conftest.py` — um `conftest.py` só alcança o próprio diretório e
subdiretórios no pytest; os novos cenários em `tests/scenarios/`
(diretório irmão de `tests/integration/`, não descendente) precisavam
das mesmas fixtures. Nenhuma mudança de comportamento, só de local —
confirmado rodando a suíte de integração inteira antes e depois da
mudança. Todas as referências a `tests/integration/conftest.py` em
docstrings de teste (32 arquivos) e em `docs/HANDOFF.md`/`tests/README.md`
foram corrigidas para o caminho novo; a referência histórica em
`docs/tasks/TASK-009.md` (Encerramento de uma TASK já fechada) foi
deixada como estava, por registrar o estado correto **daquele
momento**.

2 testes novos em `tests/scenarios/test_minimum_usable_scenario.py`.
Suíte completa: 734/734 testes aprovados, zero pulados (Ollama
verificado rodando antes da execução).
