# Claudião

Agente inteligente **local, genérico e reutilizável**, cujo raciocínio principal roda no
próprio servidor, sem depender de OpenAI, Gemini, Claude, Groq, OpenRouter ou qualquer
outra IA externa para pensar normalmente. Internet, APIs, outros agentes e integrações
são **ferramentas** — nunca fallback de inteligência.

> Projeto **novo e separado** do AIShoppingAgent. Não reutiliza código, regras de
> negócio, pipeline de preços, Telegram, Firecrawl, lojas ou qualquer TASK funcional
> daquele sistema. O AIShoppingAgent serve apenas como referência de **organização de
> repositório, documentação e rastreabilidade** — não de domínio.

## Status atual

Repositório em **fase de organização** (estrutura, documentação e planejamento de
TASKs). Nenhuma funcionalidade do agente foi implementada ainda. Consulte
[docs/tasks/README.md](docs/tasks/README.md) para o estado exato de cada TASK.

## Fonte de verdade

- **Escopo, arquitetura e decisões já aprovadas**: `Claudiao_Especificacao_Arquitetura_e_TASKs.docx`
  (documento mestre fornecido pelo usuário) e os documentos em [docs/](docs/) que o
  decompõem por assunto.
- **Decisões novas, tomadas depois da especificação mestre**: [docs/DECISION_LOG.md](docs/DECISION_LOG.md).
- **Dúvidas/contradições encontradas na especificação, ainda não resolvidas pelo
  usuário**: [docs/OPEN_QUESTIONS.md](docs/OPEN_QUESTIONS.md).
- **Trabalho a ser feito, unidade por unidade**: [docs/tasks/](docs/tasks/) (TASK-001 a
  TASK-147).

Documentação e decisões aprovadas não são reescritas silenciosamente. Mudanças de
escopo entram como nova entrada em `DECISION_LOG.md`, nunca como edição retroativa do
que já foi decidido.

## Princípios fundamentais

1. **Offline-first** — conversar, raciocinar, interpretar intenção, manter contexto,
   consultar memória/conhecimento local e planejar não dependem de internet.
2. **Inteligência local** — linguagem natural, interpretação, raciocínio, planejamento,
   replanejamento e geração de resposta rodam no modelo local.
3. **Orquestração controlada** — o modelo não controla o sistema livremente; um
   orquestrador determinístico controla execução, políticas, limites, cotas,
   ferramentas, segurança, validação, confiança, persistência, cancelamento e erros.

Detalhes completos em [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Mapa da documentação

| Documento | Assunto |
|---|---|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Arquitetura de alto nível, runtime/modelo local, protocolo interno, hierarquia de prioridade |
| [docs/VISION.md](docs/VISION.md) | Visão geral do produto e objetivo formal |
| [docs/V1_SCOPE.md](docs/V1_SCOPE.md) | Escopo da V1, mínimo utilizável (TASK-087) e V1 completa (TASK-147) |
| [docs/OUT_OF_SCOPE.md](docs/OUT_OF_SCOPE.md) | O que fica fora da V1 (candidato a V2) |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Fases (0–10) e marcos |
| [docs/BACKLOG.md](docs/BACKLOG.md) | TASKs agrupadas por bloco funcional |
| [docs/DECISION_LOG.md](docs/DECISION_LOG.md) | Histórico de decisões (append-only) |
| [docs/OPEN_QUESTIONS.md](docs/OPEN_QUESTIONS.md) | Pontos ambíguos/pendentes da especificação |
| [docs/ORCHESTRATOR.md](docs/ORCHESTRATOR.md) | Orquestrador, contexto de conversa, limites de execução |
| [docs/MEMORY.md](docs/MEMORY.md) | Memória persistente e contexto imediato |
| [docs/KNOWLEDGE.md](docs/KNOWLEDGE.md) | Conhecimento RAW/PROVISIONAL/CONFIRMED |
| [docs/TRUST_GUARDRAILS.md](docs/TRUST_GUARDRAILS.md) | Confiança, volatilidade, fontes, reputação, blacklist |
| [docs/TOOLS.md](docs/TOOLS.md) | Ferramentas da V1 (Memory, Knowledge, Web Search, File, Database, API) |
| [docs/API.md](docs/API.md) | API para aplicações externas |
| [docs/AUTHENTICATION.md](docs/AUTHENTICATION.md) | Autenticação humana, perfis, API keys de aplicações |
| [docs/SECURITY.md](docs/SECURITY.md) | Segredos, criptografia, HTTPS/HTTP, contratos de ferramenta |
| [docs/QUEUE.md](docs/QUEUE.md) | Fila FIFO persistida |
| [docs/OBSERVABILITY.md](docs/OBSERVABILITY.md) | Logs, Execution Trace, métricas |
| [docs/QUOTAS.md](docs/QUOTAS.md) | Cotas e limitação do chat |
| [docs/PANEL.md](docs/PANEL.md) | Painel read-only e painel administrativo completo |
| [docs/OPERATIONS.md](docs/OPERATIONS.md) | Modo de manutenção, health check, reinício |
| [docs/BACKUP_RESTORE.md](docs/BACKUP_RESTORE.md) | Backup, restore, rollback |
| [docs/UPDATER.md](docs/UPDATER.md) | Atualização via Git, janela noturna, rollback automático |
| [docs/DATABASE.md](docs/DATABASE.md) | PostgreSQL local, domínios de dados |
| [docs/ERROR_CATALOG.md](docs/ERROR_CATALOG.md) | Faixas de código de erro e formato JSON padrão |
| [docs/TESTING.md](docs/TESTING.md) | Tipos de teste obrigatórios na V1 |
| [docs/tasks/](docs/tasks/) | TASK-001 a TASK-147, uma por arquivo |

## Fluxo de trabalho

```
TASK → Implementação → Validação/Testes → Atualização documental → Commit → Push
```

Cada TASK só é considerada concluída quando seus critérios de aceite (descritos no
próprio arquivo `docs/tasks/TASK-XXX.md`) forem realmente satisfeitos — não apenas
quando um documento de planejamento é criado.

## Marcos

- **TASK-087** — primeiro Claudião **utilizável em produção controlada** (mínimo
  utilizável seguro: modelo local, orquestrador, PostgreSQL, autenticação, API para
  aplicações, memória, conhecimento, guardrails, confiança, fila, chat de terminal,
  painel read-only, health check inicial, testes críticos).
- **TASK-147** — **V1 completa** (todos os itens planejados da V1 concluídos).

## Estrutura de diretórios

```
backend/app/    núcleo do agente (orquestrador, providers de LLM, tools, memória,
                conhecimento, API, autenticação, fila, observabilidade, cotas,
                painel, backup, updater, persistência) — ver README.md em cada módulo
frontend/       painel web / chat web (V1, fases posteriores ao marco TASK-087)
docs/           documentação e TASKs
adr/            decisões arquiteturais que exigem justificativa própria (quando fizer
                sentido — ver docs/DECISION_LOG.md)
rfc/            propostas técnicas discutidas antes de virar decisão
tests/          unit/, integration/, scenarios/
scripts/        scripts operacionais (setup, migrations, checks)
config/         configuração central e exemplos de variáveis de ambiente
```

## Próxima TASK executável

**TASK-001 — Inicializar estrutura do projeto Claudião**
(ver [docs/tasks/TASK-001.md](docs/tasks/TASK-001.md)).
