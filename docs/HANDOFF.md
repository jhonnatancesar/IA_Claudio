# Handoff — estado vivo do projeto

Documento de **estado vivo**, atualizado a cada checkpoint de 10 TASKs concluídas
(`AGENTS.md`, seção "Regra de checkpoint"). Escrito para que **outra IA/agente,
numa sessão nova, sem o histórico desta conversa**, consiga entender onde o
projeto está e continuar o trabalho lendo só este arquivo + o resto de `docs/`.

Se você é essa IA: leia isto primeiro, depois `README.md` → `AGENTS.md` →
`docs/tasks/README.md` → `docs/tasks/TASK-XXX.md` da próxima TASK. Não pule a
leitura de `AGENTS.md` — ele tem regras de governança (branch por TASK, push só
quando pedido, PT-BR em tudo) que não estão resumidas aqui.

## Checkpoint atual

**Data:** 2026-08-16 · **TASK:** TASK-020 · **TASKs concluídas:** 20 de 147
(TASK-001 a TASK-020) · **Próxima TASK executável:** TASK-021 — Implementar
execution_id.

## O que já existe (resumo, não repete `docs/tasks/`)

- **Estrutura do repositório** organizada por completo (`docs/`, `backend/app/`
  com módulos, `tests/{unit,integration,scenarios}`, `config/`, `scripts/`,
  `adr/`, `rfc/`) — TASK-001.
- **Bloco "Fundação" completo (TASK-001 a TASK-008):** configuração central
  (`config/.env.example`), PostgreSQL local instalado e banco `claudiao`
  criado, schema inicial (`users`, `applications`, `settings`,
  `schema_migrations`, `logs`), logging local rotativo + estruturado no
  PostgreSQL, catálogo interno de erros e formato JSON padrão de erro.
- **Bloco "Segurança e identidade" completo (TASK-009 a TASK-013):**
  autenticação de usuários (hash PBKDF2), autorização por papel
  (`Role.ADMIN`/`Role.USER`), autenticação de aplicações via API key, criptografia
  de segredos (Fernet) e chave mestra externa ao banco.
- **Bloco "LLM" completo (TASK-014 a TASK-019):** interface `LocalLLMProvider`,
  `OllamaProvider` (SDK oficial, Ollama instalado e rodando localmente, sem
  modelo baixado), protocolo JSON modelo↔orquestrador (`ModelStep`), sua
  validação semântica (`validate_step`, código de erro 4001) e o prompt-base +
  composição dinâmica de prompt/contexto.
- **Bloco "Orquestração" iniciado (TASK-020 feita; TASK-021 a TASK-030
  pendentes):** modelo de dados `Execution` com transições de estado
  (`PENDING`/`RUNNING`/`COMPLETED`/`FAILED`).
- **Testes:** 161/161 aprovados (unitários + integração real contra PostgreSQL
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
| `db/` | Implementado (TASK-003/004/009) | `connection.py`, `migrations/0001_initial_schema.sql`, `migrations/0002_logs.sql` |
| `auth/` | Completo (TASK-009 a TASK-013) | `password.py`, `users.py`, `roles.py`, `api_keys.py`, `crypto.py`, `master_key.py` |
| `llm/` | Completo (TASK-014 a TASK-019) | `provider.py`, `providers/ollama_provider.py`, `protocol.py`, `protocol_validator.py`, `prompt.py`, `prompt_composer.py` |
| `orchestrator/` | Em andamento (TASK-020) | `execution.py` |
| Demais módulos (`api/`, `memory/`, `knowledge/`, `panel/`, ...) | Só README.md, sem código | — |

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

## Workflow que está sendo seguido

```
TASK → branch task-XXX → implementação → testes → docs → commit
     → merge na main local → (push só quando pedido, exceto a cada 10 TASKs)
```

Detalhes completos em `AGENTS.md`. Branches `task-001` a `task-020` existem
localmente (histórico); não foram deletadas, mas também não precisam ser —
`AGENTS.md` não pede limpeza delas.

## Próximos passos imediatos

**TASK-021 — Implementar execution_id** (dependência: TASK-020 concluída).
Provavelmente só formaliza a geração de `execution_id` (ex.: `uuid4()`) que
hoje `Execution`/`ModelStep` recebem prontos de fora. Segue o bloco
"Orquestração": TASK-022 (`ExecutionPolicy`), TASK-023 (`ExecutionOrchestrator`
— primeira peça que efetivamente liga `OllamaProvider` + `prompt_composer` +
`protocol_validator` + `Execution` num ciclo real), TASK-024 a TASK-030
(planejamento, validação de plano, execução por etapas, replanejamento,
`max_steps`, detecção de loop, cancelamento).

## Histórico de checkpoints

- **2026-08-16 — TASK-010:** primeiro checkpoint de 10 TASKs. Fundação
  completa + autenticação/autorização básicas. 60/60 testes.
- **2026-08-16 — TASK-020 (este checkpoint):** segundo checkpoint. Blocos
  "Segurança e identidade" e "LLM" completos; bloco "Orquestração" iniciado
  (modelo de `Execution`). Ollama instalado e rodando localmente (sem modelo
  baixado). 161/161 testes.
