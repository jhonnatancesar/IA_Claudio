"""Teste de integração: persiste e lê memórias de verdade no PostgreSQL
local (TASK-044). Usa a fixture `postgres_dsn` (tests/integration/conftest.py)
— pula automaticamente se o banco não estiver disponível.
"""

import uuid

import psycopg
import pytest

from app.memory.memory_model import (
    InvalidOwnerTypeError,
    MemoryNotFoundError,
    delete_memory,
    get_memory,
    list_memories_for_owner,
    record_memory_usage,
    save_memory,
    search_memories,
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


def test_save_memory_starts_with_zero_usage(postgres_dsn, unique_owner_id):
    memory = save_memory("USER", unique_owner_id, "conteúdo qualquer")

    assert memory.use_count == 0
    assert memory.last_used_at is None


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


def test_search_memories_finds_matching_content(postgres_dsn, unique_owner_id):
    save_memory("USER", unique_owner_id, "prefere café sem açúcar")
    save_memory("USER", unique_owner_id, "gosta de chá à tarde")

    results = search_memories("USER", unique_owner_id, "café")

    assert len(results) == 1
    assert "café" in results[0].content


def test_search_memories_is_case_insensitive(postgres_dsn, unique_owner_id):
    save_memory("USER", unique_owner_id, "prefere Café sem açúcar")

    results = search_memories("USER", unique_owner_id, "café")

    assert len(results) == 1


def test_search_memories_does_not_return_other_owner_matches(
    postgres_dsn, unique_owner_id
):
    other_owner_id = f"{unique_owner_id}_outro"
    save_memory("USER", other_owner_id, "prefere café sem açúcar")

    try:
        results = search_memories("USER", unique_owner_id, "café")

        assert results == []
    finally:
        with psycopg.connect(postgres_dsn) as conn:
            conn.execute("DELETE FROM memories WHERE owner_id = %s", (other_owner_id,))


def test_search_memories_empty_when_no_match(postgres_dsn, unique_owner_id):
    save_memory("USER", unique_owner_id, "gosta de chá à tarde")

    assert search_memories("USER", unique_owner_id, "café") == []


def test_search_memories_rejects_invalid_owner_type(postgres_dsn):
    with pytest.raises(InvalidOwnerTypeError):
        search_memories("SUPERUSER", "qualquer", "busca")


@pytest.mark.parametrize("query", ["", "   "])
def test_search_memories_rejects_empty_query(postgres_dsn, query):
    with pytest.raises(ValueError):
        search_memories("USER", "qualquer", query)


def test_record_memory_usage_increments_use_count(postgres_dsn, unique_owner_id):
    memory = save_memory("USER", unique_owner_id, "conteúdo qualquer")

    updated = record_memory_usage(memory.id)
    updated_again = record_memory_usage(memory.id)

    assert updated.use_count == 1
    assert updated_again.use_count == 2


def test_record_memory_usage_sets_last_used_at(postgres_dsn, unique_owner_id):
    memory = save_memory("USER", unique_owner_id, "conteúdo qualquer")

    updated = record_memory_usage(memory.id)

    assert updated.last_used_at is not None


def test_record_memory_usage_raises_for_unknown_id(postgres_dsn):
    with pytest.raises(MemoryNotFoundError):
        record_memory_usage(uuid.uuid4())


def test_delete_memory_removes_and_returns_true(postgres_dsn, unique_owner_id):
    memory = save_memory("USER", unique_owner_id, "conteúdo qualquer")

    assert delete_memory(memory.id) is True
    assert get_memory(memory.id) is None


def test_delete_memory_returns_false_for_unknown_id(postgres_dsn):
    assert delete_memory(uuid.uuid4()) is False
