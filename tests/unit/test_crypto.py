"""Testes unitários de criptografia de segredos (TASK-012). Sem banco — só a
lógica de encrypt/decrypt, recebendo a chave já pronta."""

import pytest

from app.auth.crypto import InvalidSecretError, decrypt_secret, encrypt_secret, generate_key


def test_generate_key_is_usable_by_fernet():
    key = generate_key()

    # Só precisa não levantar ao ser usada — round trip já cobre isso melhor,
    # mas aqui garantimos que a chave por si só tem o formato esperado.
    token = encrypt_secret("qualquer coisa", key)
    assert decrypt_secret(token, key) == "qualquer coisa"


def test_generate_key_is_random_each_time():
    assert generate_key() != generate_key()


def test_encrypt_then_decrypt_roundtrip():
    key = generate_key()
    plaintext = "chave-de-api-super-secreta-de-um-provedor-externo"

    token = encrypt_secret(plaintext, key)

    assert token != plaintext
    assert decrypt_secret(token, key) == plaintext


def test_encrypt_rejects_empty_plaintext():
    key = generate_key()

    with pytest.raises(ValueError):
        encrypt_secret("", key)


def test_encrypt_same_plaintext_twice_produces_different_tokens():
    key = generate_key()

    first = encrypt_secret("mesmo segredo", key)
    second = encrypt_secret("mesmo segredo", key)

    assert first != second  # Fernet inclui IV/timestamp aleatórios


def test_decrypt_with_wrong_key_raises_invalid_secret_error():
    token = encrypt_secret("segredo", generate_key())
    wrong_key = generate_key()

    with pytest.raises(InvalidSecretError):
        decrypt_secret(token, wrong_key)


def test_decrypt_tampered_token_raises_invalid_secret_error():
    key = generate_key()
    token = encrypt_secret("segredo", key)
    tampered = token[:-4] + ("AAAA" if not token.endswith("AAAA") else "BBBB")

    with pytest.raises(InvalidSecretError):
        decrypt_secret(tampered, key)


def test_decrypt_garbage_token_raises_invalid_secret_error():
    with pytest.raises(InvalidSecretError):
        decrypt_secret("isso-nao-e-um-token-fernet-valido", generate_key())
