# TASK-087 — Validar primeiro uso com aplicação real

Status: Concluída

## Objetivo

Validar primeiro uso com aplicação real, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Marco utilizável inicial") e `docs/V1_SCOPE.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Marco utilizável inicial" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/V1_SCOPE.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-086 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/V1_SCOPE.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Cenário real fixo cobrindo o fluxo ponta a ponta envolvido; ver detalhamento específico abaixo.

## Documentação afetada

`docs/V1_SCOPE.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)


## Marco

Esta TASK é o **marco oficial do primeiro Claudião utilizável em produção controlada** (seção 47 da especificação mestre — ver docs/V1_SCOPE.md). Sua conclusão certifica que todos os itens do mínimo utilizável (TASK-001 a TASK-086) estão implementados, testados e validados com uma aplicação real — não apenas o objetivo pontual desta TASK isoladamente.

## Encerramento

**Decisão prévia (via `AskUserQuestion`):** validar o marco exigia uma
resposta real de modelo, e nenhum modelo Ollama havia sido baixado
ainda (`docs/OPEN_QUESTIONS.md`, item 3). Perguntado ao usuário se
certificava o marco sem modelo real ou baixava um agora — escolhida a
segunda opção. Perguntado qual modelo baixar — o usuário escolheu
explicitamente `qwen3:8b` (5.2GB), maior que as opções de referência
sugeridas. Registrado como `DEC-011` (`docs/DECISION_LOG.md`).
`ollama pull qwen3:8b` executado; `CLAUDIAO_ACTIVE_MODEL=qwen3:8b`
adicionado a `config/.env` (não versionado).

**Validação real de ponta a ponta, sem fakes:**

1. Servidor real (`uvicorn app.api.app:app`, porta 8000).
2. `GET /health` (TASK-085) → `healthy: true` pela primeira vez com
   todos os checks reais (modelo/runtime, PostgreSQL, fila,
   configurações críticas) — `ferramentas/providers` continua `SKIPPED`
   por não existir nada ainda (TASK-088+).
3. Aplicação de teste criada via `scripts/chat.py create-application`
   (TASK-084) — API key real emitida.
4. Mensagem enviada via `scripts/chat.py chat` (TASK-084).
   Primeira tentativa com `--timeout 60` retornou
   `[erro 4009] Execução cancelada por timeout da aplicação` (HTTP
   504) — o mecanismo de timeout real (TASK-070) funcionando
   corretamente contra um modelo real lento (`qwen3:8b` em CPU), não
   um defeito. Segunda tentativa com `--timeout 240` completou de
   verdade em ~51.6s.
5. Resultado conferido diretamente no PostgreSQL (`psql`) e via `curl`:
   `usage_records` tem os dois registros (CANCELLED da tentativa 1,
   COMPLETED da tentativa 2), `execution_traces` tem o registro da
   execução bem-sucedida com `step_count`/`tools_used`/duração
   corretos, e `GET /panel` mostra a execução na seção "Execuções"
   junto com o consumo correspondente — prova que a fiação entre API,
   orquestrador, consumo, Execution Trace e painel funciona de ponta a
   ponta com dado real, não só nos testes automatizados. Dado de teste
   limpo do banco depois da validação manual.

**Cenário fixo de regressão criado** (reproduz a validação sem
intervenção manual):
`tests/scenarios/test_minimum_usable_scenario.py::test_scenario_real_model_completes_a_real_objective`
— usa `OllamaProvider` real (sem `app.dependency_overrides`) contra
`CLAUDIAO_ACTIVE_MODEL`; pula automaticamente se a variável não estiver
configurada (mantém o repositório portátil para quem clonar sem modelo
baixado) ou se o Ollama local estiver indisponível.

**Bug real encontrado e corrigido** (não fazia parte do escopo original
da TASK, mas bloqueava a suíte de rodar 100% verde na condição
realista de validação — `config/.env` carregado no processo antes do
`pytest`, algo que nunca tinha sido feito antes desta TASK):
`backend/app/observability/logging_config.py` usa uma flag de módulo
(`_configured`) setada na primeira chamada de `get_logger()` em
qualquer lugar do código — inclusive durante a *coleta* de testes pelo
pytest (ex.: ao importar `health_check.py`). Em execuções normais da
suíte, as variáveis `CLAUDIAO_POSTGRES_*` só existem depois, via
fixture `postgres_dsn` (por teste), então `attach_postgres_handler`
sempre falhava silenciosamente nesse ponto — mas com `config/.env`
carregado no ambiente do processo *antes* do pytest, o handler do
PostgreSQL passa a ser anexado de verdade ao logger raiz `claudiao`
logo na coleta, e fica assim para o resto da execução. Isso quebrou 3
testes que implicitamente assumiam "só existe 1 handler" ou que um
handler manualmente anexado a um logger de teste não teria entrega
duplicada via propagação ao logger raiz agora também populado:
- `tests/unit/test_observability_logging.py::test_handler_is_rotating_with_expected_limits`
  e `::test_configure_logging_is_idempotent_without_force` — corrigidos
  fazendo a fixture `_reset_logging_state` limpar explicitamente as 5
  variáveis `CLAUDIAO_POSTGRES_*` via `monkeypatch.delenv`, tornando o
  comportamento determinístico (1 handler, sempre) independente do
  ambiente de quem invoca o `pytest`.
- `tests/integration/test_postgres_log_handler_integration.py` — os
  dois testes que anexam `PostgresLogHandler` a um logger próprio
  (`claudiao.test.integration`/`claudiao.test.integration.list`) agora
  setam `logger.propagate = False` explicitamente, evitando entrega
  duplicada ao handler do logger raiz `claudiao` (que pode estar ativo
  ou não, dependendo do ambiente).
Não foi alterado `logging_config.py` em si — o comportamento de
"primeira chamada de `get_logger()` decide o estado para o processo
inteiro" é uma característica conhecida (já documentada como lacuna
pré-existente na TASK-085), só os testes que assumiam incorretamente
que essa condição nunca ocorreria foram corrigidos para não depender
disso.

**Testes:** suíte completa aprovada em dois modos —
735/735 com `config/.env` carregado (0 pulados, inclui o cenário com
modelo real) e 734 aprovados + 1 pulado sem o `.env` carregado
(comportamento portátil esperado, sem `CLAUDIAO_ACTIVE_MODEL`).

**Documentação atualizada:** `docs/DECISION_LOG.md` (DEC-011),
`docs/OPEN_QUESTIONS.md` (item 3), `docs/V1_SCOPE.md` (marco
certificado), `docs/tasks/README.md`, `README.md` raiz.

**Marco certificado:** a partir desta TASK, o Claudião é considerado
**utilizável em produção controlada** (`docs/V1_SCOPE.md`).
