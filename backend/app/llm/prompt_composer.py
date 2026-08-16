"""Composição dinâmica de prompt/contexto (TASK-019).

Monta o prompt completo enviado ao modelo a cada etapa: prompt-base fixo
(TASK-018) + o pedido atual (item 3 da hierarquia de prioridade,
docs/ARCHITECTURE.md) + o histórico de etapas já executadas nesta mesma
execução (para o modelo "lembrar" o que já tentou/descobriu ao longo do ciclo
do orquestrador — seção 6 da especificação mestre).

Não inclui memória persistente, conhecimento confirmado/provisório nem o
Context Manager entre conversas (TASK-037, TASK-044, TASK-052 em diante, não
implementados ainda) — a hierarquia de prioridade reserva lugar para eles
(itens 4 a 8), mas esta TASK só compõe o que já existe no projeto até aqui.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.llm.prompt import get_base_prompt
from app.llm.protocol import ModelStep


@dataclass(frozen=True)
class StepRecord:
    """Uma etapa já executada nesta execução: a decisão do modelo e o
    resultado observado (ex.: saída de uma ferramenta) — dá continuidade ao
    raciocínio nas etapas seguintes do mesmo ciclo."""

    step: ModelStep
    observation: str | None = None


def compose_prompt(
    execution_id: str,
    objective: str,
    history: list[StepRecord] | None = None,
) -> str:
    """Monta o prompt completo para a próxima chamada ao modelo local.

    `objective` é o pedido atual do usuário/aplicação (prioridade 3 da
    hierarquia). `history` são as etapas já executadas nesta mesma execução,
    em ordem cronológica — vazio ou `None` na primeira chamada.
    """
    if not objective or not objective.strip():
        raise ValueError("objective não pode ser vazio")

    sections = [get_base_prompt()]
    sections.append(
        f"\nExecução atual: {execution_id}\nPedido atual: {objective.strip()}\n"
    )

    if history:
        lines = ["\nEtapas já executadas nesta execução:"]
        for index, record in enumerate(history, start=1):
            lines.append(f"{index}. Você decidiu: {record.step.to_json()}")
            if record.observation is not None:
                lines.append(f"   Resultado observado: {record.observation}")
        sections.append("\n".join(lines) + "\n")

    return "\n".join(sections)
