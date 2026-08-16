# -*- coding: utf-8 -*-
"""Gera os README.md de esqueleto para os módulos de backend/app, frontend, tests,
config e scripts. Documentação apenas — nenhuma linha de código é criada, porque a
stack de implementação ainda não foi escolhida (ver docs/OPEN_QUESTIONS.md)."""

import os

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")

def write(rel_path, content):
    path = os.path.normpath(os.path.join(ROOT, rel_path))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

MODULES = {
    "backend/app/api/README.md": (
        "API para aplicações",
        "docs/API.md",
        "TASK-067 a TASK-073",
        "Camada de entrada HTTP usada por aplicações externas: autenticação por API "
        "key, validação de payload, execução síncrona, timeout, resposta JSON final "
        "e rastreio de consumo.",
    ),
    "backend/app/auth/README.md": (
        "Autenticação e autorização",
        "docs/AUTHENTICATION.md",
        "TASK-009 a TASK-011",
        "Autenticação humana (usuário/senha, perfis ADMIN/USER) e autenticação de "
        "aplicações via API key.",
    ),
    "backend/app/orchestrator/README.md": (
        "Orquestrador",
        "docs/ARCHITECTURE.md e docs/ORCHESTRATOR.md",
        "TASK-020 a TASK-030",
        "Núcleo determinístico: Execution, ExecutionPolicy, ExecutionOrchestrator, "
        "planejamento, validação de plano, execução por etapas, replanejamento, "
        "max_steps, detecção de loop, cancelamento.",
    ),
    "backend/app/policies/README.md": (
        "Policy Engine",
        "docs/ORCHESTRATOR.md",
        "TASK-022",
        "Regras de execução por aplicação/contexto (ExecutionPolicy): permissões de "
        "pesquisa, limites, timeout, contexto.",
    ),
    "backend/app/context/README.md": (
        "Context Manager",
        "docs/ORCHESTRATOR.md",
        "TASK-037 a TASK-043",
        "Assunto principal, entidades recentes, objetivo atual, últimas ações, "
        "referências implícitas, correções, troca de assunto e monitor de janela de "
        "contexto.",
    ),
    "backend/app/planner/README.md": (
        "Planner",
        "docs/ARCHITECTURE.md",
        "TASK-024, TASK-025, TASK-027",
        "Criação e validação do plano de execução (protocolo JSON modelo ↔ "
        "orquestrador) e replanejamento completo quando necessário.",
    ),
    "backend/app/confidence/README.md": (
        "Confidence Engine",
        "docs/TRUST_GUARDRAILS.md",
        "TASK-031 a TASK-033",
        "Confiança do modelo (LOW/MEDIUM/HIGH), volatilidade (VOLATILE/NON_VOLATILE) "
        "e cálculo da confiança final combinando evidências, reputação de fontes e "
        "contradições.",
    ),
    "backend/app/guardrails/README.md": (
        "Guardrails",
        "docs/TRUST_GUARDRAILS.md",
        "TASK-034 a TASK-036",
        "Bloqueio de resposta conclusiva em LOW, regra obrigatória de revalidação "
        "para informação volátil, tratamento de ambiguidade.",
    ),
    "backend/app/llm/README.md": (
        "LLM — abstração de raciocínio local",
        "docs/ARCHITECTURE.md",
        "TASK-014, TASK-016 a TASK-019",
        "Interface LocalLLMProvider, protocolo JSON modelo ↔ orquestrador, "
        "validação dos JSONs internos, prompt-base e composição dinâmica de "
        "prompt/contexto. Ollama é apenas o runtime inicial (ver llm/providers/).",
    ),
    "backend/app/llm/providers/README.md": (
        "Providers de LLM local",
        "docs/ARCHITECTURE.md",
        "TASK-015",
        "Implementações concretas de LocalLLMProvider. A V1 traz apenas "
        "OllamaProvider; outros runtimes (llama.cpp, vLLM) ficam preparados pela "
        "abstração, não implementados agora. Apenas um modelo local fica ativo por "
        "vez na V1.",
    ),
    "backend/app/memory/README.md": (
        "Memória persistente",
        "docs/MEMORY.md",
        "TASK-044 a TASK-051",
        "Modelo de memória por usuário/aplicação, Memory Tool, busca estruturada, "
        "relevância/frequência/last used, retenção, limite fixo e auditoria de "
        "remoção.",
    ),
    "backend/app/knowledge/README.md": (
        "Conhecimento",
        "docs/KNOWLEDGE.md",
        "TASK-052 a TASK-058",
        "Modelo RAW/PROVISIONAL/CONFIRMED, Knowledge Tool, versionamento, escopo "
        "GLOBAL/APPLICATION, evidências/fontes, promoção para CONFIRMED, avaliação "
        "de utilidade.",
    ),
    "backend/app/sources/README.md": (
        "Fontes e reputação",
        "docs/TRUST_GUARDRAILS.md",
        "TASK-059 a TASK-066",
        "Cadastro de fontes (PRIMARY/SECONDARY/UNKNOWN), reputação "
        "(LOW/MEDIUM/HIGH), histórico de reputação, blacklist, bloqueio automático "
        "e desbloqueio (somente ADMIN).",
    ),
    "backend/app/tools/README.md": (
        "Ferramentas (Tool Registry)",
        "docs/TOOLS.md",
        "TASK-046, TASK-053, TASK-088 a TASK-100",
        "Memory Tool, Knowledge Tool, Web Search Tool, File Tool, Database Tool, API "
        "Tool. Catálogo fixo, carregado na inicialização, execução sequencial na V1.",
    ),
    "backend/app/queue/README.md": (
        "Fila",
        "docs/QUEUE.md",
        "TASK-074 a TASK-077",
        "Fila FIFO persistida no PostgreSQL, estados PENDING/RUNNING/COMPLETED/"
        "FAILED, retenção/limpeza. Sem retry automático.",
    ),
    "backend/app/observability/README.md": (
        "Observabilidade",
        "docs/OBSERVABILITY.md",
        "TASK-005, TASK-006, TASK-078 a TASK-083",
        "Logging local rotativo e estruturado no PostgreSQL, Execution Trace, "
        "métricas básicas.",
    ),
    "backend/app/quotas/README.md": (
        "Cotas",
        "docs/QUOTAS.md",
        "TASK-108 a TASK-114",
        "Medição de tokens/requisições/volume por usuário e por API key, renovação "
        "diária, alertas 80/95%, bloqueio em 100%.",
    ),
    "backend/app/panel/README.md": (
        "Painel",
        "docs/PANEL.md",
        "TASK-081 a TASK-083, TASK-115 a TASK-122",
        "Painel web read-only (fila, execução atual, status, logs, erros, consumo) "
        "e, depois, painel administrativo completo (usuários, API keys, providers, "
        "cotas, configurações, manutenção, backups, atualizações, blacklist).",
    ),
    "backend/app/backup/README.md": (
        "Backup e restore",
        "docs/BACKUP_RESTORE.md",
        "TASK-126 a TASK-130",
        "Backup manual/agendado, verificação de integridade "
        "(CREATED/VERIFYING/VALID/FAILED), restore com backup automático pré-"
        "restore.",
    ),
    "backend/app/updater/README.md": (
        "Updater",
        "docs/UPDATER.md",
        "TASK-131 a TASK-137",
        "Atualização via Git por flags/tags, janela noturna 00h–03h, health check "
        "pós-update, rollback automático, bloqueio de versão com falha, histórico.",
    ),
    "backend/app/db/README.md": (
        "Persistência (PostgreSQL)",
        "docs/DATABASE.md",
        "TASK-003, TASK-004",
        "Configuração de acesso ao PostgreSQL local e schema inicial. Demais "
        "domínios de dados ganham schema nas TASKs dos respectivos blocos "
        "funcionais.",
    ),
    "backend/app/db/migrations/README.md": (
        "Migrations",
        "docs/DATABASE.md",
        "TASK-004",
        "Migrations do schema do PostgreSQL. Ferramenta de migration ainda não "
        "escolhida (ver docs/OPEN_QUESTIONS.md) — nenhuma migration foi criada "
        "nesta organização inicial.",
    ),
}

HEADER_TMPL = """# {title}

Documentação: {doc}. TASKs: {tasks}.

{desc}

Nenhum código foi criado neste módulo ainda — este README existe apenas para manter
o diretório versionado e documentar seu propósito antes da implementação (ver
AGENTS.md e docs/OPEN_QUESTIONS.md sobre a stack de implementação).
"""

def main():
    for rel, (title, doc, tasks, desc) in MODULES.items():
        write(rel, HEADER_TMPL.format(title=title, doc=doc, tasks=tasks, desc=desc))
    print(f"Gerados {len(MODULES)} READMEs de módulo.")

if __name__ == "__main__":
    main()
