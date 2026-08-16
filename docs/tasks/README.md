# TASKs

Cada arquivo `TASK-XXX.md` descreve uma unidade de trabalho: objetivo, escopo, fora
de escopo, dependências, critérios de aceite, testes esperados, documentação afetada
e status. Antes de executar uma TASK, leia os documentos obrigatórios definidos em
`AGENTS.md`.

A numeração e a ordem (TASK-001 a TASK-147) vêm da seção 51 da especificação mestre
(`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`) e não devem ser alteradas sem
antes apresentar uma auditoria e uma justificativa ao usuário.

Ver `docs/BACKLOG.md` para a lista agrupada por bloco funcional e `docs/ROADMAP.md`
para as fases e marcos.

## Marcos

- **TASK-087** — primeiro Claudião utilizável em produção controlada (mínimo
  utilizável seguro).
- **TASK-147** — V1 completa.

## Estado atual

Todas as 147 TASKs foram cadastradas nesta organização inicial. **TASK-001** está
**concluída** (estrutura de diretórios, `.gitignore`, `git init` e primeiro commit —
ver `docs/tasks/TASK-001.md` e `docs/DECISION_LOG.md`, DEC-003). As demais 146 TASKs
permanecem com status **Pendente**; nenhuma funcionalidade do agente foi
implementada.

Próxima TASK executável: **TASK-002 — Criar configuração central**.

Este documento é atualizado a cada TASK concluída (etapa "Encerramento" do workflow
em `AGENTS.md`), registrando data de conclusão e um resumo curto — no mesmo espírito
de rastreabilidade do AIShoppingAgent, mas sem copiar conteúdo daquele projeto.
