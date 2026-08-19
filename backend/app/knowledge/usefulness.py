"""Avaliação de utilidade pelo orquestrador (TASK-058).

`docs/KNOWLEDGE.md` (seção 12 da especificação mestre): "fluxo desejado:
NÃO SEI → PESQUISO → VALIDO → CONFIRMO → AVALIO UTILIDADE → SALVO." A
avaliação de utilidade é a última etapa antes de um fato ser
efetivamente guardado como reutilizável — vem depois da confirmação
(TASK-057), não antes: um fato `RAW`/`PROVISIONAL` ainda não passou por
validação suficiente para essa pergunta fazer sentido.

A especificação não detalha o critério de "útil" além de posicioná-lo
nesse ponto do fluxo. Diferente da regra de promoção (TASK-057, que só
depende de sinais já registrados no próprio `Knowledge` — confiança,
evidências), utilidade aqui inclui **relevância para o objetivo da
execução atual** — algo inerentemente contextual (depende do que o
usuário/aplicação pediu), que este módulo não tem como calcular sozinho.
Por isso `is_relevant_to_objective` é recebido já avaliado por quem
chama, em vez de derivado aqui — mesmo padrão de
`app.confidence.ambiguity_guardrail` (TASK-036): a guarda combina um
sinal contextual externo com o que já existe no modelo de dados, sem
tentar calcular o sinal contextual sozinha.

Esta é uma avaliação do **orquestrador**, não uma ferramenta que o
modelo aciona via protocolo — por isso, ao contrário de
`promotion_rule.py` (TASK-057), não é exposta em `app.tools.knowledge_tool`.
Onde o orquestrador de fato chama isso antes de decidir persistir
("SALVO") é TASK-088 em diante, quando o Tool Registry/ciclo real de
execução ganham essa integração — não implementado aqui.
"""

from __future__ import annotations

from app.knowledge.knowledge_model import Knowledge, KnowledgeStatus


def is_useful_for_orchestrator(knowledge: Knowledge, is_relevant_to_objective: bool) -> bool:
    """`True` se o orquestrador deve considerar `knowledge` útil o
    bastante para persistir/reutilizar na execução atual: precisa estar
    `CONFIRMED` **e** ser relevante para o objetivo da execução
    (`is_relevant_to_objective`, avaliado por quem chama)."""
    return knowledge.status == KnowledgeStatus.CONFIRMED and is_relevant_to_objective
