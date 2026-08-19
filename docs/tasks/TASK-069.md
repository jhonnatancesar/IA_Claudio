# TASK-069 — Implementar execução síncrona

Status: **Concluída em 2026-08-19**

## Objetivo

Implementar execução síncrona, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Aplicações") e `docs/API.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Aplicações" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/API.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-068 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/API.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários e de integração da API para aplicações (payload válido/inválido, timeout, execution_id, resposta final), conforme docs/TESTING.md.

## Documentação afetada

`docs/API.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-19. `POST /v1/executions` agora executa de fato, de
forma síncrona: monta `ExecutionPolicy.for_application` (TASK-022) a
partir do payload já validado e roda
`ExecutionOrchestrator.run_until_response` (TASK-023/026) até uma
resposta final, na mesma resposta HTTP. Criado
`backend/app/api/dependencies.py`: `get_local_llm_provider`/
`get_active_model` como dependências do FastAPI (substituíveis por fakes
em teste); `get_active_model` lê `CLAUDIAO_ACTIVE_MODEL`
(`config/.env.example`, já previsto desde a TASK-002) e levanta
`ClaudiaoError` (`NO_ACTIVE_MODEL_CONFIGURED`, código `3001`) se
ausente. `LocalLLMProviderError`/`ToolExecutorNotConfiguredError` (falhas
de runtime que não são `ClaudiaoError`) convertidas para erros com
código próprio (`3002`/`3003`) em vez de vazar como 500 não tratado.
Também corrigida uma lacuna na TASK-067: o código `2002` nunca tinha sido
adicionado à tabela de `docs/ERROR_CATALOG.md`.

`timeout_seconds` é guardado na política mas ainda não aplicado como
limite de fato (TASK-070); estourar/reportar esse limite é TASK-071. O
envelope de sucesso é o mínimo por ora — o contrato formal (`"success":
true`) e rastreio de consumo são TASK-072/TASK-073.

4 testes novos (2 unitários de `get_active_model`, sem tocar rede/banco +
2 de integração real), além de atualizar os 7 testes de integração já
existentes para usar `LocalLLMProvider` fake via
`app.dependency_overrides`, já que nenhum modelo Ollama real foi baixado.
Suíte completa: 560/560 testes aprovados.
