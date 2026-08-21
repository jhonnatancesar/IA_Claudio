# TASK-089 — Implementar primeiro provider de busca

Status: Concluída

## Objetivo

Implementar primeiro provider de busca, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Web") e `docs/TOOLS.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Web" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/TOOLS.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-088 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/TOOLS.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do WebSearchProvider/normalização/política de PDF, com casos de fonte HIGH/MEDIUM/LOW/UNKNOWN, conforme docs/TESTING.md.

## Documentação afetada

`docs/TOOLS.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-21. Fornecedor escolhido em três rodadas de
`AskUserQuestion` (`DEC-012`, `docs/DECISION_LOG.md`) — DuckDuckGo pedido
primeiro, mas descartado depois de testar de verdade (scraping HTML
bloqueado por anti-bot real; API oficial de Instant Answer vazia para
buscas genéricas); SearXNG local escolhido na sequência, rodando via
Docker (Docker Desktop já instalado nesta máquina, só precisou ser
iniciado).

Criado `backend/app/web_search/providers/searxng_provider.py`:
`SearXNGSearchProvider` — `search()` chama `GET /search?q=...&format=json`
da instância local (`http://localhost:8888`, container
`claudiao-searxng`), mapeia `results[].{url,title,content}` para
`SearchResult(url, title, snippet)`, recorta em `max_results`;
`is_available()` checa `GET /healthz`. HTTP via `urllib.request`
(biblioteca padrão, sem dependência nova), com `self._fetch` injetável
para teste — mesmo padrão de `provider._client` em `OllamaProvider`
(TASK-015).

Infra local: `config/searxng/settings.yml` (gerado pelo container, não
versionado) com `search.formats: [html, json]` habilitado explicitamente
(desligado por padrão na imagem oficial). Nova fixture `searxng_provider`
em `tests/conftest.py`, mesmo padrão de `ollama_provider` — pula o teste
se a instância local não estiver acessível.

12 testes novos: 9 unitários em `tests/unit/test_searxng_provider.py`
(mapeamento de resultados, query/format na URL, corte por `max_results`,
`content` ausente vira snippet vazio, erro de rede/JSON inválido vira
`WebSearchProviderError`, `is_available` true/false, é um
`WebSearchProvider`) e 3 de integração em
`tests/integration/test_searxng_provider_integration.py`, contra a
instância local de verdade (disponibilidade, busca real com resultados
não vazios, respeito a `max_results`) — validados com buscas genéricas
reais em inglês e nas mesmas queries em português que tinham falhado no
DuckDuckGo. Suíte completa: 754/754 testes aprovados (1 pulado,
portabilidade esperada sem `CLAUDIAO_ACTIVE_MODEL`).

Cadastro no catálogo fixo de ferramentas e conexão com o
`ExecutionOrchestrator` continuam em aberto (TASK-095+). Abertura/leitura
de página (TASK-090), normalização de conteúdo (TASK-091), extração de
referências (TASK-092), política de PDF (TASK-093) e integração com
reputação de fontes (TASK-094) não implementados aqui.
