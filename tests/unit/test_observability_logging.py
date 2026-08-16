"""Testes unitários do logging local rotativo (TASK-005).

Cobre: nível padrão (DEBUG desativado por padrão), leitura do nível via ambiente,
criação automática do diretório de log, rotação configurada e escrita efetiva de
mensagens no arquivo — conforme docs/OBSERVABILITY.md e docs/tasks/TASK-005.md.
"""

import importlib
import logging
import logging.handlers

import pytest

from app.observability import logging_config


@pytest.fixture(autouse=True)
def _reset_logging_state(monkeypatch, tmp_path):
    """Isola cada teste: log dir próprio e estado 'configurado' resetado."""
    monkeypatch.setenv("CLAUDIAO_LOG_DIR", str(tmp_path))
    monkeypatch.delenv("CLAUDIAO_LOG_LEVEL", raising=False)
    monkeypatch.delenv("CLAUDIAO_LOG_FILE", raising=False)
    importlib.reload(logging_config)
    yield
    logging.getLogger("claudiao").handlers.clear()


def test_default_level_is_info_not_debug(tmp_path):
    root = logging_config.configure_logging()
    assert root.level == logging.INFO
    assert root.level != logging.DEBUG


def test_explicit_debug_level_is_respected(monkeypatch, tmp_path):
    monkeypatch.setenv("CLAUDIAO_LOG_LEVEL", "DEBUG")
    root = logging_config.configure_logging(force=True)
    assert root.level == logging.DEBUG


def test_invalid_level_falls_back_to_default(monkeypatch, tmp_path):
    monkeypatch.setenv("CLAUDIAO_LOG_LEVEL", "NOT_A_LEVEL")
    root = logging_config.configure_logging(force=True)
    assert root.level == logging.INFO


def test_log_directory_is_created_automatically(tmp_path):
    log_dir = tmp_path / "nested" / "logs"
    import os

    os.environ["CLAUDIAO_LOG_DIR"] = str(log_dir)
    try:
        logging_config.configure_logging(force=True)
        assert log_dir.is_dir()
    finally:
        del os.environ["CLAUDIAO_LOG_DIR"]


def test_handler_is_rotating_with_expected_limits(tmp_path):
    root = logging_config.configure_logging(force=True)
    assert len(root.handlers) == 1
    handler = root.handlers[0]
    assert isinstance(handler, logging.handlers.RotatingFileHandler)
    assert handler.maxBytes == logging_config.MAX_BYTES
    assert handler.backupCount == logging_config.BACKUP_COUNT


def test_get_logger_writes_message_to_file(tmp_path):
    logger = logging_config.get_logger("test")
    logger.info("mensagem de teste do Claudião")

    for handler in logging.getLogger("claudiao").handlers:
        handler.flush()

    log_file = tmp_path / logging_config.DEFAULT_LOG_FILE
    assert log_file.exists()
    content = log_file.read_text(encoding="utf-8")
    assert "mensagem de teste do Claudião" in content
    assert "claudiao.test" in content


def test_configure_logging_is_idempotent_without_force(tmp_path):
    first = logging_config.configure_logging()
    second = logging_config.configure_logging()
    assert first is second
    assert len(second.handlers) == 1
