# TASK-005 — Criar sistema de logging local

Status: **Concluída em 2026-08-16**

## Objetivo

Criar logging local rotativo, antes de avançar para o LLM, conforme a seção "Ponto
de partida manual" da especificação mestre
(`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`) e `docs/OBSERVABILITY.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Fundação" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/OBSERVABILITY.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-004 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/OBSERVABILITY.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do componente correspondente (config, schema, logging ou catálogo de erros), conforme docs/TESTING.md. Estrutura pura de diretório (sem lógica) não exige teste automatizado.

## Documentação afetada

`docs/OBSERVABILITY.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (DEC-005),
`docs/OPEN_QUESTIONS.md` (item 1), `AGENTS.md`,
`backend/app/observability/README.md`

## Encerramento

Concluída em 2026-08-16. Primeira TASK a exigir código de aplicação real, o que
levou à decisão de linguagem (`docs/DECISION_LOG.md`, DEC-005: **Python**,
`backend/pyproject.toml`, `requires-python >= 3.11`). Implementado
`backend/app/observability/logging_config.py`: `configure_logging()` (logger raiz
`claudiao`, nível via `CLAUDIAO_LOG_LEVEL` com `INFO` como padrão e `DEBUG`
desativado por padrão, `RotatingFileHandler` de 10 MB × 5 backups, diretório via
`CLAUDIAO_LOG_DIR` criado automaticamente) e `get_logger(nome)`. `config/.env.example`
ganhou `CLAUDIAO_LOG_DIR`/`CLAUDIAO_LOG_FILE`. 7 testes unitários em
`tests/unit/test_observability_logging.py`, todos aprovados (nível padrão,
`DEBUG` explícito, nível inválido cai no padrão, criação automática de diretório,
configuração da rotação, escrita efetiva no arquivo, idempotência). Logging
estruturado no PostgreSQL fica para a TASK-006.
