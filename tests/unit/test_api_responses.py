"""Testes unitários de `build_success_response` (TASK-072) — formato JSON
padrão de sucesso da API, espelhando `build_error_response` (TASK-008)."""

from app.api.responses import build_success_response


def test_success_response_has_success_true_and_data_key():
    response = build_success_response({"execution_id": "abc", "status": "COMPLETED"})

    assert response == {
        "success": True,
        "data": {"execution_id": "abc", "status": "COMPLETED"},
    }


def test_success_response_preserves_data_reference_unchanged():
    data = {"a": 1, "b": [1, 2, 3]}

    response = build_success_response(data)

    assert response["data"] == data
