"""Teste de integração: Memory Tool (TASK-046) executando de verdade contra
o PostgreSQL local. Usa a fixture `postgres_dsn`
(tests/conftest.py) — pula automaticamente se o banco não
estiver disponível.
"""

import uuid

import psycopg
import pytest

from app.llm.protocol import Action, Confidence, ModelStep
from app.tools.memory_tool import execute_memory_tool


def _step(parameters: dict) -> ModelStep:
    return ModelStep(
        execution_id="11111111-1111-1111-1111-111111111111",
        action=Action.USE_TOOL,
        confidence=Confidence.MEDIUM,
        reason="usar memória",
        tool="MEMORY",
        parameters=parameters,
    )


@pytest.fixture
def unique_owner_id(postgres_dsn):
    owner_id = f"teste_task046_{uuid.uuid4().hex[:12]}"
    yield owner_id
    with psycopg.connect(postgres_dsn) as conn:
        conn.execute("DELETE FROM memories WHERE owner_id = %s", (owner_id,))


def test_save_operation_persists_memory(postgres_dsn, unique_owner_id):
    result = execute_memory_tool(
        _step(
            {
                "operation": "SAVE",
                "owner_type": "USER",
                "owner_id": unique_owner_id,
                "content": "prefere respostas curtas",
            }
        )
    )

    assert "Memória salva" in result
    with psycopg.connect(postgres_dsn) as conn:
        row = conn.execute(
            "SELECT content FROM memories WHERE owner_id = %s", (unique_owner_id,)
        ).fetchone()
    assert row is not None
    assert row[0] == "prefere respostas curtas"


def test_list_operation_returns_saved_memories(postgres_dsn, unique_owner_id):
    execute_memory_tool(
        _step(
            {
                "operation": "SAVE",
                "owner_type": "USER",
                "owner_id": unique_owner_id,
                "content": "gosta de café",
            }
        )
    )

    result = execute_memory_tool(
        _step({"operation": "LIST", "owner_type": "USER", "owner_id": unique_owner_id})
    )

    assert "gosta de café" in result


def test_list_operation_returns_message_when_empty(postgres_dsn, unique_owner_id):
    result = execute_memory_tool(
        _step({"operation": "LIST", "owner_type": "USER", "owner_id": unique_owner_id})
    )

    assert result == "Nenhuma memória encontrada para este dono."


def test_search_operation_returns_matching_memories(postgres_dsn, unique_owner_id):
    execute_memory_tool(
        _step(
            {
                "operation": "SAVE",
                "owner_type": "USER",
                "owner_id": unique_owner_id,
                "content": "prefere café sem açúcar",
            }
        )
    )

    result = execute_memory_tool(
        _step(
            {
                "operation": "SEARCH",
                "owner_type": "USER",
                "owner_id": unique_owner_id,
                "query": "café",
            }
        )
    )

    assert "café" in result


def test_search_operation_returns_message_when_no_match(postgres_dsn, unique_owner_id):
    result = execute_memory_tool(
        _step(
            {
                "operation": "SEARCH",
                "owner_type": "USER",
                "owner_id": unique_owner_id,
                "query": "café",
            }
        )
    )

    assert result == "Nenhuma memória encontrada para esta busca."
