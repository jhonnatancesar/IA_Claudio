"""Suíte mínima de testes críticos (TASK-086).

"Cenários reais fixos/repetíveis como critério oficial de regressão"
(`docs/TESTING.md`, seção 45) — diferente dos testes unitários/de
integração por componente já existentes (que continuam sendo a maior
parte da cobertura), estes cenários exercitam o **mínimo utilizável**
(`docs/V1_SCOPE.md`, marco TASK-087) de ponta a ponta, numa única
história cada, para detectar se a integração ENTRE peças já testadas
individualmente quebrou — não só se cada peça isolada continua
funcionando.

Dois cenários fixos, cobrindo o caminho crítico feliz e um caminho
crítico de rejeição:

1. `test_scenario_application_executes_and_appears_everywhere` — o
   fluxo completo que uma aplicação real percorre: cadastro
   (`app.auth.api_keys.create_application`, TASK-011) → `POST
   /v1/executions` (TASK-069) → resposta de sucesso (TASK-072) → o
   resultado aparece em `usage_records` (consumo, TASK-073), em
   `execution_traces` (execuções, TASK-082) e em `GET /panel`
   (TASK-081/082) — prova que a fiação entre API, orquestrador, rastreio
   de consumo, Execution Trace e painel continua íntegra, tudo junto,
   não só peça por peça.
2. `test_scenario_unauthenticated_request_is_rejected_before_any_side_effect`
   — uma aplicação sem API key válida não consegue executar (401) **e**
   isso não deixa rastro nenhum (nem `usage_records`, nem
   `execution_traces`) — prova que a autenticação continua sendo a
   primeira barreira real, não um teatro que algo poderia contornar.

Testes explícitos contra alucinação e uso incorreto de ferramentas
(`docs/TESTING.md`) **não** estão aqui — exigem um modelo Ollama real
baixado (alucinação, `docs/OPEN_QUESTIONS.md` item 3) e o Tool Registry
(uso de ferramentas, TASK-088 em diante), nenhum dos dois existe ainda.
São TASK-142/TASK-144, dedicadas, mais adiante no backlog
(`docs/TESTING.md`) — não desta TASK.

`LocalLLMProvider`/modelo ativo substituídos por fake via
`app.dependency_overrides`, mesmo padrão de
`tests/integration/test_api_executions_integration.py` — nenhum modelo
Ollama real foi baixado nesta máquina ainda.
"""

import json
import re
import uuid

import psycopg
import pytest
from fastapi.testclient import TestClient

from app.api.app import app
from app.api.dependencies import get_active_model, get_local_llm_provider
from app.auth.api_keys import create_application
from app.llm.provider import CompletionRequest, CompletionResponse, LocalLLMProvider
from app.observability.execution_trace import list_execution_traces
from app.usage.usage_model import list_usage_for_application

_EXECUTION_ID_PATTERN = re.compile(r"Execução atual: ([0-9a-fA-F-]+)")


class _AutoRespondProvider(LocalLLMProvider):
    def complete(self, request: CompletionRequest) -> CompletionResponse:
        match = _EXECUTION_ID_PATTERN.search(request.prompt)
        assert match is not None, "prompt sem execution_id reconhecível"
        text = json.dumps(
            {
                "execution_id": match.group(1),
                "action": "RESPOND",
                "confidence": "HIGH",
                "reason": "resposta do cenário crítico",
            },
            ensure_ascii=False,
        )
        return CompletionResponse(text=text, model=request.model)

    def is_available(self) -> bool:
        return True


@pytest.fixture
def registered_application(postgres_dsn):
    name = f"teste_task086_{uuid.uuid4().hex[:12]}"
    application, api_key = create_application(name)
    yield application, api_key
    with psycopg.connect(postgres_dsn) as conn:
        conn.execute("DELETE FROM applications WHERE id = %s", (application.id,))


@pytest.fixture
def client():
    app.dependency_overrides[get_active_model] = lambda: "modelo-de-teste"
    app.dependency_overrides[get_local_llm_provider] = lambda: _AutoRespondProvider()
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_scenario_application_executes_and_appears_everywhere(
    postgres_dsn, registered_application, client
):
    application, api_key = registered_application
    execution_id = None
    try:
        response = client.post(
            "/v1/executions",
            json={
                "objective": "qual é a capital da frança?",
                "usage_type": "chat",
                "web_search_allowed": False,
                "timeout_seconds": 30,
            },
            headers={"Authorization": f"Bearer {api_key}"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        execution_id = body["data"]["execution_id"]
        assert body["data"]["status"] == "COMPLETED"
        assert body["data"]["result"] == "resposta do cenário crítico"

        usage = list_usage_for_application(application.id)
        assert any(record.execution_id == execution_id for record in usage)

        traces = list_execution_traces()
        matching_trace = next((t for t in traces if t.execution_id == execution_id), None)
        assert matching_trace is not None
        assert matching_trace.result == "resposta do cenário crítico"
        assert matching_trace.succeeded is True

        panel_response = client.get("/panel")
        assert execution_id in panel_response.text
        assert "qual é a capital da frança?" in panel_response.text
    finally:
        # `execution_traces` não tem FK/CASCADE com `applications`
        # (TASK-082) — limpa explicitamente para não acumular entre execuções
        # da suíte, mesmo cuidado já tomado pelos outros testes que tocam
        # essa tabela (ex.: tests/integration/test_panel_integration.py).
        if execution_id is not None:
            with psycopg.connect(postgres_dsn) as conn:
                conn.execute(
                    "DELETE FROM execution_traces WHERE execution_id = %s", (execution_id,)
                )


def test_scenario_unauthenticated_request_is_rejected_before_any_side_effect(
    postgres_dsn, registered_application, client
):
    application, _ = registered_application

    response = client.post(
        "/v1/executions",
        json={
            "objective": "essa mensagem nunca deveria ser processada",
            "usage_type": "chat",
            "web_search_allowed": False,
            "timeout_seconds": 30,
        },
        headers={"Authorization": "Bearer cldk_chaveinvalida"},
    )

    assert response.status_code == 401
    assert response.json()["success"] is False

    assert list_usage_for_application(application.id) == []
    traces = list_execution_traces()
    assert not any(
        "essa mensagem nunca deveria ser processada" == t.objective for t in traces
    )
