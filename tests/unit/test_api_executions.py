"""Testes unitários de `_timeout_error_details` (TASK-071) — a construção
dos `details` do erro de timeout ("etapa atual e ferramenta ativa",
`docs/API.md` seção 26), isolada da rota HTTP e sem tocar rede/banco.

Hoje nenhum `tool_executor` está configurado em `POST /v1/executions`
(Tool Registry é TASK-088+), então o caminho real do endpoint nunca chega
a registrar uma etapa `USE_TOOL` antes de um timeout — os testes abaixo
constroem esse estado diretamente em `Execution` para validar a função de
verdade, pronta para quando isso passar a ser alcançável de ponta a
ponta.
"""

from app.api.executions import _timeout_error_details
from app.llm.protocol import Action, Confidence, ModelStep
from app.orchestrator.execution import Execution


def test_details_when_no_step_has_been_recorded_yet():
    execution = Execution.new(origin="chat")
    execution.start()

    details = _timeout_error_details(execution, timeout_seconds=5)

    assert details == {
        "timeout_seconds": 5,
        "current_step": 1,
        "active_tool": None,
    }


def test_details_reports_active_tool_from_last_recorded_use_tool_step():
    execution = Execution.new(origin="chat")
    execution.start()
    execution.add_step(
        ModelStep(
            execution_id=execution.execution_id,
            action=Action.USE_TOOL,
            confidence=Confidence.LOW,
            reason="preciso pesquisar",
            tool="WEB_SEARCH",
        )
    )

    details = _timeout_error_details(execution, timeout_seconds=0.5)

    assert details == {
        "timeout_seconds": 0.5,
        "current_step": 2,
        "active_tool": "WEB_SEARCH",
    }


def test_details_use_tool_count_across_multiple_recorded_steps():
    execution = Execution.new(origin="chat")
    execution.start()
    for i in range(2):
        execution.add_step(
            ModelStep(
                execution_id=execution.execution_id,
                action=Action.USE_TOOL,
                confidence=Confidence.LOW,
                reason="preciso pesquisar de novo",
                tool=f"FERRAMENTA_{i}",
            )
        )
        execution.set_last_observation("resultado")

    details = _timeout_error_details(execution, timeout_seconds=1)

    assert details["current_step"] == 3
    assert details["active_tool"] == "FERRAMENTA_1"
