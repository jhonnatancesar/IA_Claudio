"""Validação de payload da API local (TASK-068).

`docs/API.md`: "a aplicação envia contexto, tipo de uso, política
(`ExecutionPolicy`), permissão de pesquisa, timeout, limites e dados
necessários. O agente valida os campos obrigatórios antes de iniciar. Se
faltar campo obrigatório, retorna erro imediatamente, sem inferir ou
preencher." `ExecutionRequest` formaliza esses campos como um schema
Pydantic — o FastAPI já rejeita automaticamente um corpo que não bate com
ele (campo ausente/tipo errado), sem inferir nem preencher nada por
conta própria.

Campos obrigatórios: `objective` ("dados necessários" — o pedido em si),
`usage_type` ("tipo de uso"), `web_search_allowed` ("permissão de
pesquisa" — mapeia para `ExecutionPolicy.web_search_allowed`, TASK-022),
`timeout_seconds` ("timeout" — mapeia para
`ExecutionPolicy.for_application`, que já exige esse campo). `context`
("contexto") e `max_steps` ("limites") são opcionais, com `None` como
padrão explícito — nenhum dos dois é inferido a partir de outro campo.

Montar a `ExecutionPolicy` de fato e executar via `ExecutionOrchestrator`
a partir deste schema é TASK-069, não implementado aqui — esta TASK só
garante que o payload chegou completo e com tipos corretos antes de
qualquer processamento.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ExecutionRequest(BaseModel):
    objective: str = Field(min_length=1)
    usage_type: str = Field(min_length=1)
    web_search_allowed: bool
    timeout_seconds: float = Field(gt=0)
    context: dict[str, Any] | None = None
    max_steps: int | None = Field(default=None, gt=0)
