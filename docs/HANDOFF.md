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

**Data:** 2026-08-18 · **TASK:** TASK-051 · **TASKs concluídas:** 51 de 147
(TASK-001 a TASK-051) · **Próxima TASK executável:** TASK-052 — Criar modelo
RAW/PROVISIONAL/CONFIRMED.

Este checkpoint deveria ter rodado automaticamente na TASK-050 (10 TASKs desde
o checkpoint anterior, TASK-040) e não rodou — mesmo erro já registrado no
histórico de checkpoints da TASK-030. Corrigido assim que percebido, cobrindo
TASK-050 e TASK-051 juntas. Ver item 13 de "Armadilhas" abaixo.

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
  confiança do modelo (`get_model_confidence`, `is_at_least`), volatilidade
  (`Volatility`, `requires_revalidation`), Confidence Engine (`EvidenceStrength`,
  `calculate_final_confidence`), bloqueio de resposta conclusiva em `LOW`
  (código 4006), regra obrigatória de revalidação de informação `VOLATILE`
  (código 4007), tratamento de ambiguidade — bloqueio de resposta sem pergunta
  de esclarecimento (código 4008). Todos os guardrails de bloqueio recebem a
  avaliação (confiança final, volatilidade, ambiguidade) já pronta de quem
  chama — nenhum é acionado ainda no fluxo real do `ExecutionOrchestrator`.
- **Bloco "Contexto" completo (TASK-037 a TASK-043):** `ContextManager` — uma
  instância por conversa, guardando assunto principal (`set_active_topic`),
  entidades recentes (`track_entity`), referências implícitas
  (`set_implicit_reference`/`resolve_reference`), correções do usuário
  (`record_correction`) e detecção de troca real de assunto
  (`detect_topic_switch`, limpa entidades/referências ao trocar).
  `ContextWindowMonitor` (`usage_ratio`/`is_full`/`requires_warning`, 80%)
  monitora uso da janela de contexto, capacidade recebida por parâmetro (sem
  painel ainda).
- **Bloco "Memória" completo (TASK-044 a TASK-051):** modelo persistente real
  no PostgreSQL (`memories`: `save_memory`/`get_memory`), separação garantida
  por dono (`list_memories_for_owner`), Memory Tool (`execute_memory_tool`,
  operações `SAVE`/`LIST`/`SEARCH`), busca por conteúdo (`search_memories`),
  rastreamento de uso e relevância heurística (`record_memory_usage`,
  `relevance_score`), política de retenção por idade+relevância
  (`apply_retention_policy`), limite fixo de 500 por dono
  (`enforce_memory_limit`) e auditoria mínima de remoção sem guardar
  conteúdo (`memory_removal_audit`, `delete_memory(reason)`,
  `list_removal_audit_for_owner`).
- **Testes:** 379/379 aprovados (unitários + integração real contra PostgreSQL
  e Ollama locais). Rodar com:
  ```
  python -m pytest tests/ -v --basetemp=".pytest_tmp"
  ```
  (o `--basetemp` local é necessário neste ambiente — ver "Armadilhas" abaixo.)

## Mapa de código (backend/app/)

| Módulo | Status | Arquivos |
|---|---|---|
| `errors/` | Implementado (TASK-007/008) | `catalog.py`, `response.py` |
| `observability/` | Implementado (TASK-005/006) | `logging_config.py`, `postgres_log_handler.py` |
| `db/` | Implementado (TASK-003/004/009/044/048/051) | `connection.py`, `migrations/000N_*.sql` (0001–0005) |
| `auth/` | Completo (TASK-009 a TASK-013) | `password.py`, `users.py`, `roles.py`, `api_keys.py`, `crypto.py`, `master_key.py` |
| `llm/` | Completo (TASK-014 a TASK-019) | `provider.py`, `providers/ollama_provider.py`, `protocol.py`, `protocol_validator.py`, `prompt.py`, `prompt_composer.py` |
| `policies/` | Implementado (TASK-022) | `execution_policy.py` |
| `orchestrator/` | Completo (TASK-020 a TASK-030) | `execution.py`, `execution_id.py`, `orchestrator.py`, `planner.py`, `plan_validator.py`, `replanner.py`, `loop_detector.py`, `cancellation.py` |
| `confidence/` | Completo (TASK-031 a TASK-036) | `model_confidence.py`, `volatility.py`, `confidence_engine.py`, `response_guardrail.py`, `revalidation_guardrail.py`, `ambiguity_guardrail.py` |
| `context/` | Completo (TASK-037 a TASK-043) | `context_manager.py`, `context_window.py` |
| `memory/` | Completo (TASK-044 a TASK-051) | `memory_model.py`, `retention_policy.py` |
| `tools/` | Em andamento (TASK-046/047; próximas TASKs de outras ferramentas) | `memory_tool.py` |
| Demais módulos (`api/`, `knowledge/`, `panel/`, ...) | Só README.md, sem código | — |

## Decisões técnicas já tomadas (ver `docs/DECISION_LOG.md` para o texto completo)

- **DEC-001/002:** projeto separado do AIShoppingAgent; raiz do repo é `C:\IA`.
- **DEC-003:** escopo formal de TASK-001 (estrutura + git init + commit).
- **DEC-004:** stack não escolhida na organização inicial.
- **DEC-005:** linguagem do backend = **Python** (`requires-python >= 3.11`).
- **DEC-006:** driver de PostgreSQL = **psycopg 3** (`psycopg[binary]`).
- **DEC-007:** biblioteca de criptografia = **`cryptography`** (Fernet).
- **DEC-008:** runtime **Ollama** instalado localmente (confirmado pelo
  usuário); SDK oficial `ollama` como client Python.
- **Ainda em aberto** (`docs/OPEN_QUESTIONS.md`, item 1): framework web, ORM,
  ferramenta de migration. Migrations hoje são SQL puro aplicado via `psql`
  (`backend/app/db/migrations/000N_*.sql`, numeração sequencial).
- **Modelo LLM definitivo:** não escolhido, intencionalmente
  (`docs/OPEN_QUESTIONS.md`, item 3) — Ollama está instalado e rodando, mas
  nenhum modelo foi puxado (`ollama pull`).
- **Limite fixo de memória (TASK-050):** `MAX_MEMORIES_PER_OWNER = 500`,
  escolhido em código sem exigir decisão de arquitetura formal (mesmo
  espírito de `DEFAULT_MAX_STEPS`, TASK-028) — não é um `DEC-0XX` no
  `DECISION_LOG.md`, só uma constante documentada no módulo.

## Estado do ambiente local (esta máquina)

- **PostgreSQL 17** instalado via `winget` (serviço Windows
  `postgresql-x64-17`, porta 5432, `C:\Program Files\PostgreSQL\17`).
  Banco `claudiao`, dono: role de aplicação `claudiao_app` (sem privilégio de
  superusuário). Superusuário `postgres` existe só para administração.
- **Ollama** instalado via `winget` (serviço rodando em
  `http://localhost:11434`). **Nenhum modelo baixado** — `OllamaProvider`
  funciona, mas `complete()` levanta `LocalLLMProviderError` para qualquer
  modelo, já que nenhum existe localmente ainda.
- **Credenciais reais:** `config/.env` (na raiz do repo, **nunca versionado** —
  confirme com `git check-ignore -v config/.env` se tiver dúvida). Os testes de
  integração (`tests/integration/`) carregam esse arquivo automaticamente via
  `tests/integration/conftest.py` se as variáveis não estiverem no ambiente do
  processo, e pulam (não falham) se o serviço não estiver acessível — mesmo
  padrão para PostgreSQL (`postgres_dsn`) e Ollama (`ollama_provider`).
- **Python:** 3.14.6 instalado nesta máquina, mas `requires-python >= 3.11` no
  `backend/pyproject.toml` — não assumir 3.14 especificamente em código novo.
- **Dependências externas do backend:** `psycopg[binary]`, `cryptography`,
  `ollama` (ver `backend/pyproject.toml`). Sem ambiente virtual criado ainda —
  os pacotes foram instalados com `python -m pip install` direto no Python do
  sistema.
- **Migrations aplicadas manualmente via `psql`** (0001 a 0005) — não há
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
    arredondado.** Ver item 13 abaixo — essa regra já foi violada duas vezes
    (TASK-030 e TASK-050) por eu perder a contagem no meio de uma sequência
    longa de TASKs consecutivas.
11. **Padrão de guardrail isolado (TASK-034/035/036):** quando a especificação
    pede um comportamento (bloquear LOW, exigir revalidação de VOLATILE,
    tratar ambiguidade) mas os sistemas reais que alimentariam esse
    comportamento ainda não existem (evidências reais, Knowledge Tool,
    avaliação de ambiguidade do `ContextManager`), a solução adotada é criar
    a função de guarda isolada recebendo o resultado já avaliado como
    parâmetro explícito (booleano/enum), em vez de tentar calculá-lo. Quem
    acopla a guarda ao fluxo real do orquestrador é uma TASK futura,
    explicitamente citada no docstring/Encerramento de cada uma.
12. **`ContextManager`/`Memory` nasceram com todos os campos já presentes**
    (vazios/`None`/zero), e cada TASK seguinte só acrescenta métodos que
    operam sobre campos já existentes — não redesenha o dataclass. Mesmo
    padrão de `Execution` (TASK-020), que já tinha `observations` antes de
    `set_last_observation` existir (TASK-026). Exemplo mais recente: `Memory`
    (TASK-044) já tinha `use_count`/`last_used_at` com defaults antes de
    `record_memory_usage` (TASK-048) existir.
13. **Checkpoint perdido de novo, agora na TASK-050 (mesmo erro da TASK-030):**
    o quarto checkpoint (TASK-040) tinha deixado escrito "próximo checkpoint
    automático... é na TASK-040" só até ali; o quinto checkpoint devido era
    exatamente 10 TASKs depois, na TASK-050 — mas isso não foi executado
    quando a TASK-050 terminou, só quando o usuário pediu para listar as
    TASKs restantes e a contagem foi refeita manualmente durante a TASK-051.
    Causa provável: numa sequência longa de TASKs consecutivas dentro do
    mesmo bloco funcional ("Memória", TASK-044 a TASK-051), a atenção fica no
    conteúdo de cada TASK e a contagem de checkpoint não é revisitada a cada
    conclusão. Mitigação prática: ao terminar QUALQUER TASK cujo número
    termine em 0, parar e conferir explicitamente se é um múltiplo de 10 a
    partir do último checkpoint (não do zero) antes de seguir para a
    próxima — não confiar em lembrar da regra "de cabeça" no meio de uma
    sequência longa.

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

**TASK-052 — Criar modelo RAW/PROVISIONAL/CONFIRMED** (dependência: TASK-051
concluída). Abre o bloco "Conhecimento" (TASK-052 a TASK-058, ver
`docs/KNOWLEDGE.md` e `docs/BACKLOG.md`) — os três estágios de confiabilidade
de um fato aprendido pelo agente, separado de memória (TASK-044+) e de
contexto imediato (TASK-037+). TASK-053 (Knowledge Tool), TASK-054
(versionamento), TASK-055 (escopo GLOBAL/APPLICATION), TASK-056
(evidências/fontes), TASK-057 (promoção para CONFIRMED), TASK-058 (avaliação
de utilidade pelo orquestrador) constroem em cima. **Próximo checkpoint de 10
TASKs devido na TASK-060** — conferir a contagem explicitamente ao concluir
qualquer TASK terminada em 0 (ver item 13 de "Armadilhas").

## Histórico de checkpoints

- **2026-08-16 — TASK-010:** primeiro checkpoint de 10 TASKs. Fundação
  completa + autenticação/autorização básicas. 60/60 testes.
- **2026-08-16 — TASK-020:** segundo checkpoint. Blocos "Segurança e
  identidade" e "LLM" completos; bloco "Orquestração" iniciado (modelo de
  `Execution`). Ollama instalado e rodando localmente (sem modelo baixado).
  161/161 testes.
- **2026-08-16 — TASK-030:** terceiro checkpoint — feito com atraso (deveria
  ter sido automático ao concluir a TASK-030, só rodou quando o usuário
  perguntou pelo status). Bloco "Orquestração" completo: ciclo inteiro de
  execução (planejamento, validação, execução por etapas, replanejamento,
  `max_steps`, detecção de loop, cancelamento). 247/247 testes.
- **2026-08-18 — TASK-040:** quarto checkpoint, no prazo. Bloco "Confiança e
  guardrails" completo (confiança do modelo, volatilidade, Confidence Engine,
  três guardrails de bloqueio isolados — LOW, VOLATILE não revalidada,
  ambiguidade não resolvida). Bloco "Contexto" iniciado: `ContextManager` com
  assunto principal, rastreamento de entidades/referências implícitas e
  correção de contexto. 306/306 testes.
- **2026-08-18 — TASK-050/TASK-051 (este checkpoint):** quinto checkpoint —
  feito com atraso de uma TASK (deveria ter sido automático ao concluir a
  TASK-050; só rodou ao concluir a TASK-051, quando a contagem foi refeita
  manualmente). Bloco "Contexto" completo (detecção de troca de assunto,
  monitor de janela + aviso em 80%). Bloco "Memória" completo (modelo
  persistente, separação por dono, Memory Tool, busca estruturada,
  relevância/frequência/last used, retenção, limite fixo de 500 por dono,
  auditoria de remoção sem guardar conteúdo). 379/379 testes.
