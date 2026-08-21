# TASK-084 — Criar CLI/chat de teste

Status: **Concluída em 2026-08-21**

## Objetivo

Criar CLI/chat de teste, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "Marco utilizável inicial") e `docs/V1_SCOPE.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "Marco utilizável inicial" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/V1_SCOPE.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-083 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/V1_SCOPE.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Cenário real fixo cobrindo o fluxo ponta a ponta envolvido; ver detalhamento específico abaixo.

## Documentação afetada

`docs/V1_SCOPE.md`, `docs/tasks/README.md`, `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)

## Encerramento

Concluída em 2026-08-21. Novo `scripts/chat.py` — "chat simples de
terminal para teste" (`docs/V1_SCOPE.md`, mínimo utilizável). Cliente
HTTP puro de `POST /v1/executions` via `urllib.request` (biblioteca
padrão, sem dependência nova) — não é uma via de entrada privilegiada:
usa a API exatamente como qualquer aplicação externa usaria, sujeito à
mesma autenticação/validação/timeout já implementados (TASK-067 a
TASK-073). Dois subcomandos: `create-application <nome>` (cria uma
aplicação de teste via `app.auth.api_keys.create_application`,
TASK-011, e imprime a API key uma única vez — o banco só guarda o
hash, não dá para recuperar depois) e `chat --api-key ...` (laço
interativo contra um servidor já rodando, `uvicorn app.api.app:app`,
porta padrão 8000 — o script deliberadamente não sobe seu próprio
servidor, para testar o caminho HTTP real de ponta a ponta).

Verificado manualmente contra um servidor `uvicorn` real: `create-application`
criou uma aplicação e API key reais; uma mensagem enviada via `chat`
percorreu autenticação e validação reais, chegando ao erro `3001`
(`NO_ACTIVE_MODEL_CONFIGURED`) — comportamento esperado nesta máquina,
já que `CLAUDIAO_ACTIVE_MODEL` não está configurado e nenhum modelo
Ollama foi baixado (`docs/OPEN_QUESTIONS.md`, item 3); prova que o
caminho ponta a ponta (rede → autenticação → validação → orquestrador)
funciona de verdade, sem precisar de um modelo completando de fato.

11 testes novos: 9 unitários em `tests/unit/test_chat_cli.py`
(`build_execution_payload`/`format_response` isolados, `run_chat_loop`
com entrada/saída/chamada HTTP injetadas — sem terminal/rede reais) e 2
de integração em `tests/integration/test_chat_cli_integration.py` (o
payload que o CLI monta enviado de verdade para `POST /v1/executions`
via `TestClient`, com provider fake — cenário real fixo ponta a ponta,
sucesso e erro de autenticação). Suíte completa: 718/718 testes
aprovados, zero pulados (Ollama verificado rodando antes da execução).
