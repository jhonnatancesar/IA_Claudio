"""Testes unitários do escopo GLOBAL/APPLICATION de conhecimento
(TASK-055) — só o que não toca o banco (validação de consistência
`scope_type`/`scope_id`)."""

import pytest

from app.knowledge.knowledge_model import (
    InvalidKnowledgeScopeError,
    KnowledgeScope,
    list_knowledge_for_scope,
    save_knowledge,
)


def test_save_knowledge_application_scope_requires_scope_id():
    with pytest.raises(InvalidKnowledgeScopeError):
        save_knowledge("fato qualquer", scope_type=KnowledgeScope.APPLICATION)


def test_save_knowledge_global_scope_rejects_scope_id():
    with pytest.raises(InvalidKnowledgeScopeError):
        save_knowledge("fato qualquer", scope_type=KnowledgeScope.GLOBAL, scope_id="app-1")


def test_list_knowledge_for_scope_application_requires_scope_id():
    with pytest.raises(InvalidKnowledgeScopeError):
        list_knowledge_for_scope(KnowledgeScope.APPLICATION)


def test_list_knowledge_for_scope_global_rejects_scope_id():
    with pytest.raises(InvalidKnowledgeScopeError):
        list_knowledge_for_scope(KnowledgeScope.GLOBAL, scope_id="app-1")
