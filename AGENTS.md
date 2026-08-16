# Instruções para agentes

Este arquivo orienta qualquer agente (humano ou IA) que for implementar TASKs do
Claudião. Ele não substitui a especificação mestre nem os documentos em `docs/` —
resume como trabalhar dentro deste repositório.

## Leitura obrigatória antes de qualquer TASK

1. `README.md` — visão geral e mapa da documentação.
2. `docs/ARCHITECTURE.md` — arquitetura de alto nível e princípios não negociáveis.
3. `docs/tasks/README.md` — índice e estado atual das TASKs.
4. O arquivo `docs/tasks/TASK-XXX.md` da TASK específica a ser executada.
5. O(s) documento(s) listado(s) em "Documentação afetada" dentro da própria TASK.

## Regras de execução

- Este projeto é **separado** do AIShoppingAgent. Não importar código, dependências,
  regras de negócio, integrações (Telegram, Firecrawl, lojas) ou TASKs daquele
  repositório. O AIShoppingAgent só serve como referência de organização.
- Implementar **somente** o objetivo da TASK corrente. Não adiantar TASKs futuras,
  mesmo que pareça conveniente.
- Não reescrever decisões já aprovadas na especificação mestre ou em
  `docs/DECISION_LOG.md`. Se uma TASK expuser um conflito, uma decisão impossível ou
  uma lacuna, registrar em `docs/OPEN_QUESTIONS.md` e aguardar decisão do usuário —
  nunca decidir sozinho.
- Preservar as invariantes da especificação, mesmo entre TASKs distantes:
  - RAW → PROVISIONAL → CONFIRMED (conhecimento).
  - LOW / MEDIUM / HIGH (confiança) e VOLATILE / NON_VOLATILE (volatilidade).
  - Separação entre contexto imediato, memória persistente e conhecimento.
  - Orquestrador determinístico controlando o modelo — nunca o inverso.
  - `LocalLLMProvider` como abstração; Ollama é apenas o runtime inicial.
  - Internet/APIs/outros agentes são ferramentas, nunca fallback de raciocínio.
  - Política de pesquisa diferente para chat (pede autorização) e para aplicações
    (definida pela própria aplicação).
  - Marco de uso na TASK-087.
- A stack de implementação (linguagem, framework web, ORM etc.) ainda **não** foi
  decidida (ver `docs/OPEN_QUESTIONS.md`). Não escolher silenciosamente durante uma
  TASK de infraestrutura — se uma TASK exigir essa decisão, registrar a proposta em
  `docs/DECISION_LOG.md` e pedir aprovação antes de prosseguir.
- Todo o trabalho neste projeto — mensagens de progresso, documentação, TASKs,
  decision log — é conduzido em português do Brasil (PT-BR). Elementos técnicos que
  precisam permanecer literais (código, nomes de arquivo/função, comandos, variáveis
  de ambiente, stack traces, SQL, payloads JSON) continuam em sua forma original.

## Workflow oficial de execução de TASKs

```
TASK → Implementação → Validação/Testes → Atualização documental → Commit → Push
```

1. **Preparação** — ler a TASK e os documentos afetados; confirmar dependências
   satisfeitas; levantar qualquer credencial/configuração ausente e pedir ao usuário
   antes de começar (nunca inventar valores).
2. **Implementação** — cobrir exatamente o objetivo e o escopo declarados.
3. **Testes** — cobrir os testes esperados listados na TASK; seguir
   `docs/TESTING.md`.
4. **Atualização documental** — atualizar os documentos afetados e
   `docs/tasks/README.md`; se a TASK gerou uma decisão nova, registrar em
   `docs/DECISION_LOG.md`.
5. **Encerramento** — só marcar a TASK como concluída quando os critérios de aceite
   descritos nela forem realmente satisfeitos.

Commits e push seguem as regras normais de Git do agente/ferramenta em uso — nunca
sem confirmação explícita do usuário para ações que afetam o repositório remoto.

## Estado atual

Repositório em organização inicial. Nenhuma TASK funcional foi executada.
`docs/tasks/README.md` é a fonte viva do estado de cada TASK.
