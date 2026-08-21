"""Teste de integração: Knowledge Tool (TASK-053) executando de verdade
contra o PostgreSQL local. Usa a fixture `postgres_dsn`
(tests/conftest.py) — pula automaticamente se o banco não
estiver disponível.
"""

import uuid

import psycopg
import pytest

from app.llm.protocol import Action, Confidence, ModelStep
from app.tools.knowledge_tool import execute_knowledge_tool


def _step(parameters: dict) -> ModelStep:
    return ModelStep(
        execution_id="11111111-1111-1111-1111-111111111111",
        action=Action.USE_TOOL,
        confidence=Confidence.MEDIUM,
        reason="usar conhecimento",
        tool="KNOWLEDGE",
        parameters=parameters,
    )


@pytest.fixture
def created_knowledge_id(postgres_dsn):
    result = execute_knowledge_tool(
        _step({"operation": "SAVE", "content": f"fato de teste {uuid.uuid4().hex[:12]}"})
    )
    knowledge_id = result.split("id=")[1].rstrip(").")
    yield knowledge_id
    with psycopg.connect(postgres_dsn) as conn:
        # `root_id`, não `id`: NEW_VERSION cria linhas novas na mesma
        # linhagem, com `id` diferente do original.
        conn.execute("DELETE FROM knowledge WHERE root_id = %s", (knowledge_id,))


def test_save_operation_persists_knowledge_as_raw(postgres_dsn, created_knowledge_id):
    result = execute_knowledge_tool(_step({"operation": "GET", "knowledge_id": created_knowledge_id}))

    assert result.startswith("[RAW]")


def test_get_operation_returns_message_when_not_found(postgres_dsn):
    result = execute_knowledge_tool(
        _step({"operation": "GET", "knowledge_id": str(uuid.uuid4())})
    )

    assert result == "Nenhum conhecimento encontrado para este id."


def test_advance_operation_moves_to_provisional(postgres_dsn, created_knowledge_id):
    result = execute_knowledge_tool(
        _step(
            {
                "operation": "ADVANCE",
                "knowledge_id": created_knowledge_id,
                "new_status": "PROVISIONAL",
            }
        )
    )

    assert "PROVISIONAL" in result
    fetched = execute_knowledge_tool(_step({"operation": "GET", "knowledge_id": created_knowledge_id}))
    assert fetched.startswith("[PROVISIONAL]")


def test_advance_operation_rejects_skipping_stage(postgres_dsn, created_knowledge_id):
    from app.knowledge.knowledge_model import InvalidKnowledgeStatusTransitionError

    with pytest.raises(InvalidKnowledgeStatusTransitionError):
        execute_knowledge_tool(
            _step(
                {
                    "operation": "ADVANCE",
                    "knowledge_id": created_knowledge_id,
                    "new_status": "CONFIRMED",
                }
            )
        )


def test_new_version_operation_creates_version_and_marks_previous_stale(
    postgres_dsn, created_knowledge_id
):
    result = execute_knowledge_tool(
        _step(
            {
                "operation": "NEW_VERSION",
                "knowledge_id": created_knowledge_id,
                "new_content": "conteúdo atualizado",
                "reason": "correção de erro",
            }
        )
    )

    assert "v2" in result

    old = execute_knowledge_tool(_step({"operation": "GET", "knowledge_id": created_knowledge_id}))
    assert old.startswith("[RAW]")  # a versão antiga continua legível, só não é mais a atual


def test_save_operation_accepts_application_scope(postgres_dsn, created_knowledge_id):
    result = execute_knowledge_tool(
        _step(
            {
                "operation": "SAVE",
                "content": f"fato de aplicação {uuid.uuid4().hex[:8]}",
                "scope_type": "APPLICATION",
                "scope_id": "app-teste-053",
            }
        )
    )
    scope_knowledge_id = result.split("id=")[1].rstrip(").")

    try:
        listed = execute_knowledge_tool(
            _step(
                {
                    "operation": "LIST_SCOPE",
                    "scope_type": "APPLICATION",
                    "scope_id": "app-teste-053",
                }
            )
        )
        assert "fato de aplicação" in listed
    finally:
        with psycopg.connect(postgres_dsn) as conn:
            conn.execute("DELETE FROM knowledge WHERE root_id = %s", (scope_knowledge_id,))


def test_list_scope_operation_returns_message_when_empty(postgres_dsn):
    result = execute_knowledge_tool(
        _step(
            {
                "operation": "LIST_SCOPE",
                "scope_type": "APPLICATION",
                "scope_id": f"app-vazio-{uuid.uuid4().hex[:8]}",
            }
        )
    )

    assert result == "Nenhum conhecimento encontrado para este escopo."


def test_new_version_operation_rejects_stale_knowledge_id(postgres_dsn, created_knowledge_id):
    from app.knowledge.knowledge_model import KnowledgeVersionConflictError

    execute_knowledge_tool(
        _step(
            {
                "operation": "NEW_VERSION",
                "knowledge_id": created_knowledge_id,
                "new_content": "conteúdo v2",
                "reason": "motivo",
            }
        )
    )

    with pytest.raises(KnowledgeVersionConflictError):
        execute_knowledge_tool(
            _step(
                {
                    "operation": "NEW_VERSION",
                    "knowledge_id": created_knowledge_id,
                    "new_content": "conteúdo v3 inválido",
                    "reason": "motivo",
                }
            )
        )


def test_set_confidence_operation_updates_knowledge(postgres_dsn, created_knowledge_id):
    result = execute_knowledge_tool(
        _step(
            {
                "operation": "SET_CONFIDENCE",
                "knowledge_id": created_knowledge_id,
                "confidence": "HIGH",
            }
        )
    )

    assert "HIGH" in result


def test_set_volatility_operation_updates_knowledge(postgres_dsn, created_knowledge_id):
    result = execute_knowledge_tool(
        _step(
            {
                "operation": "SET_VOLATILITY",
                "knowledge_id": created_knowledge_id,
                "volatility": "VOLATILE",
            }
        )
    )

    assert "VOLATILE" in result


def test_add_and_list_evidence_operations(postgres_dsn, created_knowledge_id):
    execute_knowledge_tool(
        _step(
            {
                "operation": "ADD_EVIDENCE",
                "knowledge_id": created_knowledge_id,
                "description": "fonte oficial confirmando o fato",
            }
        )
    )

    result = execute_knowledge_tool(
        _step({"operation": "LIST_EVIDENCE", "knowledge_id": created_knowledge_id})
    )

    assert "fonte oficial confirmando o fato" in result


def test_list_evidence_operation_returns_message_when_empty(postgres_dsn, created_knowledge_id):
    result = execute_knowledge_tool(
        _step({"operation": "LIST_EVIDENCE", "knowledge_id": created_knowledge_id})
    )

    assert result == "Nenhuma evidência encontrada para este conhecimento."


def test_promote_to_confirmed_operation_succeeds_when_eligible(
    postgres_dsn, created_knowledge_id
):
    execute_knowledge_tool(
        _step(
            {
                "operation": "ADVANCE",
                "knowledge_id": created_knowledge_id,
                "new_status": "PROVISIONAL",
            }
        )
    )
    execute_knowledge_tool(
        _step(
            {
                "operation": "SET_CONFIDENCE",
                "knowledge_id": created_knowledge_id,
                "confidence": "HIGH",
            }
        )
    )
    execute_knowledge_tool(
        _step(
            {
                "operation": "ADD_EVIDENCE",
                "knowledge_id": created_knowledge_id,
                "description": "fonte oficial",
            }
        )
    )

    result = execute_knowledge_tool(
        _step({"operation": "PROMOTE_TO_CONFIRMED", "knowledge_id": created_knowledge_id})
    )

    assert "CONFIRMED" in result
    fetched = execute_knowledge_tool(_step({"operation": "GET", "knowledge_id": created_knowledge_id}))
    assert fetched.startswith("[CONFIRMED]")


def test_promote_to_confirmed_operation_rejects_when_not_eligible(
    postgres_dsn, created_knowledge_id
):
    from app.knowledge.promotion_rule import KnowledgePromotionNotEligibleError

    with pytest.raises(KnowledgePromotionNotEligibleError):
        execute_knowledge_tool(
            _step({"operation": "PROMOTE_TO_CONFIRMED", "knowledge_id": created_knowledge_id})
        )
