# TASK-046 — Implementar Memory Tool

Status: **Concluída em 2026-08-18**

## Objetivo

Implementar Memory Tool, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Memória") e `docs/MEMORY.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Memória" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/MEMORY.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-045 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/MEMORY.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de memória (persistência, busca, relevância, retenção ou auditoria de remoção, conforme o caso); teste de integração com o banco quando a TASK persistir dados, conforme docs/TESTING.md.

## Documentação afetada

`docs/MEMORY.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-18. Criado `backend/app/tools/memory_tool.py`:
`execute_memory_tool(step)`, assinatura compatível com
`ExecutionOrchestrator.tool_executor` (`Callable[[ModelStep], str]`,
TASK-026). `step.parameters["operation"]` (`"SAVE"`/`"LIST"`) decide a
chamada a `save_memory`/`list_memories_for_owner` (TASK-044/045).
`MissingToolParameterError`/`UnknownMemoryOperationError` para parâmetro
ausente/operação desconhecida.

Cadastro no Tool Registry (catálogo fixo de ferramentas
conhecidas/autorizadas) é TASK-088 em diante — esta TASK só cria a função
executável. Busca estruturada por relevância (TASK-047) não é desta
TASK — `LIST` devolve todas as memórias do dono, sem filtro de conteúdo.

7 testes unitários (validação de parâmetros, sem tocar o banco) + 3 testes
de integração novos (dispatch real contra o PostgreSQL local). Suíte
completa: 341/341 testes aprovados.
