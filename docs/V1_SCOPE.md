# Escopo da V1

Fonte: seções 46 a 48 da especificação mestre.

## Critério de liberação

A V1 não precisa estar 100% concluída para o Claudião começar a ser usado. Existem
dois marcos:

- **Mínimo utilizável seguro** — já pode começar a ser usado quando os itens críticos
  abaixo estiverem aprovados. Marco oficial: **TASK-087**.
- **V1 completa** — todos os itens planejados da V1 concluídos. Marco oficial:
  **TASK-147**.

## Primeiro marco utilizável (TASK-087)

A prioridade inicial é **aplicações primeiro** — o chat web completo vem depois.

Itens que compõem o mínimo utilizável:

- modelo local
- Ollama
- `LocalLLMProvider`
- orquestrador
- PostgreSQL
- autenticação
- API local
- API key para aplicações
- execução síncrona
- JSON interno
- memória
- conhecimento
- guardrails
- confiança
- logs básicos
- `execution_id`
- fila FIFO
- chat simples de terminal para teste
- painel web somente leitura
- health check inicial
- testes críticos
- validação com aplicação real

A partir da TASK-087, o Claudião é considerado **utilizável em produção controlada**.

**Marco certificado (TASK-087):** todos os itens acima estão
implementados, testados e foram validados de ponta a ponta contra
serviços reais (PostgreSQL local, Ollama local com modelo `qwen3:8b`
baixado — `docs/DECISION_LOG.md`, DEC-011), não só contra fakes/mocks:
servidor real (`uvicorn app.api.app:app`) → `GET /health` reportando
`healthy: true` de verdade → aplicação de teste criada via
`scripts/chat.py create-application` → mensagem real enviada via
`scripts/chat.py chat` → execução completa com resposta real do modelo
(~52s, dentro do timeout de aplicação, TASK-070) → resultado conferido
em `usage_records` (consumo), `execution_traces` (execuções) e `GET
/panel` (painel), todos consistentes entre si. O caminho de rejeição
(timeout real de aplicação, `APPLICATION_TIMEOUT_EXCEEDED`/4009) também
foi exercitado de verdade numa tentativa inicial com timeout curto
demais para o modelo, confirmando que o mecanismo de timeout (TASK-070)
funciona contra um modelo real lento, não só contra fakes rápidos nos
testes. Cenário fixo de regressão que reproduz essa validação (sem
depender de execução manual):
`tests/scenarios/test_minimum_usable_scenario.py::test_scenario_real_model_completes_a_real_objective`
— pula automaticamente se `CLAUDIAO_ACTIVE_MODEL` não estiver
configurado, para continuar portátil em quem clonar o repositório sem
modelo baixado. Suíte completa: 735/735 testes aprovados (0 pulados)
quando `config/.env` está carregado no processo do `pytest`.

**Implementação (TASK-084):** `scripts/chat.py` — "chat simples de
terminal para teste". Cliente HTTP puro de `POST /v1/executions`
(biblioteca padrão, `urllib.request`, sem dependência nova) — não é uma
via de entrada privilegiada, usa a API exatamente como qualquer
aplicação externa (mesma autenticação/validação/timeout já
implementados, TASK-067 a TASK-073). Dois subcomandos: `create-application
<nome>` (cria uma aplicação de teste via `app.auth.api_keys.
create_application`, TASK-011, e imprime a API key uma única vez — o
banco só guarda o hash) e `chat --api-key ...` (laço interativo contra
um servidor já rodando, `uvicorn app.api.app:app`, porta padrão 8000 —
o script não sobe seu próprio servidor). Verificado manualmente contra
um servidor real: autenticação e validação funcionam ponta a ponta;
sem `CLAUDIAO_ACTIVE_MODEL` configurado nesta máquina, toda mensagem
retorna o erro `3001` do catálogo — comportamento esperado, não um
defeito do CLI.

## V1 completa (TASK-147)

Itens que fecham a V1 completa, além do mínimo utilizável:

- `WebSearchProvider`
- leitura de páginas
- validação e reputação de fontes
- blacklist
- API Tool
- File Tool
- Database Tool
- chat web
- streaming
- histórico e resumo de conversas
- cotas
- painel administrativo completo
- backup/restore
- modo manutenção
- atualização via Git
- rollback
- métricas
- suíte completa de testes

## Correspondência com as TASKs

Ver `docs/ROADMAP.md` para o mapeamento de fases e `docs/BACKLOG.md` para a lista de
TASKs por bloco funcional. Em resumo: TASK-001 a TASK-087 cobrem o mínimo utilizável;
TASK-088 a TASK-147 completam a V1.
