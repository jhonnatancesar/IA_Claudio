"""Teste de integração: Knowledge Tool (TASK-053) executando de verdade
contra o PostgreSQL local. Usa a fixture `postgres_dsn`
(tests/integration/conftest.py) — pula automaticamente se o banco não
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
        conn.execute("DELETE FROM knowledge WHERE id = %s", (knowledge_id,))


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
