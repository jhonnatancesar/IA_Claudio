"""Testes unitários do prompt-base do Claudião (TASK-018).

Não testa qualidade de linguagem natural (isso não é testável de forma
determinística) — testa que os elementos exigidos pela especificação mestre
estão presentes: identidade, independência de IA externa, princípios,
hierarquia de prioridade, regras de confiança, contrato do protocolo JSON e
a exigência de responder em PT-BR.
"""

from app.llm.prompt import BASE_PROMPT, PROMPT_VERSION, get_base_prompt


def test_get_base_prompt_returns_base_prompt():
    assert get_base_prompt() == BASE_PROMPT


def test_prompt_version_is_a_non_empty_string():
    assert isinstance(PROMPT_VERSION, str)
    assert PROMPT_VERSION.strip() != ""


def test_prompt_mentions_agent_identity():
    assert "Claudião" in BASE_PROMPT


def test_prompt_states_independence_from_external_ai():
    for name in ("OpenAI", "Gemini", "Claude", "Groq", "OpenRouter"):
        assert name in BASE_PROMPT
    assert "não depende" in BASE_PROMPT


def test_prompt_covers_offline_first_principle():
    assert "Offline-first" in BASE_PROMPT


def test_prompt_covers_priority_hierarchy_in_order():
    hierarchy_terms = [
        "Segurança e guardrails",
        "Política da execução",
        "Pedido atual",
        "Contexto imediato",
        "Memória persistente",
        "Conhecimento confirmado",
        "Conhecimento provisório",
    ]
    positions = [BASE_PROMPT.index(term) for term in hierarchy_terms]

    assert positions == sorted(positions)  # aparecem na ordem certa


def test_prompt_covers_confidence_levels():
    for level in ("LOW", "MEDIUM", "HIGH"):
        assert level in BASE_PROMPT
    assert "não apresente uma conclusão como fato" in BASE_PROMPT


def test_prompt_covers_json_protocol_contract():
    for field_name in ("execution_id", "action", "confidence", "reason", "parameters"):
        assert field_name in BASE_PROMPT
    assert "USE_TOOL" in BASE_PROMPT
    assert "RESPOND" in BASE_PROMPT


def test_prompt_requires_ptbr_response():
    assert "português do Brasil" in BASE_PROMPT


def test_prompt_is_not_empty():
    assert len(BASE_PROMPT.strip()) > 0
