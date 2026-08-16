# TASK-002 — Criar configuração central

Status: **Concluída em 2026-08-16**

## Objetivo

Criar um arquivo central de configuração, inicialmente apenas com valores básicos e
placeholders, conforme a seção "Ponto de partida manual" da especificação mestre
(`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`) e `docs/ARCHITECTURE.md`.

## Escopo

Definir onde e como a configuração central do agente vive (arquivo/variáveis de
ambiente), com placeholders para os parâmetros já previstos na especificação (ex.:
runtime do modelo, janela de contexto, `max_steps`, ciclo de cotas) — sem atribuir
valores definitivos que ainda não foram decididos (ver `docs/OPEN_QUESTIONS.md`).
Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-001 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/ARCHITECTURE.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do componente correspondente (config, schema, logging ou catálogo de erros), conforme docs/TESTING.md. Estrutura pura de diretório (sem lógica) não exige teste automatizado.

## Documentação afetada

`docs/ARCHITECTURE.md`, `docs/tasks/README.md`

## Encerramento

Concluída em 2026-08-16: `config/.env.example` expandido para cobrir todos os
parâmetros de configuração já previstos na especificação mestre (PostgreSQL, chave
mestra, runtime/modelo LLM, log level, janela de contexto, `max_steps`, limite de
memória por escopo, ciclo/limiares de cota, timeout de sessão administrativa, janela
de atualização), todos como placeholders — nenhum valor definitivo atribuído. Seção
"Configuração central" adicionada a `docs/ARCHITECTURE.md` explicando os campos e
remetendo a cada documento/TASK responsável pelo valor final. Formato definitivo e
mecanismo de carregamento continuam dependentes da escolha de stack
(`docs/OPEN_QUESTIONS.md`, item 1), que não foi feita nesta TASK.
