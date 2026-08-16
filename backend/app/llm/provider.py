"""Interface abstrata `LocalLLMProvider` (TASK-014).

Abstração entre o núcleo do Claudião e o runtime de modelo local, para que
Ollama (TASK-015) não seja a única opção no futuro — llama.cpp, vLLM
(docs/ARCHITECTURE.md: "O núcleo não fica acoplado ao Ollama"). Apenas um
provider fica ativo por vez na V1; a seleção de qual instância usar é decisão
de configuração/painel, fora do escopo desta interface.

Só a interface aqui — nenhuma implementação concreta (isso é TASK-015) e
nenhum detalhe do protocolo JSON modelo↔orquestrador por etapa
(docs/ARCHITECTURE.md, seção "Protocolo interno" — isso é TASK-016/TASK-017).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CompletionRequest:
    """Uma chamada ao modelo local: prompt já composto + parâmetros básicos de
    geração. Composição de prompt/contexto é escopo de TASK-018/TASK-019 — este
    request só carrega o prompt já pronto."""

    prompt: str
    model: str
    temperature: float = 0.0
    max_tokens: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CompletionResponse:
    """Resposta bruta do modelo local — texto ainda não validado/parseado
    contra o protocolo JSON do orquestrador (isso é TASK-017)."""

    text: str
    model: str
    raw: dict[str, Any] = field(default_factory=dict)


class LocalLLMProviderError(RuntimeError):
    """Erro genérico de comunicação com um `LocalLLMProvider` — timeout,
    runtime indisponível, resposta malformada no nível de transporte (não no
    nível do protocolo JSON, que é validado em TASK-017)."""


class LocalLLMProvider(ABC):
    """Contrato que todo runtime de modelo local precisa implementar."""

    @abstractmethod
    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Envia o prompt ao modelo e retorna a resposta bruta (texto).

        Implementações levantam `LocalLLMProviderError` para falhas de
        comunicação com o runtime (não para respostas de conteúdo inválido —
        isso é validado depois, fora do provider)."""

    @abstractmethod
    def is_available(self) -> bool:
        """Verifica, de forma leve, se o runtime está acessível. Usado por
        health checks (TASK-085) — não implementado aqui, só a primitiva."""
