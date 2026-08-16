# -*- coding: utf-8 -*-
"""Gera docs/tasks/TASK-XXX.md (001..147) e docs/tasks/README.md a partir de
tasks_data.py. Roda uma única vez durante a organização inicial do repositório;
pode ser reexecutado no futuro para regenerar os arquivos caso a fonte mude."""

import os
from tasks_data import all_tasks, MILESTONE_TASK, V1_COMPLETE_TASK

TASKS = all_tasks()
BY_ID = {t["id"]: t for t in TASKS}
OUT_DIR = os.path.join("docs", "tasks")

TEST_HINTS = {
    "Fundação": "Testes unitários do componente correspondente (config, schema, "
                "logging ou catálogo de erros), conforme docs/TESTING.md. Estrutura "
                "pura de diretório (sem lógica) não exige teste automatizado.",
    "Segurança e identidade": "Testes unitários de autenticação/autorização "
                "(criação de usuário, papéis, validação de API key, "
                "criptografia/descriptografia de segredo), conforme docs/TESTING.md.",
    "LLM": "Testes unitários do provider e do protocolo JSON "
                "(parser/validator contra JSON malformado ou fora do contrato), "
                "conforme docs/TESTING.md.",
    "Orquestração": "Testes unitários do orquestrador para este passo do ciclo de "
                "execução, incluindo casos de erro/limite; teste de integração "
                "cobrindo o ciclo completo quando aplicável, conforme docs/TESTING.md.",
    "Confiança e guardrails": "Testes unitários de confiança/guardrails, incluindo "
                "casos de bloqueio (LOW), revalidação (VOLATILE) e ambiguidade; "
                "testes explícitos contra alucinação quando aplicável, conforme "
                "docs/TESTING.md.",
    "Contexto": "Testes unitários do ContextManager para este comportamento "
                "(rastreamento, correção, troca de assunto ou aviso de janela), "
                "conforme docs/TESTING.md.",
    "Memória": "Testes unitários de memória (persistência, busca, relevância, "
                "retenção ou auditoria de remoção, conforme o caso); teste de "
                "integração com o banco quando a TASK persistir dados, conforme "
                "docs/TESTING.md.",
    "Conhecimento": "Testes unitários de conhecimento (modelo RAW/PROVISIONAL/"
                "CONFIRMED, versionamento, escopo, evidências ou promoção, conforme "
                "o caso), conforme docs/TESTING.md.",
    "Fontes": "Testes unitários de fontes/reputação/blacklist para este "
                "comportamento específico, conforme docs/TESTING.md.",
    "Aplicações": "Testes unitários e de integração da API para aplicações "
                "(payload válido/inválido, timeout, execution_id, resposta final), "
                "conforme docs/TESTING.md.",
    "Fila": "Testes unitários e de integração da fila (estados, persistência, "
                "retenção), conforme docs/TESTING.md.",
    "Observabilidade inicial": "Testes unitários do Execution Trace/métricas e, "
                "quando aplicável, teste manual do painel read-only, conforme "
                "docs/TESTING.md.",
    "Marco utilizável inicial": "Cenário real fixo cobrindo o fluxo ponta a ponta "
                "envolvido; ver detalhamento específico abaixo.",
    "Web": "Testes unitários do WebSearchProvider/normalização/política de PDF, com "
                "casos de fonte HIGH/MEDIUM/LOW/UNKNOWN, conforme docs/TESTING.md.",
    "APIs e arquivos": "Testes unitários da ferramenta correspondente (API Tool, "
                "File Tool ou Database Tool), incluindo casos fora do contrato "
                "(devem ser bloqueados pelo orquestrador), conforme docs/TESTING.md.",
    "Chat web": "Teste manual/E2E do frontend para este comportamento (streaming, "
                "estados, fontes, persistência ou retomada), conforme docs/TESTING.md.",
    "Cotas": "Testes unitários de cotas (medição, renovação, alertas, bloqueio), "
                "conforme docs/TESTING.md.",
    "Administração": "Testes unitários/integração do painel administrativo para "
                "esta gestão específica, incluindo o fluxo de reautenticação em "
                "ações críticas quando aplicável, conforme docs/TESTING.md.",
    "Operação": "Teste de integração do fluxo operacional (manutenção, reinício, "
                "backup, restore ou updater, conforme o caso), incluindo o caminho "
                "de falha/rollback quando aplicável, conforme docs/TESTING.md.",
    "Qualidade final": "Esta TASK é, ela própria, parte da suíte de testes/qualidade "
                "final da V1 — ver detalhamento específico abaixo.",
}

def deps_for(tid):
    if tid == 1:
        return "Nenhuma — primeira TASK do projeto."
    return f"TASK-{tid-1:03d} concluída."

def escopo_for(t):
    return (
        f"Implementar exatamente o objetivo declarado acima, dentro do bloco "
        f"funcional \"{t['group']}\" (ver docs/BACKLOG.md e docs/ROADMAP.md), "
        f"conforme AGENTS.md, CLAUDE.md e `docs/{t['doc']}`. Nenhuma funcionalidade "
        f"de TASK posterior deve ser adiantada."
    )

FORA_DE_ESCOPO_DEFAULT = (
    "Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item "
    "listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente "
    "na especificação mestre ou em docs/DECISION_LOG.md."
)

def criterios_for(t):
    return (
        f"Objetivo declarado implementado e verificável; testes esperados "
        f"(abaixo) escritos e aprovados; `docs/{t['doc']}` e "
        f"`docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada "
        f"foi alterada silenciosamente."
    )

SPECIAL_CLOSING = {
    MILESTONE_TASK: (
        "\n## Marco\n\n"
        "Esta TASK é o **marco oficial do primeiro Claudião utilizável em "
        "produção controlada** (seção 47 da especificação mestre — ver "
        "docs/V1_SCOPE.md). Sua conclusão certifica que todos os itens do mínimo "
        "utilizável (TASK-001 a TASK-086) estão implementados, testados e "
        "validados com uma aplicação real — não apenas o objetivo pontual desta "
        "TASK isoladamente.\n"
    ),
    V1_COMPLETE_TASK: (
        "\n## Marco\n\n"
        "Esta TASK fecha o checklist da **V1 completa** (seção 48 da "
        "especificação mestre — ver docs/V1_SCOPE.md). Sua conclusão certifica "
        "que todos os itens planejados da V1 (TASK-001 a TASK-146) estão "
        "concluídos, testados e documentados.\n"
    ),
}

def render_task(t):
    tid = t["id"]
    title = t["title"]
    doc = t["doc"]
    lines = []
    lines.append(f"# TASK-{tid:03d} — {title}")
    lines.append("")
    lines.append("Status: Pendente")
    lines.append("")
    lines.append("## Objetivo")
    lines.append("")
    lines.append(f"{title}, conforme a especificação mestre "
                  f"(`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "
                  f"\"{t['group']}\") e `docs/{doc}`.")
    lines.append("")
    lines.append("## Escopo")
    lines.append("")
    lines.append(escopo_for(t))
    lines.append("")
    lines.append("## Fora de escopo")
    lines.append("")
    lines.append(FORA_DE_ESCOPO_DEFAULT)
    lines.append("")
    lines.append("## Dependências")
    lines.append("")
    lines.append(deps_for(tid))
    lines.append("")
    lines.append("## Critérios de aceite")
    lines.append("")
    lines.append(criterios_for(t))
    lines.append("")
    lines.append("## Testes esperados")
    lines.append("")
    lines.append(TEST_HINTS.get(t["group"], "Ver docs/TESTING.md."))
    lines.append("")
    lines.append("## Documentação afetada")
    lines.append("")
    lines.append(f"`docs/{doc}`, `docs/tasks/README.md`"
                  + (", `docs/DECISION_LOG.md` (se a TASK gerar decisão nova)"))
    lines.append("")
    if tid in SPECIAL_CLOSING:
        lines.append(SPECIAL_CLOSING[tid])
    return "\n".join(lines).rstrip() + "\n"


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for t in TASKS:
        path = os.path.join(OUT_DIR, f"TASK-{t['id']:03d}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(render_task(t))
    print(f"Gerados {len(TASKS)} arquivos TASK-XXX.md em {OUT_DIR}")


if __name__ == "__main__":
    main()
