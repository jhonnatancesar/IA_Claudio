"""Testes unitários de hash e verificação de senha (TASK-009)."""

import pytest

from app.auth.password import hash_password, verify_password


def test_hash_password_rejects_empty_password():
    with pytest.raises(ValueError):
        hash_password("")


def test_hash_password_produces_different_hash_each_time():
    first = hash_password("senha-correta")
    second = hash_password("senha-correta")

    assert first != second  # salts diferentes


def test_hash_password_has_expected_format():
    encoded = hash_password("senha-correta")

    algorithm, iterations, salt_hex, hash_hex = encoded.split("$")
    assert algorithm == "pbkdf2_sha256"
    assert int(iterations) >= 600_000
    bytes.fromhex(salt_hex)  # não levanta
    bytes.fromhex(hash_hex)  # não levanta


def test_verify_password_accepts_correct_password():
    encoded = hash_password("senha-correta")

    assert verify_password("senha-correta", encoded) is True


def test_verify_password_rejects_wrong_password():
    encoded = hash_password("senha-correta")

    assert verify_password("senha-errada", encoded) is False


def test_verify_password_rejects_malformed_hash():
    assert verify_password("qualquer-senha", "isso-nao-e-um-hash-valido") is False


def test_verify_password_rejects_unknown_algorithm():
    tampered = "outro_algoritmo$600000$" + "aa" * 16 + "$" + "bb" * 32
    assert verify_password("senha-correta", tampered) is False


def test_verify_password_rejects_tampered_hash():
    encoded = hash_password("senha-correta")
    algorithm, iterations, salt_hex, hash_hex = encoded.split("$")
    tampered_hash_hex = ("0" if hash_hex[0] != "0" else "1") + hash_hex[1:]
    tampered = f"{algorithm}${iterations}${salt_hex}${tampered_hash_hex}"

    assert verify_password("senha-correta", tampered) is False
