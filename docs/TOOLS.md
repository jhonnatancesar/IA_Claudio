# Ferramentas

Fonte: seções 16 a 19, 21 e 22 da especificação mestre.

## Ferramentas da V1

- Memory Tool
- Knowledge Tool
- Web Search Tool
- File Tool
- Database Tool
- API Tool

System/Automation Tool fica para a V2 (ver `OUT_OF_SCOPE.md`).

Na V1, todas as ferramentas são **globais** e cadastradas no agente. O catálogo é
**fixo** e carregado na inicialização. A execução é **sequencial** para reduzir
complexidade e consumo (paralelismo fica para depois — ver `OUT_OF_SCOPE.md`).
Providers têm ordem de preferência global inicialmente, com fallback por capacidade.

## Web Search Tool

A pesquisa usa uma abstração genérica `WebSearchProvider`, sem acoplamento direto a
Google, Firecrawl, Exa, Parallel ou outro fornecedor.

```
search(query, max_results, purpose)
```

**Implementação (TASK-088):** `backend/app/web_search/provider.py` —
`WebSearchProvider` (classe abstrata, `search()`/`is_available()`),
`SearchRequest`/`SearchResponse`/`SearchResult` (dataclasses frozen),
`SearchPurpose`, `WebSearchProviderError` — mesmo padrão de
`LocalLLMProvider` (TASK-014). Só a interface; nenhum provider concreto
ainda (TASK-089).

Purposes possíveis: `GENERAL_RESEARCH`, `ENTITY_VERIFICATION`,
`CURRENT_INFORMATION`, `PRODUCT_IDENTITY` e outros futuros.

- A pesquisa encontra resultados; o agente pode abrir e ler a página selecionada.
- Lê **somente aquela página** — não segue links automaticamente.
- Retorna também os links/referências encontrados no texto da página.
- Só abre outro link se usuário ou aplicação pedir.
- **Sem cache** de pesquisas/páginas na V1.

## Conteúdo web e PDFs

- Pode ler HTML, texto, JSON, XML e demais formatos úteis.
- PDF externo só é aberto automaticamente se vier de página oficial/segura ou domínio
  classificado `HIGH`.
- PDF de origem `UNKNOWN`, `MEDIUM` ou `LOW` **não** é aberto na V1.

## Política de pesquisa

### Chat

- Se o agente precisar pesquisar, explica o que está incerto, diz o que pretende
  pesquisar e por quê, e **espera autorização**.
- A autorização vale apenas para aquela pesquisa específica.
- Se a confiança for `LOW` e o usuário não autorizar, **não inventa**.

### Aplicações

- A própria aplicação define se pesquisa é permitida, o tipo de pesquisa, limites,
  timeout, contexto e regras.
- Se a pesquisa estiver autorizada, o agente usa automaticamente quando necessário.
- Se não estiver autorizada e a confiança for baixa, retorna que não possui confiança
  suficiente para afirmar sem validação externa.

## APIs externas e outros agentes

- O Claudião pode chamar APIs externas diretamente quando autorizado/configurado.
- Pode consultar outros agentes/serviços inteligentes.
- Outro agente **nunca** é tratado como fonte de verdade automática; deve retornar
  resposta e fontes em JSON, e o Claudião valida as fontes por conta própria antes de
  aceitar a informação.

## File Tool e Database Tool

O agente acessa somente arquivos próprios e o banco ligado ao próprio agente. As
aplicações enviam os dados necessários na requisição; o Claudião **não** entra
diretamente nos bancos das aplicações na V1.

## TASKs relacionadas

- Web: TASK-088 a TASK-094.
- APIs e arquivos: TASK-095 a TASK-100.
- Ver também `SECURITY.md` (HTTPS obrigatório para destinos externos) e
  `TRUST_GUARDRAILS.md` (reputação de fontes usada pela pesquisa).
