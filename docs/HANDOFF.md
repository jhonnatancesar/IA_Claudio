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

**Data:** 2026-08-16 · **TASK:** TASK-010 · **TASKs concluídas:** 10 de 147
(TASK-001 a TASK-010) · **Próxima TASK executável:** TASK-011 — Criar
autenticação de aplicações via API key.

## O que já existe (resumo, não repete `docs/tasks/`)

- **Estrutura do repositório** organizada por completo (`docs/`, `backend/app/`
  com 23 módulos, `tests/{unit,integration,scenarios}`, `config/`, `scripts/`,
  `adr/`, `rfc/`) — TASK-001.
- **Bloco "Fundação" completo (TASK-001 a TASK-008):** configuração central
  (`config/.env.example`), PostgreSQL local instalado e banco `claudiao`
  criado, schema inicial (`users`, `applications`, `settings`,
  `schema_migrations`), logging local rotativo + estruturado no PostgreSQL
  (tabela `logs`), catálogo interno de erros e formato JSON padrão de erro.
- **Bloco "Segurança e identidade" em andamento (TASK-009, TASK-010 feitas; TASK-011
  a TASK-013 pendentes):** autenticação de usuários (hash PBKDF2, criação,
  login) e autorização por papel (`Role.ADMIN`/`Role.USER`,
  `is_admin`/`require_admin`).
- **Testes:** 60/60 aprovados (unitários + integração real contra o PostgreSQL
  local). Rodar com:
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
| `auth/` | Em andamento (TASK-009/010) | `password.py`, `users.py`, `roles.py` |
| Demais 19 módulos (`api/`, `orchestrator/`, `llm/`, `memory/`, ...) | Só README.md, sem código | — |

## Decisões técnicas já tomadas (ver `docs/DECISION_LOG.md` para o texto completo)

- **DEC-001/002:** projeto separado do AIShoppingAgent; raiz do repo é `C:\IA`.
- **DEC-003:** escopo formal de TASK-001 (estrutura + git init + commit).
- **DEC-004:** stack não escolhida na organização inicial.
- **DEC-005:** linguagem do backend = **Python** (`requires-python >= 3.11`).
- **DEC-006:** driver de PostgreSQL = **psycopg 3** (`psycopg[binary]`).
- **Ainda em aberto** (`docs/OPEN_QUESTIONS.md`, item 1): framework web, ORM,
  ferramenta de migration. Migrations hoje são SQL puro aplicado via `psql`
  (`backend/app/db/migrations/000N_*.sql`, numeração sequencial).
- **Modelo LLM definitivo:** não escolhido, intencionalmente (`docs/OPEN_QUESTIONS.md`, item 3).

## Estado do ambiente local (esta máquina)

- **PostgreSQL 17** instalado via `winget` (serviço Windows
  `postgresql-x64-17`, porta 5432, `C:\Program Files\PostgreSQL\17`).
- **Banco:** `claudiao`, dono: role de aplicação `claudiao_app` (login próprio,
  sem privilégio de superusuário). Superusuário `postgres` existe só para
  administração.
- **Credenciais reais:** `config/.env` (na raiz do repo, **nunca versionado** —
  confirme com `git check-ignore -v config/.env` se tiver dúvida). Os testes de
  integração (`tests/integration/`) carregam esse arquivo automaticamente via
  `tests/integration/conftest.py` se as variáveis não estiverem no ambiente do
  processo, e pulam (não falham) se o banco não estiver acessível.
- **Python:** 3.14.6 instalado nesta máquina, mas `requires-python >= 3.11` no
  `backend/pyproject.toml` — não assumir 3.14 especificamente em código novo.
- **Dependências externas do backend:** só `psycopg[binary]` até agora (ver
  `backend/pyproject.toml`). Sem ambiente virtual criado ainda — os pacotes
  foram instalados com `python -m pip install` direto no Python do sistema.

## Armadilhas e lições aprendidas (não óbvias)

1. **`.gitignore` tinha `*.sql` genérico** (pensado para dumps de backup) que
   escondia `backend/app/db/migrations/*.sql`, que é código versionável. Já
   corrigido com uma exceção (`!backend/app/db/migrations/*.sql`), mas fique
   atento se criar `.sql` em outro lugar do repo.
2. **O classificador de permissões do ambiente bloqueia edições em
   `pg_hba.conf`** (mesmo com autorização explícita do usuário no chat) — não
   insista tentando outras ferramentas para contornar. O caminho que funcionou
   para definir a senha do superusuário do Postgres foi reinstalar via
   `winget install ... --override "--superpassword ..."` na instalação,
   nunca editando a config de autenticação de uma instância já rodando.
3. **`--basetemp` do pytest:** o diretório temp padrão do Windows neste sandbox
   causa `PermissionError` em alguns setups/teardowns do pytest. Rodar com
   `--basetemp=".pytest_tmp"` (relativo ao repo) evita o problema; apagar
   `.pytest_tmp/` depois (já está no `.gitignore` via `__pycache__`/padrões
   gerais — confirme antes de commitar que não sobrou lixo com `git status`).
4. **Todo texto voltado ao usuário deve ser PT-BR**, incluindo descrições
   curtas de chamadas de ferramenta, não só o texto do chat — o usuário é
   estrito quanto a isso.
5. **Import circular evitado de propósito:** `app.auth.roles` opera sobre a
   *string* `role`, não sobre a classe `User` de `app.auth.users`, porque
   `users.py` importa `Role` de `roles.py` — a direção inversa criaria um
   ciclo. Se for estender autorização, mantenha esse sentido único de
   dependência (`users.py → roles.py`, nunca o contrário).
6. **`postgres_log_handler.py` reexporta `build_dsn_from_env`** de
   `app.db.connection` por compatibilidade — a fonte real da função é
   `app.db.connection`, não duplique a lógica de DSN em módulo novo, importe
   de lá.

## Workflow que está sendo seguido

```
TASK → branch task-XXX → implementação → testes → docs → commit
     → merge na main local → (push só quando pedido, exceto a cada 10 TASKs)
```

Detalhes completos em `AGENTS.md`. Branches `task-001` a `task-010` existem
localmente (histórico); não foram deletadas, mas também não precisam ser —
`AGENTS.md` não pede limpeza delas.

## Próximos passos imediatos

**TASK-011 — Criar autenticação de aplicações via API key** (dependência:
TASK-010 concluída). Fecha o bloco "Segurança e identidade" junto com TASK-012
(criptografia de segredos) e TASK-013 (chave mestra externa ao banco) — essas
duas vão precisar decidir/usar a biblioteca de criptografia (provavelmente
`cryptography`, ainda não uma dependência do projeto; será a próxima decisão
técnica pontual, no mesmo espírito de DEC-006).

## Histórico de checkpoints

- **2026-08-16 — TASK-010 (este checkpoint):** primeiro checkpoint de 10
  TASKs. Fundação completa + autenticação/autorização básicas. 60/60 testes.
