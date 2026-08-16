"""Testes unitários de geração de API key (TASK-011). Sem banco aqui — criação/
autenticação contra a tabela `applications` está em
tests/integration/test_api_keys_integration.py.
"""

from app.auth.api_keys import generate_api_key


def test_generate_api_key_has_expected_prefix():
    api_key = generate_api_key()

    assert api_key.startswith("cldk_")


def test_generate_api_key_has_high_entropy_length():
    api_key = generate_api_key()

    # 256 bits em base64 urlsafe são ~43 caracteres; com o prefixo, bem mais
    # longo que qualquer coisa memorizável — não é uma senha de usuário.
    assert len(api_key) > 40


def test_generate_api_key_is_random_each_time():
    keys = {generate_api_key() for _ in range(20)}

    assert len(keys) == 20  # nenhuma colisão em 20 gerações
