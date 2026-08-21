"""Teste de integração: health check (TASK-085) contra o PostgreSQL e o
Ollama locais de verdade. Usa a fixture `postgres_dsn`
(tests/integration/conftest.py) — pula automaticamente se o banco não
estiver disponível. As checagens de `modelo/runtime` exigem o Ollama
local rodando (mesma regra de todo o projeto — nunca aceitar isso como
"pulado").
"""

from app.observability.health_check import HealthCheckStatus, run_health_check


def _find(result, name):
    return next(item for item in result.items if item.name == name)


def test_run_health_check_reports_ok_for_postgres(postgres_dsn):
    result = run_health_check()

    assert _find(result, "postgresql").status == HealthCheckStatus.OK


def test_run_health_check_reports_ok_for_queue(postgres_dsn):
    result = run_health_check()

    assert _find(result, "fila").status == HealthCheckStatus.OK


def test_run_health_check_reports_ok_for_model_runtime(postgres_dsn):
    result = run_health_check()

    assert _find(result, "modelo/runtime").status == HealthCheckStatus.OK


def test_run_health_check_skips_tools_and_providers(postgres_dsn):
    result = run_health_check()

    item = _find(result, "ferramentas/providers principais")
    assert item.status == HealthCheckStatus.SKIPPED


def test_run_health_check_reports_failed_critical_config_when_env_missing(
    postgres_dsn, monkeypatch
):
    monkeypatch.delenv("CLAUDIAO_ACTIVE_MODEL", raising=False)
    monkeypatch.delenv("CLAUDIAO_MASTER_KEY_PATH", raising=False)

    result = run_health_check()

    item = _find(result, "configurações críticas")
    assert item.status == HealthCheckStatus.FAILED
    assert "CLAUDIAO_ACTIVE_MODEL" in item.detail
    assert "CLAUDIAO_MASTER_KEY_PATH" in item.detail
    assert result.healthy is False


def test_run_health_check_reports_ok_critical_config_when_env_configured(
    postgres_dsn, monkeypatch, tmp_path
):
    monkeypatch.setenv("CLAUDIAO_ACTIVE_MODEL", "modelo-de-teste")
    monkeypatch.setenv("CLAUDIAO_MASTER_KEY_PATH", str(tmp_path / "master.key"))

    result = run_health_check()

    assert _find(result, "configurações críticas").status == HealthCheckStatus.OK
