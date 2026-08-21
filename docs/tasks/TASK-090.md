# TASK-090 — Implementar abertura de página

Status: Concluída

## Objetivo

Implementar abertura de página, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Web") e `docs/TOOLS.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Web" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/TOOLS.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-089 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/TOOLS.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do WebSearchProvider/normalização/política de PDF, com casos de fonte HIGH/MEDIUM/LOW/UNKNOWN, conforme docs/TESTING.md.

## Documentação afetada

`docs/TOOLS.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-21. Criado `backend/app/web_search/page_fetcher.py`:
`open_page(url, timeout=10.0) -> PageContent`
(`url`/`final_url`/`status_code`/`content_type`/`body` bruto),
`PageFetchError`. Nenhuma decisão nova de arquitetura — diferente de
`WebSearchProvider` (TASK-088), abrir uma página não tem fornecedor
concorrente para abstrair (não é "Google vs. Firecrawl"), então é uma
função simples via `urllib.request` (biblioteca padrão), sem ABC/classe.
Não segue links encontrados no conteúdo da página — só faz uma
requisição HTTP para a `url` recebida, exatamente como `docs/TOOLS.md`
descreve ("Lê somente aquela página — não segue links automaticamente").
Redirecionamentos HTTP padrão (3xx) são resolvidos pelo próprio
`urllib` — não é "seguir link do conteúdo", é a mesma página mudando de
endereço; `final_url` no retorno registra isso.

Nenhuma normalização de conteúdo por tipo (HTML/text/JSON/XML,
TASK-091), nenhuma extração de referências/links do corpo da página
(TASK-092), nenhuma política de PDF seguro (TASK-093) e nenhuma
integração com reputação de fontes (TASK-094) implementadas aqui — só a
abertura/leitura bruta.

10 testes novos: 8 unitários em `tests/unit/test_page_fetcher.py`
(`urlopen` mockado — sucesso, `final_url` após redirect, `url` vazia/em
branco rejeitada, erro HTTP/URL/OS vira `PageFetchError`, header
`User-Agent` enviado) e 2 de integração em
`tests/integration/test_page_fetcher_integration.py`, contra a instância
SearXNG local (TASK-089, já rodando) em vez da internet pública — evita
depender de um site de terceiro instável/fora do nosso controle nos
testes automatizados; pula se indisponível. Suíte completa: 764/764
testes aprovados (1 pulado, portabilidade esperada sem
`CLAUDIAO_ACTIVE_MODEL`).

**Checkpoint de 10 TASKs:** esta TASK fecha o checkpoint (último foi na
TASK-080) — `main` local enviada para `origin/main` e `docs/HANDOFF.md`
atualizado na mesma resposta que encerra esta TASK, antes de aguardar a
próxima mensagem do usuário.
