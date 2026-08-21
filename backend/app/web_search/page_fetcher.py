"""Abertura de página web (TASK-090).

`docs/TOOLS.md`: "A pesquisa encontra resultados; o agente pode abrir e
ler a página selecionada." — "Lê **somente aquela página** — não segue
links automaticamente." — "Só abre outro link se usuário ou aplicação
pedir." — "Sem cache de pesquisas/páginas na V1."

Diferente de `WebSearchProvider` (TASK-088/TASK-089), abrir uma página é
uma operação HTTP genérica — não existe fornecedor para abstrair (não é
"Google vs. Firecrawl", é só buscar a URL que a busca já retornou), então
aqui é uma função simples, sem classe/ABC. `urllib.request` (biblioteca
padrão), sem dependência nova, mesmo princípio de `scripts/chat.py`
(TASK-084) e `SearXNGSearchProvider` (TASK-089).

Só a abertura/leitura bruta aqui — nenhuma normalização de conteúdo por
tipo (HTML/text/JSON/XML, TASK-091), nenhuma extração de referências/links
da página (TASK-092), nenhuma política de PDF seguro (TASK-093) e nenhuma
integração com reputação de fontes (TASK-094). `open_page` não segue
hyperlinks encontrados no corpo da página — só faz uma requisição HTTP
para a `url` recebida; redirecionamentos HTTP (3xx) padrão do próprio
protocolo são resolvidos pelo `urllib` (não é "seguir um link do
conteúdo", é a mesma página mudando de endereço)."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_TIMEOUT = 10.0
DEFAULT_USER_AGENT = "Claudiao/1.0 (+https://github.com/jhonnatancesar/IA_Claudio)"


@dataclass(frozen=True)
class PageContent:
    """Conteúdo bruto de uma página aberta — sem normalização (TASK-091)."""

    url: str
    final_url: str
    status_code: int
    content_type: str
    body: bytes


class PageFetchError(RuntimeError):
    """Erro ao abrir uma página — timeout, DNS, conexão recusada, status HTTP
    de erro (4xx/5xx) etc."""


def open_page(url: str, timeout: float = DEFAULT_TIMEOUT) -> PageContent:
    """Abre e lê uma única página. Levanta `PageFetchError` para qualquer
    falha de rede/HTTP — não decide se o conteúdo é seguro para abrir
    (isso é a política de PDF, TASK-093, aplicada por quem chama antes de
    invocar esta função para URLs de PDF)."""
    if not url or not url.strip():
        raise ValueError("url não pode ser vazia")

    request = Request(url, headers={"User-Agent": DEFAULT_USER_AGENT})
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read()
            return PageContent(
                url=url,
                final_url=response.geturl(),
                status_code=response.status,
                content_type=response.headers.get_content_type(),
                body=body,
            )
    except HTTPError as exc:
        raise PageFetchError(f"HTTP {exc.code} ao abrir {url}: {exc.reason}") from exc
    except URLError as exc:
        raise PageFetchError(f"falha ao abrir {url}: {exc.reason}") from exc
    except OSError as exc:
        raise PageFetchError(f"falha ao abrir {url}: {exc}") from exc
