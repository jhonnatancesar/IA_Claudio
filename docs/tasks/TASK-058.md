# TASK-058 — Implementar avaliação de utilidade pelo orquestrador

Status: **Concluída em 2026-08-19**

## Objetivo

Implementar avaliação de utilidade pelo orquestrador, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Conhecimento") e `docs/KNOWLEDGE.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Conhecimento" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/KNOWLEDGE.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-057 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/KNOWLEDGE.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de conhecimento (modelo RAW/PROVISIONAL/CONFIRMED, versionamento, escopo, evidências ou promoção, conforme o caso), conforme docs/TESTING.md.

## Documentação afetada

`docs/KNOWLEDGE.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-19. Criado `backend/app/knowledge/usefulness.py`:
`is_useful_for_orchestrator(knowledge, is_relevant_to_objective)` (função
pura) — a etapa "AVALIO UTILIDADE" do fluxo (seção 12): exige status
`CONFIRMED` e `is_relevant_to_objective`. Relevância para o objetivo da
execução atual é contextual (depende do pedido do usuário/aplicação) e
não pode ser derivada só do `Knowledge` — recebida já avaliada por quem
chama, mesmo padrão de `app.confidence.ambiguity_guardrail` (TASK-036).

É uma avaliação do orquestrador, não uma ferramenta acionada pelo modelo
— ao contrário de `promotion_rule.py` (TASK-057), não é exposta em
`app.tools.knowledge_tool`. Onde o orquestrador de fato chama isso antes
de "SALVO" é TASK-088 em diante, não implementado aqui.

Com esta TASK, o bloco "Conhecimento" (TASK-052 a TASK-058) está
completo.

5 testes unitários novos (função pura). Suíte completa: 471/471 testes
aprovados (mais 4 pulados por indisponibilidade do Ollama local no
momento — ambiental, não relacionado a esta TASK).
