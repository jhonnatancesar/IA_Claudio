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

**Data:** 2026-08-18 · **TASK:** TASK-040 · **TASKs concluídas:** 40 de 147
(TASK-001 a TASK-040) · **Próxima TASK executável:** TASK-041 — Implementar
detecção de troca de assunto.

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
- **Bloco "Contexto" em andamento (TASK-037 a TASK-040 concluídas, de
  TASK-037 a TASK-043):** `ContextManager` — uma instância por conversa,
  guardando assunto principal (`set_active_topic`), entidades recentes
  (`track_entity`, ordem de recência), referências implícitas
  (`set_implicit_reference`/`resolve_reference`) e correções do usuário
  (`record_correction`). Faltam: detecção de troca de assunto (TASK-041) e
  monitor de janela de contexto + aviso em 80% (TASK-042/TASK-043).
- **Testes:** 306/306 aprovados (unitários + integração real contra PostgreSQL
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
| `db/` | Implementado (TASK-003/004/009) | `connection.py`, `migrations/000N_*.sql` |
| `auth/` | Completo (TASK-009 a TASK-013) | `password.py`, `users.py`, `roles.py`, `api_keys.py`, `crypto.py`, `master_key.py` |
| `llm/` | Completo (TASK-014 a TASK-019) | `provider.py`, `providers/ollama_provider.py`, `protocol.py`, `protocol_validator.py`, `prompt.py`, `prompt_composer.py` |
| `policies/` | Implementado (TASK-022) | `execution_policy.py` |
| `orchestrator/` | Completo (TASK-020 a TASK-030) | `execution.py`, `execution_id.py`, `orchestrator.py`, `planner.py`, `plan_validator.py`, `replanner.py`, `loop_detector.py`, `cancellation.py` |
| `confidence/` | Completo (TASK-031 a TASK-036) | `model_confidence.py`, `volatility.py`, `confidence_engine.py`, `response_guardrail.py`, `revalidation_guardrail.py`, `ambiguity_guardrail.py` |
| `context/` | Em andamento (TASK-037 a TASK-040 de TASK-037 a TASK-043) | `context_manager.py` |
| Demais módulos (`api/`, `memory/`, `knowledge/`, `panel/`, `tools/`, ...) | Só README.md, sem código | — |

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
    arredondado** — o segundo checkpoint foi na TASK-020, então o terceiro
    foi na TASK-030 e este (quarto) é exatamente na TASK-040. Simples soma,
    sem lógica escondida.
11. **Padrão de guardrail isolado (TASK-034/035/036):** quando a especificação
    pede um comportamento (bloquear LOW, exigir revalidação de VOLATILE,
    tratar ambiguidade) mas os sistemas reais que alimentariam esse
    comportamento ainda não existem (evidências reais, Knowledge Tool,
    avaliação de ambiguidade do `ContextManager`), a solução adotada é criar
    a função de guarda isolada recebendo o resultado já avaliado como
    parâmetro explícito (booleano/enum), em vez de tentar calculá-lo. Quem
    acopla a guarda ao fluxo real do orquestrador é uma TASK futura,
    explicitamente citada no docstring/Encerramento de cada uma.
12. **`ContextManager` (TASK-037) nasceu com todos os campos já presentes**
    (vazios/`None`), e cada TASK seguinte (038/039/040) só acrescenta
    métodos que operam sobre campos já existentes — não redesenha o
    dataclass. Mesmo padrão de `Execution` (TASK-020), que já tinha
    `observations` antes de `set_last_observation` existir (TASK-026).

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

**TASK-041 — Implementar detecção de troca de assunto** (dependência:
TASK-040 concluída). `ContextManager.set_active_topic` (TASK-038) já troca o
valor do assunto principal quando chamado, mas não decide *quando* chamar —
TASK-041 deve decidir isso (critério de detecção não detalhado na
especificação mestre, seção 9, além de "limpa referências antigas quando
houver mudança real de tópico"). Prováveis candidatos a limpar junto:
`recent_entities`/`implicit_references`. TASK-042 (monitor de janela de
contexto) e TASK-043 (aviso em 80%) fecham o bloco "Contexto" — depois disso
começa o bloco "Memória" (TASK-044 a TASK-051, ver `docs/BACKLOG.md`).

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
- **2026-08-18 — TASK-040 (este checkpoint):** quarto checkpoint, no prazo.
  Bloco "Confiança e guardrails" completo (confiança do modelo, volatilidade,
  Confidence Engine, três guardrails de bloqueio isolados — LOW, VOLATILE não
  revalidada, ambiguidade não resolvida). Bloco "Contexto" iniciado:
  `ContextManager` com assunto principal, rastreamento de entidades/
  referências implícitas e correção de contexto. 306/306 testes.
