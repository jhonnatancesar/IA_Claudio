"""Teste de integração: persiste e lê memórias de verdade no PostgreSQL
local (TASK-044). Usa a fixture `postgres_dsn` (tests/integration/conftest.py)
— pula automaticamente se o banco não estiver disponível.
"""

import uuid

import psycopg
import pytest

from app.memory.memory_model import (
    InvalidOwnerTypeError,
    get_memory,
    list_memories_for_owner,
    save_memory,
)


@pytest.fixture
def unique_owner_id(postgres_dsn):
    """`owner_id` isolado por execução, e limpeza garantida ao final do teste."""
    owner_id = f"teste_task044_{uuid.uuid4().hex[:12]}"
    yield owner_id
    with psycopg.connect(postgres_dsn) as conn:
        conn.execute("DELETE FROM memories WHERE owner_id = %s", (owner_id,))


def test_save_memory_persists_and_is_readable_by_id(postgres_dsn, unique_owner_id):
    memory = save_memory("USER", unique_owner_id, "prefere respostas curtas")

    fetched = get_memory(memory.id)

    assert fetched is not None
    assert fetched.owner_type == "USER"
    assert fetched.owner_id == unique_owner_id
    assert fetched.content == "prefere respostas curtas"


def test_save_memory_accepts_application_owner_type(postgres_dsn, unique_owner_id):
    memory = save_memory("APPLICATION", unique_owner_id, "contexto persistido")

    assert memory.owner_type == "APPLICATION"


def test_save_memory_rejects_invalid_owner_type(postgres_dsn, unique_owner_id):
    with pytest.raises(InvalidOwnerTypeError):
        save_memory("SUPERUSER", unique_owner_id, "conteúdo qualquer")


def test_get_memory_returns_none_for_unknown_id(postgres_dsn):
    assert get_memory(uuid.uuid4()) is None


def test_list_memories_for_owner_returns_only_that_owner(postgres_dsn, unique_owner_id):
    other_owner_id = f"{unique_owner_id}_outro"
    save_memory("USER", unique_owner_id, "memória do dono A")
    save_memory("USER", other_owner_id, "memória do dono B")

    try:
        memories = list_memories_for_owner("USER", unique_owner_id)

        assert len(memories) == 1
        assert memories[0].content == "memória do dono A"
        assert memories[0].owner_id == unique_owner_id
    finally:
        with psycopg.connect(postgres_dsn) as conn:
            conn.execute("DELETE FROM memories WHERE owner_id = %s", (other_owner_id,))


def test_list_memories_for_owner_does_not_mix_owner_types(postgres_dsn, unique_owner_id):
    save_memory("USER", unique_owner_id, "memória de usuário")
    save_memory("APPLICATION", unique_owner_id, "memória de aplicação")

    user_memories = list_memories_for_owner("USER", unique_owner_id)
    app_memories = list_memories_for_owner("APPLICATION", unique_owner_id)

    assert len(user_memories) == 1
    assert user_memories[0].content == "memória de usuário"
    assert len(app_memories) == 1
    assert app_memories[0].content == "memória de aplicação"


def test_list_memories_for_owner_empty_when_none_exist(postgres_dsn, unique_owner_id):
    assert list_memories_for_owner("USER", unique_owner_id) == []


def test_list_memories_for_owner_rejects_invalid_owner_type(postgres_dsn):
    with pytest.raises(InvalidOwnerTypeError):
        list_memories_for_owner("SUPERUSER", "qualquer")
