# TASK-009 — Criar autenticação de usuários

Status: Pendente

## Objetivo

Criar autenticação de usuários, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Segurança e identidade") e `docs/AUTHENTICATION.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Segurança e identidade" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/AUTHENTICATION.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-008 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/AUTHENTICATION.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de autenticação/autorização (criação de usuário, papéis, validação de API key, criptografia/descriptografia de segredo), conforme docs/TESTING.md.

## Documentação afetada

`docs/AUTHENTICATION.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)
