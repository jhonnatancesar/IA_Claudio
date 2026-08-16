"""Criptografia de segredos em repouso (TASK-012).

Usa `Fernet` (`cryptography.fernet`) — criptografia simétrica autenticada
(AES-128 em CBC + HMAC-SHA256), a abstração de alto nível recomendada pelo
próprio pacote `cryptography` para "criptografar um blob com uma chave
simétrica" (docs/SECURITY.md: "API keys, tokens e segredos externos são
criptografados em repouso").

Escopo estrito desta TASK: só `encrypt_secret`/`decrypt_secret`, recebendo a
chave já pronta. De onde a chave mestra vem e como fica protegida fora do
PostgreSQL é a TASK-013, não implementada aqui.
"""

from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken


class InvalidSecretError(ValueError):
    """Levantado quando um token não pôde ser decifrado — chave errada, token
    corrompido/adulterado, ou que nunca foi gerado por `encrypt_secret`."""


def generate_key() -> bytes:
    """Gera uma chave nova, no formato esperado por `Fernet` (32 bytes,
    urlsafe-base64). Quem persiste essa chave como chave mestra é a TASK-013."""
    return Fernet.generate_key()


def encrypt_secret(plaintext: str, key: bytes) -> str:
    """Criptografa um segredo em texto plano. Retorna um token urlsafe-base64
    que inclui timestamp e autenticação — `Fernet` detecta adulteração na
    hora de decifrar."""
    if not plaintext:
        raise ValueError("plaintext não pode ser vazio")
    fernet = Fernet(key)
    token = fernet.encrypt(plaintext.encode("utf-8"))
    return token.decode("utf-8")


def decrypt_secret(token: str, key: bytes) -> str:
    """Decifra um token gerado por `encrypt_secret`. Levanta
    `InvalidSecretError` se a chave estiver errada ou o token for
    inválido/adulterado."""
    fernet = Fernet(key)
    try:
        plaintext = fernet.decrypt(token.encode("utf-8"))
    except InvalidToken as exc:
        raise InvalidSecretError("token inválido ou chave incorreta") from exc
    return plaintext.decode("utf-8")
