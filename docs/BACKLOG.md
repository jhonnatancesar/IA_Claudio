# Backlog

Fonte: seção 51 da especificação mestre. Lista completa das TASK-001 a
TASK-147, agrupadas nos mesmos blocos funcionais da especificação e na
mesma ordem. Não renumerar nem reordenar sem antes apresentar auditoria e
justificativa (ver AGENTS.md).

Cada linha aponta para o arquivo individual em `docs/tasks/`, que contém
objetivo, escopo, fora de escopo, dependências, critérios de aceite, testes
esperados, documentação afetada e status.

## Fundação

- [TASK-001](tasks/TASK-001.md) — Inicializar estrutura do projeto Claudião
- [TASK-002](tasks/TASK-002.md) — Criar configuração central
- [TASK-003](tasks/TASK-003.md) — Configurar PostgreSQL local
- [TASK-004](tasks/TASK-004.md) — Criar schema inicial do banco
- [TASK-005](tasks/TASK-005.md) — Criar sistema de logging local
- [TASK-006](tasks/TASK-006.md) — Criar logging estruturado no PostgreSQL
- [TASK-007](tasks/TASK-007.md) — Criar catálogo interno de erros
- [TASK-008](tasks/TASK-008.md) — Implementar resposta padrão de erro JSON

## Segurança e identidade

- [TASK-009](tasks/TASK-009.md) — Criar autenticação de usuários
- [TASK-010](tasks/TASK-010.md) — Criar roles ADMIN e USER
- [TASK-011](tasks/TASK-011.md) — Criar autenticação de aplicações via API key
- [TASK-012](tasks/TASK-012.md) — Implementar criptografia de segredos
- [TASK-013](tasks/TASK-013.md) — Implementar chave mestra externa ao banco

## LLM

- [TASK-014](tasks/TASK-014.md) — Criar interface LocalLLMProvider
- [TASK-015](tasks/TASK-015.md) — Implementar OllamaProvider
- [TASK-016](tasks/TASK-016.md) — Criar protocolo JSON modelo ↔ orquestrador
- [TASK-017](tasks/TASK-017.md) — Criar validação dos JSONs internos
- [TASK-018](tasks/TASK-018.md) — Criar prompt-base do Claudião
- [TASK-019](tasks/TASK-019.md) — Criar composição dinâmica de prompt/contexto

## Orquestração

- [TASK-020](tasks/TASK-020.md) — Criar modelo de Execution
- [TASK-021](tasks/TASK-021.md) — Implementar execution_id
- [TASK-022](tasks/TASK-022.md) — Criar ExecutionPolicy
- [TASK-023](tasks/TASK-023.md) — Criar ExecutionOrchestrator
- [TASK-024](tasks/TASK-024.md) — Implementar planejamento inicial
- [TASK-025](tasks/TASK-025.md) — Implementar validação de plano
- [TASK-026](tasks/TASK-026.md) — Implementar execução por etapas
- [TASK-027](tasks/TASK-027.md) — Implementar replanejamento completo
- [TASK-028](tasks/TASK-028.md) — Implementar max_steps
- [TASK-029](tasks/TASK-029.md) — Implementar detecção de loop
- [TASK-030](tasks/TASK-030.md) — Implementar cancelamento

## Confiança e guardrails

- [TASK-031](tasks/TASK-031.md) — Implementar confiança LOW/MEDIUM/HIGH do modelo
- [TASK-032](tasks/TASK-032.md) — Implementar volatilidade VOLATILE/NON_VOLATILE
- [TASK-033](tasks/TASK-033.md) — Implementar confidence engine do orquestrador
- [TASK-034](tasks/TASK-034.md) — Implementar bloqueio de resposta conclusiva em LOW
- [TASK-035](tasks/TASK-035.md) — Implementar regra obrigatória para informação volátil
- [TASK-036](tasks/TASK-036.md) — Implementar tratamento de ambiguidade

## Contexto

- [TASK-037](tasks/TASK-037.md) — Criar ContextManager
- [TASK-038](tasks/TASK-038.md) — Criar active topic
- [TASK-039](tasks/TASK-039.md) — Criar rastreamento de entidades/referências
- [TASK-040](tasks/TASK-040.md) — Implementar correção de contexto
- [TASK-041](tasks/TASK-041.md) — Implementar detecção de troca de assunto
- [TASK-042](tasks/TASK-042.md) — Implementar monitor de janela de contexto
- [TASK-043](tasks/TASK-043.md) — Implementar aviso em 80%

## Memória

- [TASK-044](tasks/TASK-044.md) — Criar modelo de memória persistente
- [TASK-045](tasks/TASK-045.md) — Separar memória por usuário/aplicação
- [TASK-046](tasks/TASK-046.md) — Implementar Memory Tool
- [TASK-047](tasks/TASK-047.md) — Implementar busca estruturada de memória
- [TASK-048](tasks/TASK-048.md) — Implementar relevância/frequência/last used
- [TASK-049](tasks/TASK-049.md) — Implementar política de retenção
- [TASK-050](tasks/TASK-050.md) — Implementar limite fixo de memória
- [TASK-051](tasks/TASK-051.md) — Implementar auditoria de memória removida

## Conhecimento

- [TASK-052](tasks/TASK-052.md) — Criar modelo RAW/PROVISIONAL/CONFIRMED
- [TASK-053](tasks/TASK-053.md) — Implementar Knowledge Tool
- [TASK-054](tasks/TASK-054.md) — Implementar versionamento de conhecimento
- [TASK-055](tasks/TASK-055.md) — Implementar escopo GLOBAL/APPLICATION
- [TASK-056](tasks/TASK-056.md) — Implementar evidências/fontes
- [TASK-057](tasks/TASK-057.md) — Implementar regra de promoção para CONFIRMED
- [TASK-058](tasks/TASK-058.md) — Implementar avaliação de utilidade pelo orquestrador

## Fontes

- [TASK-059](tasks/TASK-059.md) — Criar cadastro de fontes
- [TASK-060](tasks/TASK-060.md) — Implementar PRIMARY/SECONDARY/UNKNOWN
- [TASK-061](tasks/TASK-061.md) — Implementar reputação LOW/MEDIUM/HIGH
- [TASK-062](tasks/TASK-062.md) — Implementar atualização de reputação
- [TASK-063](tasks/TASK-063.md) — Criar histórico de reputação
- [TASK-064](tasks/TASK-064.md) — Criar blacklist
- [TASK-065](tasks/TASK-065.md) — Implementar bloqueio automático
- [TASK-066](tasks/TASK-066.md) — Implementar desbloqueio somente ADMIN

## Aplicações

- [TASK-067](tasks/TASK-067.md) — Criar API local do Claudião
- [TASK-068](tasks/TASK-068.md) — Criar validação de payload
- [TASK-069](tasks/TASK-069.md) — Implementar execução síncrona
- [TASK-070](tasks/TASK-070.md) — Implementar timeout definido pela aplicação
- [TASK-071](tasks/TASK-071.md) — Implementar erro de timeout
- [TASK-072](tasks/TASK-072.md) — Implementar resposta JSON final
- [TASK-073](tasks/TASK-073.md) — Implementar rastreio de consumo

## Fila

- [TASK-074](tasks/TASK-074.md) — Criar fila FIFO
- [TASK-075](tasks/TASK-075.md) — Persistir fila no PostgreSQL
- [TASK-076](tasks/TASK-076.md) — Criar estados da fila
- [TASK-077](tasks/TASK-077.md) — Implementar retenção/limpeza

## Observabilidade inicial

- [TASK-078](tasks/TASK-078.md) — Criar Execution Trace
- [TASK-079](tasks/TASK-079.md) — Registrar ferramentas/passos/tempos
- [TASK-080](tasks/TASK-080.md) — Criar métricas básicas
- [TASK-081](tasks/TASK-081.md) — Criar painel web read-only
- [TASK-082](tasks/TASK-082.md) — Mostrar execuções no painel
- [TASK-083](tasks/TASK-083.md) — Mostrar erros/logs/consumo

## Marco utilizável inicial

- [TASK-084](tasks/TASK-084.md) — Criar CLI/chat de teste
- [TASK-085](tasks/TASK-085.md) — Criar health check inicial
- [TASK-086](tasks/TASK-086.md) — Criar suíte mínima de testes críticos
- [TASK-087](tasks/TASK-087.md) — Validar primeiro uso com aplicação real — **marco: primeiro Claudião utilizável**

## Web

- [TASK-088](tasks/TASK-088.md) — Criar WebSearchProvider
- [TASK-089](tasks/TASK-089.md) — Implementar primeiro provider de busca
- [TASK-090](tasks/TASK-090.md) — Implementar abertura de página
- [TASK-091](tasks/TASK-091.md) — Implementar normalização HTML/text/JSON/XML
- [TASK-092](tasks/TASK-092.md) — Implementar extração de referências
- [TASK-093](tasks/TASK-093.md) — Implementar política de PDF seguro
- [TASK-094](tasks/TASK-094.md) — Implementar integração com reputação de fontes

## APIs e arquivos

- [TASK-095](tasks/TASK-095.md) — Implementar API Tool
- [TASK-096](tasks/TASK-096.md) — Implementar política HTTPS
- [TASK-097](tasks/TASK-097.md) — Implementar chamadas a outros agentes
- [TASK-098](tasks/TASK-098.md) — Implementar validação das fontes retornadas por agentes
- [TASK-099](tasks/TASK-099.md) — Implementar File Tool interno
- [TASK-100](tasks/TASK-100.md) — Implementar Database Tool interno

## Chat web

- [TASK-101](tasks/TASK-101.md) — Criar frontend web do chat
- [TASK-102](tasks/TASK-102.md) — Implementar streaming
- [TASK-103](tasks/TASK-103.md) — Exibir estados de execução
- [TASK-104](tasks/TASK-104.md) — Exibir fontes
- [TASK-105](tasks/TASK-105.md) — Persistir conversas
- [TASK-106](tasks/TASK-106.md) — Criar resumo de conversa
- [TASK-107](tasks/TASK-107.md) — Implementar retomada por resumo

## Cotas

- [TASK-108](tasks/TASK-108.md) — Criar sistema de cotas
- [TASK-109](tasks/TASK-109.md) — Medir tokens/processamento
- [TASK-110](tasks/TASK-110.md) — Medir requisições
- [TASK-111](tasks/TASK-111.md) — Medir volume de dados
- [TASK-112](tasks/TASK-112.md) — Implementar renovação diária
- [TASK-113](tasks/TASK-113.md) — Implementar alertas 80/95%
- [TASK-114](tasks/TASK-114.md) — Implementar bloqueio 100%

## Administração

- [TASK-115](tasks/TASK-115.md) — Evoluir painel para ADMIN
- [TASK-116](tasks/TASK-116.md) — Gestão de usuários
- [TASK-117](tasks/TASK-117.md) — Gestão de API keys
- [TASK-118](tasks/TASK-118.md) — Gestão de providers
- [TASK-119](tasks/TASK-119.md) — Gestão de cotas
- [TASK-120](tasks/TASK-120.md) — Gestão de configurações
- [TASK-121](tasks/TASK-121.md) — Implementar reautenticação para ações críticas
- [TASK-122](tasks/TASK-122.md) — Implementar logout por inatividade

## Operação

- [TASK-123](tasks/TASK-123.md) — Implementar modo manutenção
- [TASK-124](tasks/TASK-124.md) — Implementar cancelamento/limpeza de fila em manutenção
- [TASK-125](tasks/TASK-125.md) — Implementar reinício pelo painel
- [TASK-126](tasks/TASK-126.md) — Implementar backup manual
- [TASK-127](tasks/TASK-127.md) — Implementar backup agendado
- [TASK-128](tasks/TASK-128.md) — Implementar verificação de integridade
- [TASK-129](tasks/TASK-129.md) — Implementar restore
- [TASK-130](tasks/TASK-130.md) — Implementar backup pré-restore
- [TASK-131](tasks/TASK-131.md) — Implementar updater Git
- [TASK-132](tasks/TASK-132.md) — Implementar flags/tags de versão
- [TASK-133](tasks/TASK-133.md) — Implementar agendamento 00h–03h
- [TASK-134](tasks/TASK-134.md) — Implementar health check pós-update
- [TASK-135](tasks/TASK-135.md) — Implementar rollback automático
- [TASK-136](tasks/TASK-136.md) — Implementar bloqueio de versão com falha
- [TASK-137](tasks/TASK-137.md) — Criar histórico de atualizações

## Qualidade final

- [TASK-138](tasks/TASK-138.md) — Testes unitários completos
- [TASK-139](tasks/TASK-139.md) — Testes de integração
- [TASK-140](tasks/TASK-140.md) — Cenários fixos de regressão
- [TASK-141](tasks/TASK-141.md) — Cenários variáveis
- [TASK-142](tasks/TASK-142.md) — Testes de alucinação
- [TASK-143](tasks/TASK-143.md) — Testes de confiança e volatilidade
- [TASK-144](tasks/TASK-144.md) — Testes de segurança das tools
- [TASK-145](tasks/TASK-145.md) — Métricas finais de qualidade
- [TASK-146](tasks/TASK-146.md) — Checklist de itens críticos
- [TASK-147](tasks/TASK-147.md) — Checklist V1 completa — **marco: V1 completa**
