"""Hash e verificação de senha (TASK-009).

Sem dependência externa nova: PBKDF2-HMAC-SHA256 via `hashlib`, algoritmo
aprovado pela OWASP para hashing de senha. 600.000 iterações (recomendação OWASP
2023 para PBKDF2-SHA256) e salt aleatório de 16 bytes por senha.
"""

from __future__ import annotations

import hashlib
import hmac
import os

_ALGORITHM = "pbkdf2_sha256"
_ITERATIONS = 600_000
_SALT_BYTES = 16


def hash_password(password: str) -> str:
    """Gera o hash de uma senha em texto plano, pronto para persistir.

    Formato: `pbkdf2_sha256$<iterações>$<salt em hex>$<hash em hex>` — os
    parâmetros ficam junto do hash para permitir aumentar `_ITERATIONS` no
    futuro sem invalidar hashes antigos (verificados com as iterações
    originais deles).
    """
    if not password:
        raise ValueError("senha não pode ser vazia")
    salt = os.urandom(_SALT_BYTES)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _ITERATIONS)
    return f"{_ALGORITHM}${_ITERATIONS}${salt.hex()}${derived.hex()}"


def verify_password(password: str, encoded_hash: str) -> bool:
    """Verifica uma senha em texto plano contra um hash gerado por
    `hash_password`. Nunca levanta exceção para entrada malformada — retorna
    `False`. Comparação em tempo constante (`hmac.compare_digest`)."""
    try:
        algorithm, iterations_str, salt_hex, hash_hex = encoded_hash.split("$")
        if algorithm != _ALGORITHM:
            return False
        iterations = int(iterations_str)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
    except (ValueError, AttributeError):
        return False

    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(derived, expected)
