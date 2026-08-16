"""`OllamaProvider` — primeira implementação concreta de `LocalLLMProvider`
(TASK-015).

Usa o SDK oficial `ollama` (pacote `ollama`, mantido pela Ollama Inc.) contra
o runtime Ollama local (docs/ARCHITECTURE.md: Ollama é o runtime inicial da
V1, atrás da abstração `LocalLLMProvider`). Nenhum modelo foi baixado/
escolhido ainda (docs/OPEN_QUESTIONS.md, item 3) — este provider funciona com
qualquer modelo já disponível no Ollama local, passado via
`CompletionRequest.model`.
"""

from __future__ import annotations

from typing import Any

import ollama

from app.llm.provider import (
    CompletionRequest,
    CompletionResponse,
    LocalLLMProvider,
    LocalLLMProviderError,
)

DEFAULT_HOST = "http://localhost:11434"


class OllamaProvider(LocalLLMProvider):
    """`LocalLLMProvider` para o runtime Ollama, via seu SDK oficial."""

    def __init__(self, host: str = DEFAULT_HOST) -> None:
        self._client = ollama.Client(host=host)

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        options: dict[str, Any] = {"temperature": request.temperature}
        if request.max_tokens is not None:
            options["num_predict"] = request.max_tokens

        try:
            raw = self._client.generate(
                model=request.model, prompt=request.prompt, options=options
            )
        except (ollama.ResponseError, ConnectionError) as exc:
            raise LocalLLMProviderError(str(exc)) from exc

        raw_dict: dict[str, Any] = (
            raw.model_dump() if hasattr(raw, "model_dump") else dict(raw)
        )
        return CompletionResponse(
            text=raw_dict.get("response", ""),
            model=request.model,
            raw=raw_dict,
        )

    def is_available(self) -> bool:
        try:
            self._client.list()
        except Exception:
            return False
        return True
