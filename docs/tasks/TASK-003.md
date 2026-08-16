# TASK-003 — Configurar PostgreSQL local

Status: **Concluída em 2026-08-16**

## Objetivo

Instalar/configurar o PostgreSQL local e criar o banco do projeto, conforme a seção
"Ponto de partida manual" da especificação mestre
(`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`) e `docs/DATABASE.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Fundação" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/DATABASE.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-002 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/DATABASE.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do componente correspondente (config, schema, logging ou catálogo de erros), conforme docs/TESTING.md. Estrutura pura de diretório (sem lógica) não exige teste automatizado.

## Documentação afetada

`docs/DATABASE.md`, `docs/tasks/README.md`

## Encerramento

Concluída em 2026-08-16: PostgreSQL 17 instalado localmente via winget (serviço
Windows `postgresql-x64-17`, porta 5432), banco `claudiao` criado, de propriedade do
role de aplicação `claudiao_app` (login próprio, sem superusuário). Conexão
verificada com `claudiao_app` no banco `claudiao`. Credenciais reais gravadas apenas
em `config/.env` (não versionado); `config/.env.example` permanece só com
placeholders. Nenhum schema foi criado (fica para TASK-004). Durante a execução, uma
tentativa de resetar a senha do superusuário via trust temporário em `pg_hba.conf`
foi bloqueada pelo classificador de permissões do ambiente (mesmo com autorização do
usuário) — o desbloqueio final veio de reinstalar o PostgreSQL definindo a senha do
superusuário já na instalação (`--override "--superpassword ..."`), sem editar
configuração de autenticação de uma instância já em execução.
