# TASK-053 — Implementar Knowledge Tool

Status: **Concluída em 2026-08-18**

## Objetivo

Implementar Knowledge Tool, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Conhecimento") e `docs/KNOWLEDGE.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Conhecimento" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/KNOWLEDGE.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-052 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/KNOWLEDGE.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de conhecimento (modelo RAW/PROVISIONAL/CONFIRMED, versionamento, escopo, evidências ou promoção, conforme o caso), conforme docs/TESTING.md.

## Documentação afetada

`docs/KNOWLEDGE.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-18. Criado `backend/app/tools/knowledge_tool.py`:
`execute_knowledge_tool(step)`, assinatura compatível com
`ExecutionOrchestrator.tool_executor` (`Callable[[ModelStep], str]`,
TASK-026), mesmo padrão de `app.tools.memory_tool` (TASK-046).
`step.parameters["operation"]` (`"SAVE"`/`"GET"`/`"ADVANCE"`) decide a
chamada a `save_knowledge`/`get_knowledge`/`advance_knowledge_status`
(TASK-052). `ADVANCE` só aplica a transição mecânica já validada —
decidir *quando* promover é a regra de promoção, TASK-057, não
implementada aqui. Cadastro no Tool Registry é TASK-088 em diante.

11 testes novos (7 unitários de validação de parâmetros + 4 de integração
real). Suíte completa: 402/402 testes aprovados.
