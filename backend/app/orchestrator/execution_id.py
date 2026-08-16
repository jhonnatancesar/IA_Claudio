"""Geração de `execution_id` (TASK-021).

Cada requisição recebe um `execution_id` único (seção 25 da especificação
mestre) — reenvios e retries manuais sempre geram um novo, nunca reaproveitam
o anterior. UUID4 (aleatório, sem informação embutida) é suficiente, e já é o
formato exigido pela validação semântica do protocolo
(`app.llm.protocol_validator`, TASK-017).
"""

from __future__ import annotations

import uuid


def generate_execution_id() -> str:
    """Gera um `execution_id` novo, único, no formato UUID (string)."""
    return str(uuid.uuid4())
