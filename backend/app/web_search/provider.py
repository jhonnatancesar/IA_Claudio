"""Interface abstrata `WebSearchProvider` (TASK-088).

Abstração entre o núcleo do Claudião e o serviço de busca web usado pela
Web Search Tool, para que nenhum fornecedor específico (Google, Firecrawl,
Exa, Parallel, ...) fique acoplado diretamente ao núcleo — mesmo princípio
de `LocalLLMProvider` (TASK-014) para o runtime de modelo local
(`docs/ARCHITECTURE.md`: "O núcleo não fica acoplado ao Ollama"; `docs/TOOLS.md`:
"A pesquisa usa uma abstração genérica `WebSearchProvider`, sem acoplamento
direto a Google, Firecrawl, Exa, Parallel ou outro fornecedor"). Apenas um
provider fica ativo por vez na V1.

Só a interface aqui — nenhuma implementação concreta (isso é TASK-089),
nenhuma abertura/leitura de página (TASK-090), nenhuma normalização de
conteúdo (TASK-091), nenhuma extração de referências (TASK-092), nenhuma
política de PDF (TASK-093) e nenhuma integração com reputação de fontes
(TASK-094).

`docs/TOOLS.md` descreve a busca como `search(query, max_results, purpose)`.
Aqui os três parâmetros ficam agrupados em `SearchRequest` (dataclass),
mesmo padrão de `CompletionRequest`/`CompletionResponse` em
`app.llm.provider` (TASK-014) — request/response tipados em vez de
parâmetros soltos, para manter espaço de extensão futura (ex.: `metadata`)
sem quebrar a assinatura do método `search`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class SearchPurpose(StrEnum):
    """Propósitos de busca previstos em `docs/TOOLS.md` ("Purposes possíveis").
    A especificação deixa a lista aberta ("e outros futuros") — novos valores
    são adicionados quando uma TASK concreta precisar deles, não
    antecipados aqui."""

    GENERAL_RESEARCH = "GENERAL_RESEARCH"
    ENTITY_VERIFICATION = "ENTITY_VERIFICATION"
    CURRENT_INFORMATION = "CURRENT_INFORMATION"
    PRODUCT_IDENTITY = "PRODUCT_IDENTITY"


@dataclass(frozen=True)
class SearchRequest:
    """Uma chamada de busca: termo, quantidade máxima de resultados e o
    propósito da busca (`docs/TOOLS.md`)."""

    query: str
    max_results: int
    purpose: SearchPurpose
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SearchResult:
    """Um resultado individual de busca — só o que a própria busca retorna
    (URL, título, trecho). Abrir e ler a página apontada por `url` é
    TASK-090, não desta interface."""

    url: str
    title: str
    snippet: str


@dataclass(frozen=True)
class SearchResponse:
    """Resposta bruta de uma busca — lista de resultados ainda não validados
    contra reputação de fontes (`app.sources.source_registry`, TASK-094)."""

    results: list[SearchResult]
    raw: dict[str, Any] = field(default_factory=dict)


class WebSearchProviderError(RuntimeError):
    """Erro genérico de comunicação com um `WebSearchProvider` — timeout,
    serviço indisponível, resposta malformada no nível de transporte."""


class WebSearchProvider(ABC):
    """Contrato que todo provider de busca web precisa implementar."""

    @abstractmethod
    def search(self, request: SearchRequest) -> SearchResponse:
        """Executa a busca e retorna os resultados brutos.

        Implementações levantam `WebSearchProviderError` para falhas de
        comunicação com o serviço (não para "nenhum resultado encontrado",
        que é uma `SearchResponse` com `results` vazio, não um erro)."""

    @abstractmethod
    def is_available(self) -> bool:
        """Verifica, de forma leve, se o serviço de busca está acessível.
        Usado por health checks (TASK-085) — não conectado aqui, só a
        primitiva."""
