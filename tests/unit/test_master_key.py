"""Testes unitários da chave mestra externa ao banco (TASK-013). Sem banco —
só arquivo local (via `tmp_path`)."""

import pytest

from app.auth.crypto import decrypt_secret, encrypt_secret
from app.auth.master_key import (
    MasterKeyPathNotConfiguredError,
    load_or_create_master_key,
)


def test_creates_key_file_when_missing(tmp_path):
    key_path = tmp_path / "master.key"
    assert not key_path.exists()

    key = load_or_create_master_key(key_path)

    assert key_path.exists()
    assert key_path.read_bytes() == key


def test_loads_existing_key_without_overwriting(tmp_path):
    key_path = tmp_path / "master.key"
    first = load_or_create_master_key(key_path)

    second = load_or_create_master_key(key_path)

    assert second == first  # não gera uma chave nova por cima


def test_creates_parent_directories_when_missing(tmp_path):
    key_path = tmp_path / "nested" / "dir" / "master.key"

    load_or_create_master_key(key_path)

    assert key_path.exists()


def test_raises_when_no_path_and_no_env_var(monkeypatch):
    monkeypatch.delenv("CLAUDIAO_MASTER_KEY_PATH", raising=False)

    with pytest.raises(MasterKeyPathNotConfiguredError):
        load_or_create_master_key()


def test_uses_env_var_when_no_explicit_path(monkeypatch, tmp_path):
    key_path = tmp_path / "master.key"
    monkeypatch.setenv("CLAUDIAO_MASTER_KEY_PATH", str(key_path))

    key = load_or_create_master_key()

    assert key_path.exists()
    assert key_path.read_bytes() == key


def test_explicit_path_takes_priority_over_env_var(monkeypatch, tmp_path):
    env_path = tmp_path / "from_env.key"
    explicit_path = tmp_path / "explicit.key"
    monkeypatch.setenv("CLAUDIAO_MASTER_KEY_PATH", str(env_path))

    load_or_create_master_key(explicit_path)

    assert explicit_path.exists()
    assert not env_path.exists()


def test_loaded_key_works_with_crypto_module(tmp_path):
    key_path = tmp_path / "master.key"
    key = load_or_create_master_key(key_path)

    token = encrypt_secret("segredo real", key)
    reloaded_key = load_or_create_master_key(key_path)

    assert decrypt_secret(token, reloaded_key) == "segredo real"
