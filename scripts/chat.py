"""CLI/chat de teste (TASK-084).

"Chat simples de terminal para teste" — um dos itens do mínimo utilizável
(`docs/V1_SCOPE.md`, marco TASK-087). "A prioridade inicial é aplicações
primeiro — o chat web completo vem depois" (mesma seção): este script
não é uma nova via de entrada privilegiada para o Claudião — é um
cliente HTTP comum de `POST /v1/executions` (`docs/API.md`), exatamente
como qualquer aplicação externa usaria a API. Não bypassa autenticação,
validação, timeout, nem nenhuma regra já implementada (TASK-067 a
TASK-073).

Dois modos, por subcomando:

- `chat create-application <nome>`: cria uma aplicação de teste
  (`app.auth.api_keys.create_application`, TASK-011) e imprime a API key
  **uma única vez** — o banco só guarda o hash (TASK-011), não dá para
  recuperar a chave depois. É a única parte deste script que importa
  `backend.app` e toca o banco diretamente; é um atalho de setup, não o
  chat em si.
- `chat chat --api-key ...`: laço interativo puro sobre HTTP (biblioteca
  padrão — `urllib.request`, sem dependência nova) contra um servidor já
  rodando (`uvicorn app.api.app:app`, porta padrão 8000) — este script
  **não** sobe seu próprio servidor.

Requer que `CLAUDIAO_ACTIVE_MODEL` esteja configurado e um modelo Ollama
de verdade tenha sido baixado para completar uma execução de ponta a
ponta (`docs/OPEN_QUESTIONS.md`, item 3, ainda em aberto nesta máquina)
— sem isso, toda mensagem volta com o erro `3001`/`3002` do catálogo
(`docs/ERROR_CATALOG.md`), o que já é uma verificação válida de que a
autenticação/validação/rede estão funcionando ponta a ponta, mesmo sem
completar de verdade.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

DEFAULT_BASE_URL = "http://127.0.0.1:8000"
DEFAULT_TIMEOUT_SECONDS = 30.0
API_KEY_ENV_VAR = "CLAUDIAO_CLI_API_KEY"
EXIT_WORDS = {"sair", "exit", "quit"}


def build_execution_payload(objective: str, timeout_seconds: float) -> dict:
    """Monta o corpo de `POST /v1/executions` para uma mensagem do chat
    de teste (`app.api.schemas.ExecutionRequest`, TASK-068) —
    `usage_type` fixo `"chat"`, sem pesquisa web (mínimo necessário para
    uma conversa simples), sem `max_steps` (usa o padrão da política,
    `ExecutionPolicy.for_application`)."""
    return {
        "objective": objective,
        "usage_type": "chat",
        "web_search_allowed": False,
        "timeout_seconds": timeout_seconds,
    }


@dataclass(frozen=True)
class ChatTurnResult:
    """Texto pronto para mostrar ao usuário no terminal."""

    ok: bool
    message: str


def format_response(status_code: int, body: dict) -> ChatTurnResult:
    """Interpreta o corpo de resposta de `POST /v1/executions` — formato
    padrão de sucesso/erro (`docs/ERROR_CATALOG.md`, "Formato padrão de
    resposta", TASK-072) — e devolve o texto pronto para mostrar."""
    if body.get("success"):
        result = body.get("data", {}).get("result", "")
        return ChatTurnResult(ok=True, message=result)
    error = body.get("error", {})
    code = error.get("code", "?")
    message = error.get("message", "erro desconhecido")
    return ChatTurnResult(ok=False, message=f"[erro {code}] {message} (HTTP {status_code})")


def call_execution_api(
    base_url: str, api_key: str, objective: str, timeout_seconds: float
) -> ChatTurnResult:
    """Chama `POST /v1/executions` de verdade via HTTP e devolve o
    resultado já formatado. Levanta `urllib.error.URLError` se o
    servidor não responder (ex.: nenhum `uvicorn` rodando em
    `base_url`)."""
    payload = build_execution_payload(objective, timeout_seconds)
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/v1/executions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    # +5s de folga sobre o timeout_seconds do payload — dá tempo do
    # próprio servidor responder com o erro de timeout formatado
    # (TASK-071) em vez do socket do cliente estourar primeiro.
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds + 5) as response:
            body = json.loads(response.read().decode("utf-8"))
            return format_response(response.status, body)
    except urllib.error.HTTPError as exc:
        body = json.loads(exc.read().decode("utf-8"))
        return format_response(exc.code, body)


def run_chat_loop(
    base_url: str,
    api_key: str,
    timeout_seconds: float,
    *,
    input_fn=input,
    output_fn=print,
) -> None:
    """Laço interativo: lê uma linha do terminal, chama a API, mostra o
    resultado, repete até `"sair"`/`"exit"`/`"quit"` ou EOF
    (Ctrl+D/Ctrl+C). `input_fn`/`output_fn` são injetáveis para teste,
    sem precisar de um terminal de verdade."""
    output_fn(f"Claudião — chat de teste (TASK-084). Servidor: {base_url}")
    output_fn('Digite sua mensagem, ou "sair" para encerrar.')
    while True:
        try:
            objective = input_fn("> ").strip()
        except EOFError:
            break
        if not objective:
            continue
        if objective.lower() in EXIT_WORDS:
            break
        try:
            result = call_execution_api(base_url, api_key, objective, timeout_seconds)
        except urllib.error.URLError as exc:
            output_fn(f"[erro de conexão] {exc}")
            continue
        output_fn(result.message)


def create_test_application(name: str) -> None:
    """Cria uma aplicação de teste (`app.auth.api_keys.create_application`,
    TASK-011) e imprime a API key — só existe agora, o banco guarda só o
    hash."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
    from app.auth.api_keys import create_application

    application, api_key = create_application(name)
    print(f"Aplicação '{application.name}' criada (id={application.id}).")
    print(f"API key (guarde agora — não pode ser recuperada depois): {api_key}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Claudião — CLI/chat de teste (TASK-084)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser(
        "create-application", help="cria uma aplicação de teste e imprime a API key"
    )
    create_parser.add_argument("name", help="nome da aplicação (precisa ser único)")

    chat_parser = subparsers.add_parser("chat", help="inicia o chat de teste interativo")
    chat_parser.add_argument(
        "--api-key",
        default=os.environ.get(API_KEY_ENV_VAR),
        help=f"API key da aplicação de teste (ou variável {API_KEY_ENV_VAR})",
    )
    chat_parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    chat_parser.add_argument(
        "--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS, dest="timeout_seconds"
    )

    args = parser.parse_args(argv)

    if args.command == "create-application":
        create_test_application(args.name)
        return

    if not args.api_key:
        parser.error(
            f"API key obrigatória: use --api-key ou defina {API_KEY_ENV_VAR} "
            "(crie uma aplicação de teste com: python scripts/chat.py "
            "create-application <nome>)"
        )
    run_chat_loop(args.base_url, args.api_key, args.timeout_seconds)


if __name__ == "__main__":
    main()
