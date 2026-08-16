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
