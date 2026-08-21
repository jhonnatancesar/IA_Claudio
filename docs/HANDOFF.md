# Handoff — estado vivo do projeto

Documento de **estado vivo**, atualizado a cada checkpoint de 10 TASKs concluídas
(`AGENTS.md`, seção "Regra de checkpoint"). Escrito para que **outra IA/agente,
numa sessão nova, sem o histórico desta conversa**, consiga entender onde o
projeto está e continuar o trabalho lendo só este arquivo + o resto de `docs/`.

Se você é essa IA: leia isto primeiro, depois `README.md` → `AGENTS.md` →
`docs/tasks/README.md` → `docs/tasks/TASK-XXX.md` da próxima TASK. Não pule a
leitura de `AGENTS.md` — ele tem regras de governança (branch por TASK, push da
branch sempre, push da main só no checkpoint/pedido, PT-BR em tudo) que não
estão resumidas aqui.

## Checkpoint atual

**Data:** 2026-08-21 · **TASK:** TASK-090 · **TASKs concluídas:** 90 de 147
(TASK-001 a TASK-090) · **Próxima TASK executável:** TASK-091 —
Implementar normalização HTML/text/JSON/XML.

Este checkpoint rodou no prazo certo (10 TASKs desde o checkpoint anterior,
TASK-080) — nono checkpoint seguido no prazo desde que o item 13 de
"Armadilhas" passou a ser aplicado (TASK-060).

**Marco do primeiro Claudião utilizável atingido nesta janela (TASK-087,
`docs/V1_SCOPE.md`).** A partir da TASK-087, o Claudião é considerado
**utilizável em produção controlada** — validado de ponta a ponta com
serviços reais (PostgreSQL, Ollama com modelo `qwen3:8b` baixado), não só
com fakes/mocks.

## O que já existe (resumo, não repete `docs/tasks/`)

- **Estrutura do repositório** organizada por completo (`docs/`, `backend/app/`
  com módulos, `tests/{unit,integration,scenarios}`, `config/`, `scripts/`,
  `adr/`, `rfc/`) — TASK-001.
- **Bloco "Fundação" completo (TASK-001 a TASK-008):** configuração central,
  PostgreSQL local instalado e banco `claudiao` criado, schema inicial
  (`users`, `applications`, `settings`, `schema_migrations`, `logs`), logging
  local rotativo + estruturado no PostgreSQL, catálogo interno de erros e
  formato JSON padrão de erro.
- **Bloco "Segurança e identidade" completo (TASK-009 a TASK-013):**
  autenticação de usuários (hash PBKDF2), autorização por papel
  (`Role.ADMIN`/`Role.USER`), autenticação de aplicações via API key,
  criptografia de segredos (Fernet) e chave mestra externa ao banco.
- **Bloco "LLM" completo (TASK-014 a TASK-019):** interface `LocalLLMProvider`,
  `OllamaProvider` (SDK oficial, Ollama instalado e rodando localmente, sem
  modelo baixado), protocolo JSON modelo↔orquestrador (`ModelStep`), sua
  validação semântica (`validate_step`, código de erro 4001) e o prompt-base +
  composição dinâmica de prompt/contexto.
- **Bloco "Orquestração" completo (TASK-020 a TASK-030):** `Execution`
  (estados `PENDING`/`RUNNING`/`COMPLETED`/`FAILED`/`CANCELLED`),
  `execution_id` (UUID4), `ExecutionPolicy`, `ExecutionOrchestrator`
  (`run_step`/`run_until_response` — liga provider, prompt, protocolo,
  validação de plano e execução de ferramentas via `tool_executor`),
  planejamento inicial, validação de plano, execução por etapas com
  observações realimentadas ao modelo, replanejamento completo, `max_steps`,
  detecção de loop e cancelamento (`CancellationToken`).
- **Bloco "Confiança e guardrails" completo (TASK-031 a TASK-036):**
  confiança do modelo, volatilidade, Confidence Engine (`EvidenceStrength`,
  `calculate_final_confidence`), bloqueio de resposta conclusiva em `LOW`
  (código 4006), regra obrigatória de revalidação de informação `VOLATILE`
  (código 4007), tratamento de ambiguidade (código 4008). Todos os guardrails
  de bloqueio recebem a avaliação já pronta de quem chama — nenhum é acionado
  ainda no fluxo real do `ExecutionOrchestrator` (isso é TASK-088 em diante).
- **Bloco "Contexto" completo (TASK-037 a TASK-043):** `ContextManager` — uma
  instância por conversa (assunto principal, entidades recentes, referências
  implícitas, correções, detecção de troca de assunto) e
  `ContextWindowMonitor` (uso/aviso em 80% da janela de contexto).
- **Bloco "Memória" completo (TASK-044 a TASK-051):** modelo persistente real
  no PostgreSQL (`memories`), separação por dono, Memory Tool
  (`execute_memory_tool`, `SAVE`/`LIST`/`SEARCH`), busca por conteúdo,
  rastreamento de uso e relevância heurística, retenção por idade+relevância,
  limite fixo de 500 por dono, auditoria mínima de remoção (sem guardar
  conteúdo).
- **Bloco "Conhecimento" completo (TASK-052 a TASK-058):** modelo
  RAW/PROVISIONAL/CONFIRMED (`knowledge`), Knowledge Tool
  (`execute_knowledge_tool`), versionamento (nunca sobrescreve `content`,
  sempre nova linha ligada por linhagem), escopo GLOBAL/APPLICATION,
  confiança/volatilidade opcionais + evidências (texto livre), regra de
  promoção para CONFIRMED (`promote_to_confirmed`, exige confiança `HIGH` +
  evidência) e avaliação de utilidade pelo orquestrador
  (`is_useful_for_orchestrator`, não exposta como tool — é decisão do
  orquestrador, não do modelo).
- **Bloco "Fontes" completo (TASK-059 a TASK-066):** cadastro de fontes
  (`sources`, `register_source` idempotente por `identifier`), tipo
  `PRIMARY`/`SECONDARY`/`UNKNOWN`, reputação `LOW`/`MEDIUM`/`HIGH` com
  atualização em um degrau por vez (`reputation_rule.py`) e histórico de
  auditoria, blacklist com origem `AGENT`/`ADMIN` e motivo obrigatório,
  bloqueio automático quando a reputação cai para `LOW`
  (`auto_block_rule.py`) e desbloqueio restrito a `ADMIN`
  (`unblock_rule.py`, reaproveita `app.auth.roles.require_admin`).
- **Bloco "Aplicações" completo (TASK-067 a TASK-073):** API local via
  FastAPI (`backend/app/api/`, DEC-009) com `uvicorn` como servidor ASGI.
  `POST /v1/executions` autentica por API key (`Authorization: Bearer`),
  valida o payload (`ExecutionRequest`) e executa de fato via
  `ExecutionOrchestrator.run_until_response`, de forma síncrona, com
  `timeout_seconds` aplicado como limite de verdade (roda o orquestrador
  num worker de `ThreadPoolExecutor`, `future.result(timeout=...)` retorna
  assim que o prazo estoura mesmo com o modelo travado, cancela o
  `CancellationToken` compartilhado — `APPLICATION_TIMEOUT_EXCEEDED`,
  código `4009`, HTTP `504`, com `details` trazendo etapa atual/ferramenta
  ativa). Resposta segue o envelope `{"success": bool, ...}` em sucesso e
  erro (`build_success_response`/`build_error_response`). Rastreio de
  consumo (`app.usage.usage_model.record_usage`) grava uma linha em
  `usage_records` a cada desfecho. Nenhum modelo Ollama real foi baixado
  ainda, então os testes da API usam `LocalLLMProvider`/modelo ativo
  fakes via `app.dependency_overrides`.
- **Bloco "Fila" completo (TASK-074 a TASK-077):** `FifoQueue`/`QueueItem`
  em memória (`backend/app/queue/queue_model.py`, mesmo espírito de
  `Execution`) com persistência real em `queue_items`
  (`save_queue_item`/`get_queue_item`/`list_queue_items`), transições de
  estado aplicadas a um item já persistido por `item_id`
  (`start_queue_item`/`complete_queue_item`/`fail_queue_item`) e retenção/
  limpeza (`app.queue.retention_policy`, só itens terminais mais antigos
  que 7 dias). Nenhuma TASK conecta esta fila a `POST /v1/executions`,
  que continua síncrono ponta a ponta.
- **Bloco "Observabilidade inicial" completo (TASK-078 a TASK-083):**
  `ExecutionTrace` (`backend/app/observability/execution_trace.py`)
  conectado de verdade ao `ExecutionOrchestrator` — `trace` opcional em
  `run_step`/`run_until_response` (mesmo padrão de `cancellation_token`),
  registrando etapas e o tempo real de cada chamada ao modelo/ferramenta.
  `POST /v1/executions` cria, popula e agora também **persiste** um
  resumo do trace por requisição — `execution_traces`
  (`save_execution_trace`/`get_execution_trace`/`list_execution_traces`,
  `DEC-010`: decisão pedida ao usuário via `AskUserQuestion` na TASK-082,
  já que a especificação não define isso; só o resumo, não `steps`/
  `errors`/`usage` completos). `backend/app/observability/metrics.py`: 5
  métricas com dado real + 5 lacunas conhecidas documentadas (sem mudança
  desde o checkpoint anterior). `backend/app/panel/routes.py`: `GET
  /panel`, sem autenticação (deliberado — é o painel read-only, regras de
  auth do painel administrativo são TASK-115+), cinco seções: Fila,
  Execuções, Erros, Logs recentes, Consumo. `backend/app/observability/
  health_check.py` (TASK-085): `run_health_check()`, `GET /health`
  (HTTP 200/503, sem auth), rodado no `lifespan` de inicialização.
- **Bloco "Marco utilizável inicial" completo (TASK-084 a TASK-087):**
  `scripts/chat.py` (TASK-084) — CLI HTTP puro (`urllib.request`, sem
  dependência nova) com `create-application`/`chat`, usa a API exatamente
  como qualquer aplicação externa. Primeiros cenários fixos de regressão
  (TASK-086, `tests/scenarios/test_minimum_usable_scenario.py`).
  **TASK-087 é o marco oficial do primeiro Claudião utilizável** — ver
  destaque no topo deste documento. `DEC-011`: modelo `qwen3:8b` baixado
  (`ollama pull`), `CLAUDIAO_ACTIVE_MODEL=qwen3:8b` em `config/.env`
  (provisório, não é a escolha definitiva). Validação real de ponta a
  ponta sem fakes: servidor real → health check saudável → aplicação
  criada via CLI → mensagem real → execução completa (~52s) → conferida
  em `usage_records`/`execution_traces`/painel. Bug real de logging
  encontrado e corrigido nesta TASK (ver "Armadilhas", item 21).
- **Bloco "Web" em andamento (TASK-088 a TASK-090 concluídas, de
  TASK-088 a TASK-094):** `backend/app/web_search/provider.py`
  (TASK-088) — `WebSearchProvider` (ABC), `SearchRequest`/
  `SearchResponse`/`SearchResult`/`SearchPurpose`, mesmo padrão de
  `LocalLLMProvider`. `providers/searxng_provider.py` (TASK-089) —
  `SearXNGSearchProvider`, primeiro provider concreto, contra uma
  instância local do **SearXNG** rodando via **Docker** (`DEC-012`: três
  rodadas de `AskUserQuestion` — DuckDuckGo pedido primeiro mas
  descartado depois de testar de verdade contra proteção anti-bot real e
  API oficial vazia para buscas genéricas; SearXNG local escolhido na
  sequência). `page_fetcher.py` (TASK-090) — `open_page(url)`, função
  simples via `urllib.request` (sem fornecedor a abstrair), não segue
  links do conteúdo da página. Falta: normalização por tipo de conteúdo
  (TASK-091), extração de referências (TASK-092), política de PDF seguro
  (TASK-093), integração com reputação de fontes (TASK-094). Cadastro no
  catálogo fixo de ferramentas e conexão com o `ExecutionOrchestrator`
  continuam em aberto (TASK-095+).
- **Testes:** 764/764 aprovados (unitários + integração real contra
  PostgreSQL, Ollama e SearXNG locais — **Ollama precisa estar rodando**
  para a suíte completa passar sem pular nada; abra o app se os testes de
  integração do Ollama pularem, não trate o skip como aceitável. O mesmo
  vale para o container `claudiao-searxng`, TASK-089 — `docker start
  claudiao-searxng` se não estiver rodando). Rodar com:
  ```
  python -m pytest tests/ -v --basetemp=".pytest_tmp"
  ```
  (o `--basetemp` local é necessário neste ambiente — ver "Armadilhas" abaixo.)
  Com `config/.env` carregado no processo (`set -a && source
  ../config/.env && set +a`, a partir de `backend/`), o cenário de modelo
  real (TASK-087) também roda: 735/735 nesse modo específico (contagem
  menor que 764 porque isso foi medido no checkpoint da TASK-087, antes
  das TASK-088/089/090 — a suíte cresceu desde então; rodar de novo para
  o número atual).

## Mapa de código (backend/app/)

| Módulo | Status | Arquivos |
|---|---|---|
| `errors/` | Implementado (TASK-007/008) | `catalog.py`, `response.py` |
| `observability/` | Completo (TASK-005/006, TASK-078 a TASK-085) | `logging_config.py`, `postgres_log_handler.py`, `execution_trace.py`, `metrics.py`, `health_check.py` |
| `panel/` | Completo (TASK-081 a TASK-083) | `routes.py` |
| `web_search/` | Em andamento (TASK-088 a TASK-090, de TASK-088 a TASK-094) | `provider.py`, `providers/searxng_provider.py`, `page_fetcher.py` |
| `db/` | Implementado (várias TASKs) | `connection.py`, `migrations/000N_*.sql` (0001–0016) |
| `auth/` | Completo (TASK-009 a TASK-013) | `password.py`, `users.py`, `roles.py`, `api_keys.py`, `crypto.py`, `master_key.py` |
| `llm/` | Completo (TASK-014 a TASK-019) | `provider.py`, `providers/ollama_provider.py`, `protocol.py`, `protocol_validator.py`, `prompt.py`, `prompt_composer.py` |
| `policies/` | Implementado (TASK-022) | `execution_policy.py` |
| `orchestrator/` | Completo (TASK-020 a TASK-030, TASK-079) | `execution.py`, `execution_id.py`, `orchestrator.py`, `planner.py`, `plan_validator.py`, `replanner.py`, `loop_detector.py`, `cancellation.py` |
| `confidence/` | Completo (TASK-031 a TASK-036) | `model_confidence.py`, `volatility.py`, `confidence_engine.py`, `response_guardrail.py`, `revalidation_guardrail.py`, `ambiguity_guardrail.py` |
| `context/` | Completo (TASK-037 a TASK-043) | `context_manager.py`, `context_window.py` |
| `memory/` | Completo (TASK-044 a TASK-051) | `memory_model.py`, `retention_policy.py` |
| `knowledge/` | Completo (TASK-052 a TASK-058) | `knowledge_model.py`, `promotion_rule.py`, `usefulness.py` |
| `sources/` | Completo (TASK-059 a TASK-066) | `source_registry.py`, `reputation_rule.py`, `auto_block_rule.py`, `unblock_rule.py` |
| `tools/` | Em andamento (Memory/Knowledge Tools prontas; outras ferramentas são TASKs futuras) | `memory_tool.py`, `knowledge_tool.py` |
| `api/` | Completo (TASK-067 a TASK-073, TASK-079) | `app.py`, `auth.py`, `schemas.py`, `dependencies.py`, `executions.py`, `responses.py` |
| `usage/` | Completo (TASK-073) | `usage_model.py` |
| `queue/` | Completo (TASK-074 a TASK-077) | `queue_model.py`, `retention_policy.py` |
| Demais módulos (`quotas/`, `updater/`, `backup/`, ...) | Só README.md, sem código | — |

## Decisões técnicas já tomadas (ver `docs/DECISION_LOG.md` para o texto completo)

- **DEC-001/002:** projeto separado do AIShoppingAgent; raiz do repo é `C:\IA`.
- **DEC-003:** escopo formal de TASK-001 (estrutura + git init + commit).
- **DEC-004:** stack não escolhida na organização inicial.
- **DEC-005:** linguagem do backend = **Python** (`requires-python >= 3.11`).
- **DEC-006:** driver de PostgreSQL = **psycopg 3** (`psycopg[binary]`).
- **DEC-007:** biblioteca de criptografia = **`cryptography`** (Fernet).
- **DEC-008:** runtime **Ollama** instalado localmente (confirmado pelo
  usuário); SDK oficial `ollama` como client Python.
- **DEC-009:** framework web = **FastAPI** (com `uvicorn` como servidor
  ASGI), decidido via `AskUserQuestion` na TASK-067.
- **DEC-010:** Execution Trace **persistido** no PostgreSQL (tabela nova
  `execution_traces`, só o resumo) — decidido via `AskUserQuestion` na
  TASK-082.
- **DEC-011:** primeiro modelo Ollama baixado = **`qwen3:8b`**
  (provisório, não definitivo) — decidido via `AskUserQuestion` na
  TASK-087, para viabilizar a validação real do marco utilizável.
- **DEC-012:** primeiro provider de busca = **SearXNG local via Docker**
  — decidido via `AskUserQuestion` (três rodadas) na TASK-089, depois de
  testar e descartar DuckDuckGo na prática (bloqueio anti-bot real + API
  oficial vazia para buscas genéricas).
- **Ainda em aberto** (`docs/OPEN_QUESTIONS.md`, item 1): ORM, ferramenta de
  migration. Migrations hoje são SQL puro aplicado via `psql`
  (`backend/app/db/migrations/000N_*.sql`, numeração sequencial).
- **Modelo LLM definitivo:** ainda não escolhido de forma definitiva
  (`docs/OPEN_QUESTIONS.md`, item 3) — `qwen3:8b` está em uso como
  escolha provisória (`DEC-011`) desde a TASK-087, só para viabilizar
  validação real; a escolha definitiva continua exigindo testes
  sistemáticos, não esta validação pontual.
- **Limite fixo de memória (TASK-050):** `MAX_MEMORIES_PER_OWNER = 500`,
  escolhido em código sem exigir decisão de arquitetura formal (mesmo
  espírito de `DEFAULT_MAX_STEPS`, TASK-028) — não é um `DEC-0XX` no
  `DECISION_LOG.md`, só uma constante documentada no módulo.

## Estado do ambiente local (esta máquina)

- **PostgreSQL 17** instalado via `winget` (serviço Windows
  `postgresql-x64-17`, porta 5432, `C:\Program Files\PostgreSQL\17`).
  Banco `claudiao`, dono: role de aplicação `claudiao_app` (sem privilégio de
  superusuário). Superusuário `postgres` existe só para administração.
- **Ollama** instalado via `winget` (serviço em `http://localhost:11434`).
  **Modelo `qwen3:8b` baixado** desde a TASK-087 (`ollama pull qwen3:8b`,
  5.2GB, `DEC-011`) — `CLAUDIAO_ACTIVE_MODEL=qwen3:8b` em `config/.env`.
  `OllamaProvider` funciona contra esse modelo de verdade; respostas reais
  levam dezenas de segundos em CPU (~52s observado). **O usuário mantém o
  app Ollama aberto e pediu para nunca deixar testes passarem "pulados"
  por ele estar fechado** — abra o app (ou inicie o serviço) e re-rode a
  suíte antes de reportar resultados.
- **Docker Desktop** instalado nesta máquina (não foi instalado pela IA —
  já estava presente; só foi *iniciado* na TASK-089, já que não estava
  rodando). Executável real:
  `C:\Users\User\AppData\Local\Programs\DockerDesktop\Docker Desktop.exe`
  — `where docker`/PATH podem não resolver de primeira num shell novo;
  `docker --version`/`docker info` já funcionam direto neste ambiente.
  Container `claudiao-searxng` (imagem `searxng/searxng:latest`, porta
  `8888`, `--restart unless-stopped`) roda uma instância local do SearXNG
  (`DEC-012`) usada pelo `SearXNGSearchProvider` (TASK-089) — config em
  `config/searxng/settings.yml` (gerada pelo container, não versionada,
  `search.formats: [html, json]` habilitado manualmente pois vem
  desligado por padrão). Se o container não estiver rodando:
  `docker start claudiao-searxng`.
- **Credenciais reais:** `config/.env` (na raiz do repo, **nunca versionado** —
  confirme com `git check-ignore -v config/.env` se tiver dúvida). Os testes de
  integração/cenário (`tests/integration/`, `tests/scenarios/`) carregam esse
  arquivo automaticamente via `tests/conftest.py` (movido de
  `tests/integration/conftest.py` na TASK-086, para alcançar `tests/scenarios/`
  também) se as variáveis não estiverem no ambiente do processo, e pulam (não
  falham) se o serviço não estiver acessível — mesmo padrão para PostgreSQL
  (`postgres_dsn`) e Ollama (`ollama_provider`), mas ver o aviso acima sobre
  não aceitar esse pulo passivamente.
- **Python:** 3.14.6 instalado nesta máquina, mas `requires-python >= 3.11` no
  `backend/pyproject.toml` — não assumir 3.14 especificamente em código novo.
- **Dependências externas do backend:** `psycopg[binary]`, `cryptography`,
  `ollama`, `fastapi`, `uvicorn` (ver `backend/pyproject.toml`). Sem ambiente
  virtual criado ainda — os pacotes foram instalados com `python -m pip
  install` direto no Python do sistema. Nenhuma dependência nova para
  `web_search/` (TASK-088 a TASK-090) — tudo via `urllib.request`
  (biblioteca padrão).
- **Instalar programas novos (`winget install ...` ou equivalente) exige
  perguntar ao usuário primeiro**, mesmo nesta máquina de dev/teste — usar
  serviços já instalados (abrir o Ollama, rodar o Postgres) é livre; instalar
  algo novo não é.
- **Migrations aplicadas manualmente via `psql`** (0001 a 0016) — não há
  script/comando único que reaplique todas; cada TASK que criou uma migration
  a aplicou na hora com `psql -h 127.0.0.1 -p 5432 -U claudiao_app -d claudiao
  -f backend/app/db/migrations/000N_*.sql`, usando `CLAUDIAO_POSTGRES_PASSWORD`
  de `config/.env` como `PGPASSWORD`.

## Armadilhas e lições aprendidas (não óbvias)

1. **`.gitignore` tinha `*.sql` genérico** (pensado para dumps de backup) que
   escondia `backend/app/db/migrations/*.sql`, que é código versionável. Já
   corrigido com uma exceção (`!backend/app/db/migrations/*.sql`).
2. **O classificador de permissões do ambiente bloqueia edições em
   `pg_hba.conf`** (mesmo com autorização explícita do usuário no chat) — não
   insista tentando outras ferramentas para contornar. O caminho que funcionou
   para definir a senha do superusuário do Postgres foi reinstalar via
   `winget install ... --override "--superpassword ..."` na instalação,
   nunca editando a config de autenticação de uma instância já rodando.
3. **`--basetemp` do pytest:** o diretório temp padrão do Windows neste sandbox
   causa `PermissionError` em alguns setups/teardowns do pytest. Rodar com
   `--basetemp=".pytest_tmp"` (relativo ao repo) evita o problema; apagar
   `.pytest_tmp/` e `.pytest_cache/` depois, confirmando com `git status` que
   não sobrou lixo antes de commitar.
4. **Todo texto voltado ao usuário deve ser PT-BR**, incluindo descrições
   curtas de chamadas de ferramenta, não só o texto do chat — o usuário é
   estrito quanto a isso.
5. **Import circular evitado de propósito:** `app.auth.roles` opera sobre a
   *string* `role`, não sobre a classe `User` de `app.auth.users`, porque
   `users.py` importa `Role` de `roles.py`. Mesmo princípio replicado em
   `app.orchestrator.execution`, que importa `ModelStep` de `app.llm.protocol`
   (sentido único).
6. **`postgres_log_handler.py` reexporta `build_dsn_from_env`** de
   `app.db.connection` por compatibilidade — a fonte real da função é
   `app.db.connection`.
7. **`json.dumps` escapa acentos por padrão** (`\uXXXX`) — `ModelStep.to_json()`
   usa `ensure_ascii=False` de propósito, porque o protocolo é PT-BR
   (descoberto como bug real na TASK-019). Se criar mais serialização JSON de
   texto em português, lembre desse parâmetro.
8. **`dict(valor)` em cima de entrada não confiável pode levantar
   `ValueError`/`TypeError` genérico**, não um erro de domínio — `ModelStep.
   from_dict` agora valida `isinstance(parameters_raw, dict)` antes de
   `dict(...)` (bug de regressão corrigido na TASK-017). Ao decodificar JSON
   externo, prefira checar o tipo antes de converter.
9. **Ao escrever testes com providers fake que repetem `USE_TOOL`**, cuidado
   com parâmetros idênticos entre chamadas — a detecção de loop (TASK-029,
   threshold 3) dispara antes de `max_steps` se os parâmetros não mudarem.
   Testes que quiserem isolar `max_steps` (ou qualquer outro comportamento)
   de propósito precisam variar os parâmetros a cada chamada do provider
   fake (ver `_InfiniteToolProvider`/`_ProgressingToolProvider` em
   `tests/unit/test_max_steps.py`/`test_orchestrator_loop_detection.py`).
10. **Checkpoint de 10 em 10 é contado a partir do checkpoint anterior, não
    arredondado.** Já foi violado duas vezes (TASK-030 e TASK-050) por perder
    a contagem no meio de uma sequência longa de TASKs consecutivas — corrigido
    desta vez (TASK-060, no prazo) conferindo a contagem explicitamente ao
    concluir qualquer TASK terminada em 0. Mantenha esse hábito.
11. **Padrão de guardrail isolado (TASK-034/035/036, TASK-058):** quando a
    especificação pede um comportamento (bloquear LOW, exigir revalidação de
    VOLATILE, tratar ambiguidade, avaliar utilidade) mas os sistemas reais que
    alimentariam esse comportamento ainda não existem (evidências reais,
    contexto de execução real), a solução adotada é criar a função de guarda
    isolada recebendo o resultado já avaliado como parâmetro explícito
    (booleano/enum), em vez de tentar calculá-lo. Quem acopla a guarda ao
    fluxo real do orquestrador é uma TASK futura (em geral TASK-088+),
    explicitamente citada no docstring/Encerramento de cada uma. Guardrails
    desse tipo (`app.confidence.*`, `app.knowledge.usefulness`) nunca são
    expostos como operação de Tool — são decisões do orquestrador, não do
    modelo.
12. **Dataclasses de modelo nascem com todos os campos já presentes**
    (vazios/`None`/zero), e cada TASK seguinte só acrescenta métodos que
    operam sobre campos já existentes — não redesenha a dataclass. Padrão
    replicado em `Execution` (TASK-020), `ContextManager` (TASK-037),
    `Memory` (TASK-044) e `Knowledge` (TASK-052): campos como
    `use_count`/`root_id`/`scope_type`/`confidence` chegam com default antes
    da função que os usa de verdade existir.
13. **Checkpoint perdido duas vezes seguidas (TASK-030, TASK-050) pela mesma
    causa: sequência longa de TASKs consecutivas dentro do mesmo bloco
    funcional tira o foco da contagem de checkpoint.** Mitigação que
    funcionou na TASK-060: ao terminar QUALQUER TASK cujo número termine em
    0, parar e conferir explicitamente se é um múltiplo de 10 a partir do
    último checkpoint (não do zero) antes de seguir — não confiar em lembrar
    a regra "de cabeça" no meio de uma sequência longa.
14. **Nunca reportar testes pulados por Ollama indisponível como um fato
    ambiental aceitável.** Ollama está instalado e disponível nesta máquina —
    um skip significa que o serviço não está rodando *agora*, não que é
    inacessível. Abrir o Ollama (o usuário confirmou que pode ser feito
    livremente) e re-rodar a suíte antes de reportar "N testes passando".
15. **Modelo de conhecimento com linhagem/versão (TASK-054) exige atenção em
    limpeza de teste:** `root_id` agrupa todas as versões de um fato; ao
    limpar dados de teste, sempre `DELETE ... WHERE root_id = %s`, nunca
    `WHERE id = %s` — `NEW_VERSION`/`create_new_version` cria linhas novas
    com `id` diferente na mesma linhagem, que ficariam órfãs.
16. **Tabelas com FK para `knowledge`/`memories` precisam de `ON DELETE
    CASCADE`** quando a remoção em teste (ou uso administrativo) da linha
    pai é esperada — descoberto ao criar `knowledge_evidence` (TASK-056) sem
    isso, quebrando a limpeza de testes que criavam evidências. Corrigido na
    própria migration antes de commitar.
17. **Registrar um código de erro em `register_error()` não atualiza
    `docs/ERROR_CATALOG.md` sozinho** — já aconteceu duas vezes (código
    `2002` na TASK-067, só documentado na TASK-069; códigos `4006`/`4007`/
    `4008` das TASK-034/035/036, só documentados na TASK-070). Ao registrar
    qualquer erro novo, conferir se a tabela de `docs/ERROR_CATALOG.md` já
    tem TODOS os códigos existentes no catálogo real
    (`backend/app/errors/catalog.py`), não só o que a TASK atual está
    adicionando.
18. **Cancelamento cooperativo (`CancellationToken`, TASK-030) não é
    preemptivo** — só é observado no início de cada `run_step`, antes de
    chamar o modelo. Para aplicar um limite de tempo de verdade num fluxo de
    uma única etapa `RESPOND` (o caso comum), onde não há um segundo `run_step`
    para checar o token, é preciso um limite externo à checagem cooperativa —
    a TASK-070 resolveu isso rodando `run_until_response` num worker de
    `ThreadPoolExecutor` e usando `future.result(timeout=...)` na thread da
    requisição HTTP. Isso preserva "sem threads/async" do lado do
    orquestrador (só uma thread por vez escreve em `Execution` — a thread da
    requisição para de tocar `execution` assim que segue pelo caminho de
    timeout) enquanto dá um limite real e testável sem depender de timing
    exato entre threads (o teste de timeout usa um provider fake que dorme
    muito mais que o timeout configurado, então o resultado nunca é
    ambíguo).
19. **O mesmo padrão de single-writer da TASK-070 (item 18) se repete
    sempre que um objeto mutável em memória é compartilhado entre a
    thread da requisição HTTP e a thread do `ThreadPoolExecutor` rodando
    o orquestrador.** A TASK-079 aplicou a mesma regra a `ExecutionTrace`
    (`trace`, além de `execution`): a thread principal só chama
    `trace.finish(...)` nos desfechos em que sabe que a thread do
    orquestrador já terminou de vez (sucesso, falha de modelo/ferramenta
    — não no timeout). Ao adicionar qualquer novo objeto mutável passado
    para `run_until_response`, replicar essa mesma disciplina.
20. **Quando a especificação pede uma métrica/comportamento mas nenhuma
    TASK anterior gravou o sinal necessário em lugar nenhum** (ex.:
    TASK-080, "respostas bloqueadas por baixa confiança" — os guardrails
    de confiança nunca disparam de verdade porque não estão acoplados ao
    orquestrador, item 11), a solução adotada foi **implementar a função
    de qualquer forma, corretamente, mesmo que hoje sempre devolva vazio/
    zero na prática**, e documentar isso explicitamente como lacuna
    conhecida (no docstring do módulo e em `docs/OBSERVABILITY.md`) — não
    inventar a coleta de dado que falta (isso seria adiantar uma TASK
    futura de conexão, mesmo tipo de trabalho que a TASK-079 fez para
    etapas/tempos) nem simplesmente pular a métrica sem registrar por
    quê. Mesmo espírito do item 11, generalizado para métricas.
21. **`logging_config.py` decide "já configurado" (`_configured`, flag de
    módulo) na primeira chamada de `get_logger()` de todo o processo —
    inclusive durante a *coleta* do pytest** (ex.: ao importar
    `health_check.py`). Em execução normal da suíte isso nunca dá
    problema, porque `CLAUDIAO_POSTGRES_*` só existe depois, via fixture
    `postgres_dsn` (por teste) — mas com `config/.env` carregado no
    ambiente do processo *antes* do `pytest` (necessário para o cenário
    de modelo real da TASK-087 rodar em vez de pular), o handler do
    PostgreSQL é anexado ao logger raiz já na coleta e fica assim para o
    resto da execução, quebrando testes que assumiam "só existe 1
    handler" ou que um logger de teste próprio não teria entrega
    duplicada via propagação. Corrigido isolando `CLAUDIAO_POSTGRES_*`
    explicitamente nos testes afetados (`monkeypatch.delenv`,
    `logger.propagate = False`) — não a fonte do problema em si, que
    continua sendo uma fragilidade conhecida de `logging_config.py`
    (TASK-005). Se criar mais testes de logging, isolar essas variáveis
    de propósito, não assumir que o ambiente do processo está "limpo".
22. **Bypass de proteção anti-bot é uma linha que não se cruza, mesmo sob
    pressão de "só preciso que funcione".** Na TASK-089, o endpoint de
    scraping HTML do DuckDuckGo retornou um desafio `anomaly.js` em vez
    de resultados — a resposta correta foi reportar o achado ao usuário e
    pedir direção (não tentar emular browser/resolver o desafio), o que
    levou à escolha de SearXNG como alternativa legítima. Vale para
    qualquer TASK futura que toque scraping de terceiros.
23. **Docker Desktop neste ambiente não fica no PATH nem em `C:\Program
    Files\Docker`** — o executável real é
    `C:\Users\User\AppData\Local\Programs\DockerDesktop\Docker
    Desktop.exe` (instalação por usuário, não por máquina). `docker
    --version`/`docker info` já resolvem direto num shell novo mesmo
    com o Docker Desktop fechado (só falham na conexão com o daemon,
    "failed to connect... dockerDesktopLinuxEngine") — iniciar o app e
    aguardar ~20s antes de repetir o comando resolve.

## Workflow que está sendo seguido

```
TASK → branch task-XXX → implementação → testes → docs → commit
     → merge na main local → push da branch (sempre)
     → (push da main + HANDOFF.md: a cada 10 TASKs ou pedido explícito)
```

Detalhes completos em `AGENTS.md`. Todas as branches `task-XXX` desde
`task-003` foram enviadas ao GitHub (regra: toda branch sobe assim que a TASK
termina, sem precisar pedir); não são deletadas depois do merge.

## Próximos passos imediatos

**TASK-091 — Implementar normalização HTML/text/JSON/XML** (dependência:
TASK-090 concluída). Continua o bloco "Web" (TASK-088 a TASK-094, ver
`docs/TOOLS.md` e `docs/BACKLOG.md`): `WebSearchProvider` (TASK-088),
`SearXNGSearchProvider` (TASK-089) e `open_page` (TASK-090) já existem —
falta normalizar o conteúdo bruto (`PageContent.body`) por tipo antes de
qualquer uso real. TASK-092 (extração de referências) e TASK-093
(política de PDF seguro) constroem em cima. Nenhuma decisão de
arquitetura nova esperada para TASK-091 (só transformar bytes já obtidos,
sem escolha de fornecedor envolvida) — mas confirmar lendo o próprio
`docs/tasks/TASK-091.md` antes de assumir isso. **Próximo checkpoint de
10 TASKs devido na TASK-100** — conferir a contagem explicitamente ao
concluir qualquer TASK terminada em 0 (ver item 13 de "Armadilhas").

Lembrete de sequenciamento: ao terminar qualquer TASK, anunciar
proativamente número + título da próxima TASK pendente — mas só começar
a executá-la quando o usuário pedir explicitamente (não é mais "IA
executa sozinho a próxima", isso foi corrigido depois de um mal-entendido
nesta janela).

## Histórico de checkpoints

- **2026-08-16 — TASK-010:** primeiro checkpoint de 10 TASKs. Fundação
  completa + autenticação/autorização básicas. 60/60 testes.
- **2026-08-16 — TASK-020:** segundo checkpoint. Blocos "Segurança e
  identidade" e "LLM" completos; bloco "Orquestração" iniciado (modelo de
  `Execution`). Ollama instalado e rodando localmente (sem modelo baixado).
  161/161 testes.
- **2026-08-16 — TASK-030:** terceiro checkpoint — feito com atraso (deveria
  ter sido automático ao concluir a TASK-030, só rodou quando o usuário
  perguntou pelo status). Bloco "Orquestração" completo. 247/247 testes.
- **2026-08-18 — TASK-040:** quarto checkpoint, no prazo. Bloco "Confiança e
  guardrails" completo; bloco "Contexto" iniciado. 306/306 testes.
- **2026-08-18 — TASK-050/TASK-051:** quinto checkpoint — feito com atraso de
  uma TASK. Blocos "Contexto" e "Memória" completos. 379/379 testes.
- **2026-08-19 — TASK-060:** sexto checkpoint, no prazo certo pela primeira
  vez desde o atraso da TASK-030. Bloco "Conhecimento" completo
  (RAW/PROVISIONAL/CONFIRMED, versionamento, escopo, evidências, promoção,
  utilidade); bloco "Fontes" iniciado (cadastro + tipo). 487/487 testes.
- **2026-08-19 — TASK-070:** sétimo checkpoint, no prazo. Bloco "Fontes"
  completo (reputação, histórico, blacklist, bloqueio automático,
  desbloqueio só `ADMIN`); bloco "Aplicações" iniciado (API FastAPI local
  — DEC-009 —, autenticação, validação de payload, execução síncrona
  real, timeout aplicado de fato via `ThreadPoolExecutor` +
  `future.result(timeout=...)`). 562/562 testes.
- **2026-08-21 — TASK-080:** oitavo checkpoint, no prazo. Bloco
  "Aplicações" completo (erro de timeout específico, resposta JSON final
  com envelope `success`, rastreio de consumo); bloco "Fila" completo
  (FIFO persistida, estados, retenção/limpeza); bloco "Observabilidade
  inicial" iniciado (Execution Trace conectado de verdade ao
  orquestrador — etapas/ferramentas/tempos reais —, métricas básicas com
  5 lacunas conhecidas documentadas). 668/668 testes.
- **2026-08-21 — TASK-090 (este checkpoint):** nono checkpoint, no prazo.
  Bloco "Observabilidade inicial" completo (painel web read-only —
  Fila/Execuções/Erros/Logs/Consumo —, Execution Trace persistido —
  `DEC-010` —, health check inicial); bloco "Marco utilizável inicial"
  completo — **TASK-087, marco oficial do primeiro Claudião utilizável,
  atingido nesta janela**, com modelo `qwen3:8b` baixado (`DEC-011`) e
  validação real de ponta a ponta sem fakes; bloco "Web" iniciado
  (`WebSearchProvider`, `SearXNGSearchProvider` contra SearXNG local via
  Docker — `DEC-012` —, `open_page`). 764/764 testes.
