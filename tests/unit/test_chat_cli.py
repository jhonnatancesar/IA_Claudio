"""Testes unitários do CLI/chat de teste (TASK-084) — funções puras e o
laço interativo com entrada/saída e chamada HTTP injetadas, sem tocar
rede/banco/terminal de verdade.

`scripts/chat.py` fica fora de `backend/app` (é um cliente HTTP puro,
não faz parte do pacote do núcleo) — inserido no `sys.path` manualmente
aqui, mesmo padrão que o próprio script usa para `backend/app` no modo
`create-application`.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import chat  # noqa: E402


def test_build_execution_payload_shape():
    payload = chat.build_execution_payload("qual é a capital da frança?", 30.0)

    assert payload == {
        "objective": "qual é a capital da frança?",
        "usage_type": "chat",
        "web_search_allowed": False,
        "timeout_seconds": 30.0,
    }


def test_format_response_success():
    body = {"success": True, "data": {"execution_id": "exec-1", "result": "resposta pronta"}}

    result = chat.format_response(200, body)

    assert result.ok is True
    assert result.message == "resposta pronta"


def test_format_response_error_includes_code_and_message():
    body = {
        "success": False,
        "error": {"code": 3001, "message": "Nenhum modelo local ativo configurado"},
    }

    result = chat.format_response(503, body)

    assert result.ok is False
    assert "3001" in result.message
    assert "Nenhum modelo local ativo configurado" in result.message
    assert "503" in result.message


def test_run_chat_loop_exits_on_sair(monkeypatch):
    inputs = iter(["sair"])
    outputs: list[str] = []

    def fake_call(*args, **kwargs):
        raise AssertionError("não deveria chamar a API depois de 'sair'")

    monkeypatch.setattr(chat, "call_execution_api", fake_call)

    chat.run_chat_loop(
        "http://localhost:8000",
        "chave",
        30.0,
        input_fn=lambda _: next(inputs),
        output_fn=outputs.append,
    )

    assert any("chat de teste" in line for line in outputs)


def test_run_chat_loop_exits_on_eof():
    def raise_eof(_):
        raise EOFError

    outputs: list[str] = []

    chat.run_chat_loop(
        "http://localhost:8000", "chave", 30.0, input_fn=raise_eof, output_fn=outputs.append
    )

    assert outputs  # só as mensagens de boas-vindas, sem travar


def test_run_chat_loop_skips_empty_input(monkeypatch):
    inputs = iter(["   ", "sair"])
    calls = []
    monkeypatch.setattr(chat, "call_execution_api", lambda *a, **k: calls.append(a))

    chat.run_chat_loop(
        "http://localhost:8000",
        "chave",
        30.0,
        input_fn=lambda _: next(inputs),
        output_fn=lambda _: None,
    )

    assert calls == []


def test_run_chat_loop_prints_result_for_real_message(monkeypatch):
    inputs = iter(["oi", "sair"])
    outputs: list[str] = []

    def fake_call(base_url, api_key, objective, timeout_seconds):
        assert objective == "oi"
        return chat.ChatTurnResult(ok=True, message="olá!")

    monkeypatch.setattr(chat, "call_execution_api", fake_call)

    chat.run_chat_loop(
        "http://localhost:8000",
        "chave",
        30.0,
        input_fn=lambda _: next(inputs),
        output_fn=outputs.append,
    )

    assert "olá!" in outputs


def test_run_chat_loop_reports_connection_error_and_continues(monkeypatch):
    import urllib.error

    inputs = iter(["oi", "sair"])
    outputs: list[str] = []

    def fake_call(*args, **kwargs):
        raise urllib.error.URLError("conexão recusada")

    monkeypatch.setattr(chat, "call_execution_api", fake_call)

    chat.run_chat_loop(
        "http://localhost:8000",
        "chave",
        30.0,
        input_fn=lambda _: next(inputs),
        output_fn=outputs.append,
    )

    assert any("erro de conexão" in line for line in outputs)


def test_main_requires_api_key_for_chat_command(monkeypatch, capsys):
    monkeypatch.delenv(chat.API_KEY_ENV_VAR, raising=False)

    with pytest.raises(SystemExit):
        chat.main(["chat"])

    captured = capsys.readouterr()
    assert "API key obrigatória" in captured.err
