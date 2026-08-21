# TASK-088 — Criar WebSearchProvider

Status: Concluída

## Objetivo

Criar WebSearchProvider, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Web") e `docs/TOOLS.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Web" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/TOOLS.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-087 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/TOOLS.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do WebSearchProvider/normalização/política de PDF, com casos de fonte HIGH/MEDIUM/LOW/UNKNOWN, conforme docs/TESTING.md.

## Documentação afetada

`docs/TOOLS.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-21. Criado `backend/app/web_search/provider.py`:
`WebSearchProvider` (ABC, `search()`/`is_available()`), `SearchRequest`/
`SearchResponse`/`SearchResult` (dataclasses frozen), `SearchPurpose`
(`GENERAL_RESEARCH`/`ENTITY_VERIFICATION`/`CURRENT_INFORMATION`/
`PRODUCT_IDENTITY`, os quatro valores documentados em `docs/TOOLS.md` —
lista deliberadamente não estendida, a própria especificação deixa em
aberto "e outros futuros"), `WebSearchProviderError` — mesmo padrão
arquitetural de `LocalLLMProvider` (TASK-014): só a interface, nenhuma
implementação concreta.

Decisão de design (dentro do escopo normal de implementação, não uma
decisão de arquitetura nova): `docs/TOOLS.md` descreve a chamada como
`search(query, max_results, purpose)` — três parâmetros soltos; agrupados
aqui em `SearchRequest` (com `metadata` como escape hatch), espelhando
`CompletionRequest`/`CompletionResponse` de `app.llm.provider` — mesma
lógica de manter espaço de extensão futura sem quebrar a assinatura do
método.

Nenhum provider concreto (TASK-089), abertura/leitura de página
(TASK-090), normalização de conteúdo (TASK-091), extração de referências
(TASK-092), política de PDF (TASK-093) ou integração com reputação de
fontes (TASK-094) implementados aqui — só a interface. Cadastro no
catálogo fixo de ferramentas e conexão com o `ExecutionOrchestrator`
continuam em aberto para as próximas TASKs.

8 testes unitários novos em `tests/unit/test_web_search_provider.py`
(instanciação direta da ABC falha, subclasse incompleta falha,
imutabilidade do request, default de `metadata`, os quatro valores de
`SearchPurpose`, provider fake completo e indisponível). Suíte completa:
742/742 testes aprovados (1 pulado, portabilidade esperada sem
`CLAUDIAO_ACTIVE_MODEL`).
