# Web Search — abstração de busca web

Documentação: docs/TOOLS.md. TASKs: TASK-088 a TASK-094.

Interface `WebSearchProvider`, sem acoplamento a nenhum fornecedor de busca
específico (Google, Firecrawl, Exa, Parallel, ...) — mesmo princípio de
`app.llm.provider.LocalLLMProvider` (TASK-014) para o runtime de modelo
local.

- `provider.py` (TASK-088) — `WebSearchProvider` (classe abstrata),
  `SearchRequest`/`SearchResponse`/`SearchResult` (dataclasses frozen),
  `SearchPurpose` (`GENERAL_RESEARCH`/`ENTITY_VERIFICATION`/
  `CURRENT_INFORMATION`/`PRODUCT_IDENTITY`), `WebSearchProviderError`. Só a
  interface — nenhuma implementação concreta (TASK-089), nenhuma abertura
  de página (TASK-090), nenhuma normalização de conteúdo (TASK-091),
  nenhuma extração de referências (TASK-092), nenhuma política de PDF
  (TASK-093) e nenhuma integração com reputação de fontes (TASK-094).
  Cadastro no catálogo fixo de ferramentas e conexão com o
  `ExecutionOrchestrator` continuam em aberto para as próximas TASKs do
  bloco "Web"/"APIs e arquivos" — não implementados aqui.

Testes em `tests/unit/test_web_search_provider.py` (sem rede real — TASK-089
é a primeira implementação concreta).
