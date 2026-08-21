"""Testes unitários de open_page (TASK-090), com `urlopen` mockado — sem
rede real. Validação contra uma página real está em
tests/integration/test_page_fetcher_integration.py."""

from unittest.mock import MagicMock

import pytest
from urllib.error import HTTPError, URLError

from app.web_search import page_fetcher
from app.web_search.page_fetcher import PageFetchError, open_page


def _mock_response(
    *, body: bytes = b"<html></html>", status: int = 200, content_type: str = "text/html", final_url: str | None = None
) -> MagicMock:
    response = MagicMock()
    response.read.return_value = body
    response.status = status
    response.geturl.return_value = final_url or "https://exemplo.com"
    response.headers.get_content_type.return_value = content_type
    response.__enter__.return_value = response
    response.__exit__.return_value = False
    return response


def test_open_page_returns_page_content_on_success(monkeypatch):
    response = _mock_response(body=b"conteudo da pagina", content_type="text/plain")
    monkeypatch.setattr(page_fetcher, "urlopen", MagicMock(return_value=response))

    page = open_page("https://exemplo.com")

    assert page.url == "https://exemplo.com"
    assert page.final_url == "https://exemplo.com"
    assert page.status_code == 200
    assert page.content_type == "text/plain"
    assert page.body == b"conteudo da pagina"


def test_open_page_reports_final_url_after_redirect(monkeypatch):
    response = _mock_response(final_url="https://exemplo.com/destino")
    monkeypatch.setattr(page_fetcher, "urlopen", MagicMock(return_value=response))

    page = open_page("https://exemplo.com/origem")

    assert page.url == "https://exemplo.com/origem"
    assert page.final_url == "https://exemplo.com/destino"


def test_open_page_rejects_empty_url():
    with pytest.raises(ValueError):
        open_page("")


def test_open_page_rejects_blank_url():
    with pytest.raises(ValueError):
        open_page("   ")


def test_open_page_wraps_http_error_as_page_fetch_error(monkeypatch):
    error = HTTPError("https://exemplo.com", 404, "Not Found", {}, None)
    monkeypatch.setattr(page_fetcher, "urlopen", MagicMock(side_effect=error))

    with pytest.raises(PageFetchError):
        open_page("https://exemplo.com")


def test_open_page_wraps_url_error_as_page_fetch_error(monkeypatch):
    error = URLError("nome não resolvido")
    monkeypatch.setattr(page_fetcher, "urlopen", MagicMock(side_effect=error))

    with pytest.raises(PageFetchError):
        open_page("https://dominio-que-nao-existe.invalid")


def test_open_page_wraps_os_error_as_page_fetch_error(monkeypatch):
    monkeypatch.setattr(page_fetcher, "urlopen", MagicMock(side_effect=TimeoutError("tempo esgotado")))

    with pytest.raises(PageFetchError):
        open_page("https://exemplo.com")


def test_open_page_sends_a_user_agent_header(monkeypatch):
    response = _mock_response()
    mock_urlopen = MagicMock(return_value=response)
    monkeypatch.setattr(page_fetcher, "urlopen", mock_urlopen)

    open_page("https://exemplo.com")

    sent_request = mock_urlopen.call_args[0][0]
    assert sent_request.get_header("User-agent") == page_fetcher.DEFAULT_USER_AGENT
