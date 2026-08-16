"""Protocolo JSON modelo ↔ orquestrador (TASK-016).

Um JSON por etapa (docs/ARCHITECTURE.md, seção "Protocolo interno" — seção 7
da especificação mestre). Sem dependência obrigatória de tool calling nativo
do modelo: o modelo local só precisa gerar texto no formato deste protocolo.

Define o formato e faz a decodificação básica (campos obrigatórios, valores
dentro do enum). Validação mais profunda/robusta contra entrada adversarial
é escopo da TASK-017 — este módulo cobre o essencial para não deixar passar
JSON claramente fora do contrato, mas TASK-017 pode construir em cima.

`Confidence` mora aqui porque é o protocolo JSON que primeiro precisa dela
como vocabulário compartilhado; a lógica de *cálculo* de confiança (Confidence
Engine) é escopo de TASK-031/TASK-033, que reaproveita este `Enum` em vez de
duplicá-lo.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Action(StrEnum):
    """Ações que o modelo pode declarar numa etapa. Conjunto mínimo sustentado
    pela especificação mestre: `USE_TOOL` (exemplo explícito, seção 7) e
    `RESPOND` (resposta final, exigida pelo ciclo do orquestrador, seção 6).
    Não inclui um valor separado para replanejamento — replanejar é descartar
    o plano e voltar a gerar etapas neste mesmo protocolo, não uma ação
    própria (docs/ARCHITECTURE.md)."""

    USE_TOOL = "USE_TOOL"
    RESPOND = "RESPOND"


class Confidence(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ProtocolDecodeError(ValueError):
    """Levantado quando um JSON não corresponde ao protocolo: JSON malformado,
    campo obrigatório ausente, ou `action`/`confidence` fora do enum."""


_REQUIRED_FIELDS = ("execution_id", "action", "confidence", "reason")


@dataclass(frozen=True)
class ModelStep:
    """Uma etapa do protocolo: o que o modelo decide fazer, com justificativa
    e confiança declaradas."""

    execution_id: str
    action: Action
    confidence: Confidence
    reason: str
    tool: str | None = None
    parameters: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "execution_id": self.execution_id,
            "action": self.action.value,
            "confidence": self.confidence.value,
            "reason": self.reason,
        }
        if self.tool is not None:
            data["tool"] = self.tool
        if self.parameters:
            data["parameters"] = self.parameters
        return data

    def to_json(self) -> str:
        # ensure_ascii=False (fix, TASK-019): sem isso, acentos em `reason`
        # viram escapes \uXXXX — o protocolo é PT-BR (docs/AGENTS.md), então o
        # JSON deve ficar legível em UTF-8 nativo, não escapado.
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ModelStep":
        if not isinstance(data, dict):
            raise ProtocolDecodeError("etapa do protocolo deve ser um objeto JSON")

        missing = [f for f in _REQUIRED_FIELDS if f not in data]
        if missing:
            raise ProtocolDecodeError(
                f"campos obrigatórios ausentes: {', '.join(missing)}"
            )

        try:
            action = Action(data["action"])
        except ValueError as exc:
            raise ProtocolDecodeError(f"action inválida: {data['action']!r}") from exc

        try:
            confidence = Confidence(data["confidence"])
        except ValueError as exc:
            raise ProtocolDecodeError(
                f"confidence inválida: {data['confidence']!r}"
            ) from exc

        tool = data.get("tool")
        if action == Action.USE_TOOL and not tool:
            raise ProtocolDecodeError("action USE_TOOL exige o campo 'tool'")

        parameters_raw = data.get("parameters") or {}
        if not isinstance(parameters_raw, dict):
            # Fix (TASK-017): sem isso, `dict(parameters_raw)` para um valor
            # que não é dict/lista-de-pares levanta ValueError/TypeError não
            # capturado aqui, escapando como um erro não relacionado ao
            # protocolo em vez de um ProtocolDecodeError claro.
            raise ProtocolDecodeError("parameters deve ser um objeto JSON")

        return cls(
            execution_id=str(data["execution_id"]),
            action=action,
            confidence=confidence,
            reason=str(data["reason"]),
            tool=tool,
            parameters=dict(parameters_raw),
        )

    @classmethod
    def from_json(cls, raw: str) -> "ModelStep":
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ProtocolDecodeError(f"JSON malformado: {exc}") from exc
        return cls.from_dict(data)
