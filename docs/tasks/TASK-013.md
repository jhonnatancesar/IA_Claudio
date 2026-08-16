# TASK-013 — Implementar chave mestra externa ao banco

Status: **Concluída em 2026-08-16**

## Objetivo

Implementar chave mestra externa ao banco, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Segurança e identidade") e `docs/SECURITY.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Segurança e identidade" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/SECURITY.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-012 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/SECURITY.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários de autenticação/autorização (criação de usuário, papéis, validação de API key, criptografia/descriptografia de segredo), conforme docs/TESTING.md.

## Documentação afetada

`docs/SECURITY.md`, `docs/tasks/README.md`, `backend/app/auth/README.md`

## Encerramento

Concluída em 2026-08-16. Criado `backend/app/auth/master_key.py`:
`load_or_create_master_key(path=None)` — carrega a chave de um arquivo local
fora do PostgreSQL (nunca versionado); gera uma chave nova
(`app.auth.crypto.generate_key()`) se o arquivo não existir, e a persiste.
Caminho vem de `CLAUDIAO_MASTER_KEY_PATH` quando `path` não é informado;
`MasterKeyPathNotConfiguredError` se nenhum dos dois estiver disponível.
Permissão do arquivo restringida por melhor esforço (`os.chmod`) — no Windows
isso só alcança a flag somente-leitura, não uma ACL real; registrado como
lacuna conhecida em `docs/SECURITY.md`, sem justificar uma dependência nova
(`pywin32`) só para isso nesta TASK. 7 testes unitários novos (cria quando
ausente, reusa quando existe, cria diretórios pai, erro sem configuração,
variável de ambiente, prioridade de `path` explícito, integração com o módulo
de criptografia da TASK-012). Suíte completa: 84/84 testes aprovados.

**Com esta TASK, o bloco "Segurança e identidade" (TASK-009 a TASK-013) está
completo.**
