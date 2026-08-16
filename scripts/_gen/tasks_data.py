# -*- coding: utf-8 -*-
# Dados estruturados das TASKs da especificação mestre (seção 51).
# Usado apenas para gerar docs/BACKLOG.md e docs/tasks/TASK-XXX.md.
# Este arquivo não é parte do produto e pode ser removido depois da geração,
# mas fica versionado para permitir regenerar os documentos se necessário.

# Cada grupo: (nome_do_grupo, doc_principal_afetado, [(id, titulo), ...])
GROUPS = [
    ("Fundação", "ARCHITECTURE.md", [
        (1, "Inicializar estrutura do projeto Claudião"),
        (2, "Criar configuração central"),
        (3, "Configurar PostgreSQL local"),
        (4, "Criar schema inicial do banco"),
        (5, "Criar sistema de logging local"),
        (6, "Criar logging estruturado no PostgreSQL"),
        (7, "Criar catálogo interno de erros"),
        (8, "Implementar resposta padrão de erro JSON"),
    ]),
    ("Segurança e identidade", "AUTHENTICATION.md", [
        (9, "Criar autenticação de usuários"),
        (10, "Criar roles ADMIN e USER"),
        (11, "Criar autenticação de aplicações via API key"),
        (12, "Implementar criptografia de segredos"),
        (13, "Implementar chave mestra externa ao banco"),
    ]),
    ("LLM", "ARCHITECTURE.md", [
        (14, "Criar interface LocalLLMProvider"),
        (15, "Implementar OllamaProvider"),
        (16, "Criar protocolo JSON modelo ↔ orquestrador"),
        (17, "Criar validação dos JSONs internos"),
        (18, "Criar prompt-base do Claudião"),
        (19, "Criar composição dinâmica de prompt/contexto"),
    ]),
    ("Orquestração", "ORCHESTRATOR.md", [
        (20, "Criar modelo de Execution"),
        (21, "Implementar execution_id"),
        (22, "Criar ExecutionPolicy"),
        (23, "Criar ExecutionOrchestrator"),
        (24, "Implementar planejamento inicial"),
        (25, "Implementar validação de plano"),
        (26, "Implementar execução por etapas"),
        (27, "Implementar replanejamento completo"),
        (28, "Implementar max_steps"),
        (29, "Implementar detecção de loop"),
        (30, "Implementar cancelamento"),
    ]),
    ("Confiança e guardrails", "TRUST_GUARDRAILS.md", [
        (31, "Implementar confiança LOW/MEDIUM/HIGH do modelo"),
        (32, "Implementar volatilidade VOLATILE/NON_VOLATILE"),
        (33, "Implementar confidence engine do orquestrador"),
        (34, "Implementar bloqueio de resposta conclusiva em LOW"),
        (35, "Implementar regra obrigatória para informação volátil"),
        (36, "Implementar tratamento de ambiguidade"),
    ]),
    ("Contexto", "ORCHESTRATOR.md", [
        (37, "Criar ContextManager"),
        (38, "Criar active topic"),
        (39, "Criar rastreamento de entidades/referências"),
        (40, "Implementar correção de contexto"),
        (41, "Implementar detecção de troca de assunto"),
        (42, "Implementar monitor de janela de contexto"),
        (43, "Implementar aviso em 80%"),
    ]),
    ("Memória", "MEMORY.md", [
        (44, "Criar modelo de memória persistente"),
        (45, "Separar memória por usuário/aplicação"),
        (46, "Implementar Memory Tool"),
        (47, "Implementar busca estruturada de memória"),
        (48, "Implementar relevância/frequência/last used"),
        (49, "Implementar política de retenção"),
        (50, "Implementar limite fixo de memória"),
        (51, "Implementar auditoria de memória removida"),
    ]),
    ("Conhecimento", "KNOWLEDGE.md", [
        (52, "Criar modelo RAW/PROVISIONAL/CONFIRMED"),
        (53, "Implementar Knowledge Tool"),
        (54, "Implementar versionamento de conhecimento"),
        (55, "Implementar escopo GLOBAL/APPLICATION"),
        (56, "Implementar evidências/fontes"),
        (57, "Implementar regra de promoção para CONFIRMED"),
        (58, "Implementar avaliação de utilidade pelo orquestrador"),
    ]),
    ("Fontes", "TRUST_GUARDRAILS.md", [
        (59, "Criar cadastro de fontes"),
        (60, "Implementar PRIMARY/SECONDARY/UNKNOWN"),
        (61, "Implementar reputação LOW/MEDIUM/HIGH"),
        (62, "Implementar atualização de reputação"),
        (63, "Criar histórico de reputação"),
        (64, "Criar blacklist"),
        (65, "Implementar bloqueio automático"),
        (66, "Implementar desbloqueio somente ADMIN"),
    ]),
    ("Aplicações", "API.md", [
        (67, "Criar API local do Claudião"),
        (68, "Criar validação de payload"),
        (69, "Implementar execução síncrona"),
        (70, "Implementar timeout definido pela aplicação"),
        (71, "Implementar erro de timeout"),
        (72, "Implementar resposta JSON final"),
        (73, "Implementar rastreio de consumo"),
    ]),
    ("Fila", "QUEUE.md", [
        (74, "Criar fila FIFO"),
        (75, "Persistir fila no PostgreSQL"),
        (76, "Criar estados da fila"),
        (77, "Implementar retenção/limpeza"),
    ]),
    ("Observabilidade inicial", "OBSERVABILITY.md", [
        (78, "Criar Execution Trace"),
        (79, "Registrar ferramentas/passos/tempos"),
        (80, "Criar métricas básicas"),
        (81, "Criar painel web read-only"),
        (82, "Mostrar execuções no painel"),
        (83, "Mostrar erros/logs/consumo"),
    ]),
    ("Marco utilizável inicial", "V1_SCOPE.md", [
        (84, "Criar CLI/chat de teste"),
        (85, "Criar health check inicial"),
        (86, "Criar suíte mínima de testes críticos"),
        (87, "Validar primeiro uso com aplicação real"),
    ]),
    ("Web", "TOOLS.md", [
        (88, "Criar WebSearchProvider"),
        (89, "Implementar primeiro provider de busca"),
        (90, "Implementar abertura de página"),
        (91, "Implementar normalização HTML/text/JSON/XML"),
        (92, "Implementar extração de referências"),
        (93, "Implementar política de PDF seguro"),
        (94, "Implementar integração com reputação de fontes"),
    ]),
    ("APIs e arquivos", "TOOLS.md", [
        (95, "Implementar API Tool"),
        (96, "Implementar política HTTPS"),
        (97, "Implementar chamadas a outros agentes"),
        (98, "Implementar validação das fontes retornadas por agentes"),
        (99, "Implementar File Tool interno"),
        (100, "Implementar Database Tool interno"),
    ]),
    ("Chat web", "ARCHITECTURE.md", [
        (101, "Criar frontend web do chat"),
        (102, "Implementar streaming"),
        (103, "Exibir estados de execução"),
        (104, "Exibir fontes"),
        (105, "Persistir conversas"),
        (106, "Criar resumo de conversa"),
        (107, "Implementar retomada por resumo"),
    ]),
    ("Cotas", "QUOTAS.md", [
        (108, "Criar sistema de cotas"),
        (109, "Medir tokens/processamento"),
        (110, "Medir requisições"),
        (111, "Medir volume de dados"),
        (112, "Implementar renovação diária"),
        (113, "Implementar alertas 80/95%"),
        (114, "Implementar bloqueio 100%"),
    ]),
    ("Administração", "PANEL.md", [
        (115, "Evoluir painel para ADMIN"),
        (116, "Gestão de usuários"),
        (117, "Gestão de API keys"),
        (118, "Gestão de providers"),
        (119, "Gestão de cotas"),
        (120, "Gestão de configurações"),
        (121, "Implementar reautenticação para ações críticas"),
        (122, "Implementar logout por inatividade"),
    ]),
    ("Operação", "OPERATIONS.md", [
        (123, "Implementar modo manutenção"),
        (124, "Implementar cancelamento/limpeza de fila em manutenção"),
        (125, "Implementar reinício pelo painel"),
        (126, "Implementar backup manual"),
        (127, "Implementar backup agendado"),
        (128, "Implementar verificação de integridade"),
        (129, "Implementar restore"),
        (130, "Implementar backup pré-restore"),
        (131, "Implementar updater Git"),
        (132, "Implementar flags/tags de versão"),
        (133, "Implementar agendamento 00h–03h"),
        (134, "Implementar health check pós-update"),
        (135, "Implementar rollback automático"),
        (136, "Implementar bloqueio de versão com falha"),
        (137, "Criar histórico de atualizações"),
    ]),
    ("Qualidade final", "TESTING.md", [
        (138, "Testes unitários completos"),
        (139, "Testes de integração"),
        (140, "Cenários fixos de regressão"),
        (141, "Cenários variáveis"),
        (142, "Testes de alucinação"),
        (143, "Testes de confiança e volatilidade"),
        (144, "Testes de segurança das tools"),
        (145, "Métricas finais de qualidade"),
        (146, "Checklist de itens críticos"),
        (147, "Checklist V1 completa"),
    ]),
]

# Overrides de documentação afetada por TASK específica (quando o doc principal do
# grupo não é o mais preciso para aquela TASK pontual).
DOC_OVERRIDE = {
    3: "DATABASE.md", 4: "DATABASE.md",
    5: "OBSERVABILITY.md", 6: "OBSERVABILITY.md",
    7: "ERROR_CATALOG.md", 8: "ERROR_CATALOG.md",
    12: "SECURITY.md", 13: "SECURITY.md",
    85: "OPERATIONS.md",
    86: "TESTING.md",
    96: "SECURITY.md",
    99: "TOOLS.md", 100: "TOOLS.md",
    123: "OPERATIONS.md", 124: "OPERATIONS.md", 125: "OPERATIONS.md",
    126: "BACKUP_RESTORE.md", 127: "BACKUP_RESTORE.md", 128: "BACKUP_RESTORE.md",
    129: "BACKUP_RESTORE.md", 130: "BACKUP_RESTORE.md",
    131: "UPDATER.md", 132: "UPDATER.md", 133: "UPDATER.md", 134: "UPDATER.md",
    135: "UPDATER.md", 136: "UPDATER.md", 137: "UPDATER.md",
}

MILESTONE_TASK = 87
V1_COMPLETE_TASK = 147

def all_tasks():
    """Retorna lista de dicts: id, titulo, grupo, doc."""
    out = []
    for group_name, group_doc, items in GROUPS:
        for tid, title in items:
            out.append({
                "id": tid,
                "title": title,
                "group": group_name,
                "doc": DOC_OVERRIDE.get(tid, group_doc),
            })
    out.sort(key=lambda x: x["id"])
    return out
