# TASK-001 — Inicializar estrutura do projeto Claudião

Status: Pendente

## Objetivo

Criar a pasta/repositório do Claudião e a estrutura mínima de diretórios, conforme a
seção "Ponto de partida manual" da especificação mestre
(`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`) e `docs/DECISION_LOG.md`
(DEC-002, DEC-003).

## Escopo

- Estrutura de diretórios do repositório (backend, frontend, docs, tests, config,
  scripts, adr, rfc), com os módulos internos previstos em `docs/ARCHITECTURE.md`.
- Controle de versão: inicializar Git no repositório, com `.gitignore` cobrindo
  segredos, backups, logs e artefatos de build (ver `.gitignore` na raiz).
- Primeiro commit registrando a organização inicial (estrutura + documentação
  criadas nesta fase, conforme `README.md`).
- **Não** inclui escolha de linguagem/stack (ver `docs/OPEN_QUESTIONS.md`, item 1) —
  os diretórios de código ficam agnósticos de linguagem por ora.

## Fora de escopo

Configuração central da aplicação (TASK-002); PostgreSQL (TASK-003/TASK-004);
logging (TASK-005/TASK-006); catálogo de erros (TASK-007/TASK-008); qualquer decisão
de stack de implementação; qualquer item listado em `docs/OUT_OF_SCOPE.md`.

## Dependências

Nenhuma — primeira TASK do projeto.

## Critérios de aceite

- Estrutura de diretórios criada e correspondente ao descrito em `docs/ARCHITECTURE.md`
  (seção "Estrutura de diretórios" do `README.md`).
- `.gitignore` presente e cobrindo segredos/backups/logs.
- Repositório Git inicializado (`git init`), com o primeiro commit da organização
  registrado.
- `docs/tasks/README.md` refletindo o estado real desta TASK.

## Testes esperados

Nenhum teste automatizado aplicável — esta TASK é puramente estrutural (diretórios,
Git). Validação é manual: conferir a árvore de diretórios contra
`docs/ARCHITECTURE.md` e confirmar que `git status`/`git log` mostram o repositório
inicializado com o commit esperado.

## Documentação afetada

`README.md`, `docs/ARCHITECTURE.md`, `docs/DECISION_LOG.md` (DEC-002/DEC-003),
`docs/tasks/README.md`.
