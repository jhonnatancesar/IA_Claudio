"""`SearXNGSearchProvider` — primeira implementação concreta de
`WebSearchProvider` (TASK-089).

Usa uma instância local do **SearXNG** (metasearch engine open-source,
autohospedada), via sua API JSON (`GET /search?q=...&format=json`) — mesmo
princípio de `OllamaProvider` (TASK-015): serviço já instalado/rodando
localmente, sem acoplar o núcleo a um fornecedor comercial.

Decisão pedida ao usuário via `AskUserQuestion` (TASK-089): as
alternativas óbvias sem custo (scraping HTML do DuckDuckGo) esbarraram em
proteção anti-bot real (`SearxEngineAccessDeniedException`/desafio
`anomaly.js` — contornar isso está fora de cogitação, é bypass de
bot-detection) e a API oficial de "Instant Answer" do DuckDuckGo só
retorna algo para tópicos tipo enciclopédia, ficando vazia para buscas
genéricas do dia a dia (testado com queries reais antes de descartar).
SearXNG resolve isso agregando vários motores de busca de verdade sem
exigir API key paga de terceiro. Rodando via Docker (Docker Desktop já
instalado nesta máquina) — `docker run ... searxng/searxng`, config em
`config/searxng/settings.yml` (não versionado, mesmo princípio de
`config/.env`), com `search.formats: [html, json]` habilitado
explicitamente (desligado por padrão na imagem oficial).
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from app.web_search.provider import (
    SearchRequest,
    SearchResponse,
    SearchResult,
    WebSearchProvider,
    WebSearchProviderError,
)

DEFAULT_BASE_URL = "http://localhost:8888"
DEFAULT_TIMEOUT = 10.0


def _default_fetch(url: str, timeout: float) -> bytes:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return response.read()


class SearXNGSearchProvider(WebSearchProvider):
    """`WebSearchProvider` para uma instância local do SearXNG."""

    def __init__(self, base_url: str = DEFAULT_BASE_URL, timeout: float = DEFAULT_TIMEOUT) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._fetch = _default_fetch

    def search(self, request: SearchRequest) -> SearchResponse:
        params = urllib.parse.urlencode({"q": request.query, "format": "json"})
        url = f"{self._base_url}/search?{params}"

        try:
            body = self._fetch(url, self._timeout)
        except (urllib.error.URLError, OSError) as exc:
            raise WebSearchProviderError(str(exc)) from exc

        try:
            data: dict[str, Any] = json.loads(body)
        except json.JSONDecodeError as exc:
            raise WebSearchProviderError(f"resposta inválida do SearXNG: {exc}") from exc

        results = [
            SearchResult(
                url=item.get("url", ""),
                title=item.get("title", ""),
                snippet=item.get("content") or "",
            )
            for item in data.get("results", [])[: request.max_results]
        ]
        return SearchResponse(results=results, raw=data)

    def is_available(self) -> bool:
        try:
            self._fetch(f"{self._base_url}/healthz", self._timeout)
        except (urllib.error.URLError, OSError):
            return False
        return True
