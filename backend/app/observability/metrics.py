"""Métricas básicas (TASK-080).

Seções 35/44 da especificação mestre (`docs/OBSERVABILITY.md`,
"Métricas"): "taxa de sucesso, uso correto/incorreto de ferramentas,
falhas por ferramenta/provider, respostas bloqueadas por baixa
confiança, falhas de validação, replanejamentos, tempo médio, número de
passos, consumo, erros por provider." "As métricas aparecem no painel
administrativo" (TASK-081 em diante, não implementado aqui).

Cada métrica é uma função pura que agrega sobre uma coleção de
`ExecutionTrace` (TASK-078/079, `app.observability.execution_trace`) ou,
para consumo, sobre `UsageRecord` (TASK-073, `app.usage.usage_model`) —
nenhuma delas lê o banco ou coleta dados sozinha; quem chama já reuniu a
coleção (de onde vem essa coleção — lista em memória de uma sessão,
consulta futura ao banco — não é desta TASK).

Cobertura real vs. lacunas conhecidas, por item da especificação:

- **taxa de sucesso** — `success_rate`, implementada: `trace.result is
  not None` como sinal de sucesso (`ExecutionTrace.finish(result=...)`
  só recebe `None` nos caminhos de falha, TASK-079).
- **tempo médio** — `average_duration_seconds`, implementada, só sobre
  traces já finalizados (`duration_seconds` não `None`).
- **número de passos** — `average_step_count`, implementada.
- **uso... de ferramentas** — `tool_usage_counts`, implementada como
  contagem de frequência (`tools_used`); **não** distingue uso
  "correto"/"incorreto" — isso exigiria saber se uma etapa `USE_TOOL`
  foi rejeitada por `validate_plan` (código `4003`,
  `PLAN_TOOL_NOT_AUTHORIZED`), informação que hoje não chega a
  `ExecutionTrace` (TASK-079 deliberadamente não conectou registro de
  erros ao trace — ver `docs/OBSERVABILITY.md`).
- **consumo** — `request_count_by_status`, implementada sobre
  `UsageRecord` (cobre "número de requisições" por status; medição de
  tokens/volume é o sistema de cotas completo, TASK-108 a TASK-114, sem
  dado nenhum ainda).
- **falhas por ferramenta/provider**, **respostas bloqueadas por baixa
  confiança**, **falhas de validação** (por código específico),
  **replanejamentos**, **erros por provider** — **lacunas conhecidas,
  registradas aqui para não parecerem esquecidas** (mesmo espírito da
  lacuna de retenção de logs em `docs/OBSERVABILITY.md`): nenhuma delas
  tem hoje uma fonte de dado real —
  - guardrails de confiança (TASK-034/035/036) não estão acoplados ao
    fluxo real do orquestrador ainda (HANDOFF.md, item 11 — isso é
    TASK-088 em diante), então "respostas bloqueadas por baixa
    confiança" nunca acontece de verdade no sistema hoje;
  - `replan()` (TASK-027) não incrementa nenhum contador observável;
  - erros/falhas não são registrados em `ExecutionTrace` (TASK-079,
    decisão de escopo deliberada), então não há como atribuir uma
    falha a uma ferramenta ou a um provider específico ainda.
  Construir a coleta desses sinais é trabalho de conexão (mesmo tipo de
  TASK que a TASK-079 fez para etapas/tempos), não desta TASK — inventar
  essa fiação agora seria adiantar funcionalidade não pedida.
"""

from __future__ import annotations

from collections import Counter

from app.observability.execution_trace import ExecutionTrace
from app.usage.usage_model import UsageRecord


def success_rate(traces: list[ExecutionTrace]) -> float | None:
    """Proporção de execuções concluídas com sucesso (`result is not
    None`) sobre o total. `None` se `traces` estiver vazia — sem dado,
    não "0% de sucesso"."""
    if not traces:
        return None
    successes = sum(1 for trace in traces if trace.result is not None)
    return successes / len(traces)


def average_step_count(traces: list[ExecutionTrace]) -> float | None:
    """Média de `step_count` entre as execuções. `None` se `traces`
    estiver vazia."""
    if not traces:
        return None
    return sum(trace.step_count for trace in traces) / len(traces)


def average_duration_seconds(traces: list[ExecutionTrace]) -> float | None:
    """Média de `duration_seconds` entre as execuções já finalizadas
    (`finished_at` definido). `None` se nenhuma execução tiver
    terminado ainda."""
    durations = [
        trace.duration_seconds for trace in traces if trace.duration_seconds is not None
    ]
    if not durations:
        return None
    return sum(durations) / len(durations)


def tool_usage_counts(traces: list[ExecutionTrace]) -> dict[str, int]:
    """Quantas vezes cada ferramenta foi usada, somando `tools_used` de
    todas as execuções. Dicionário vazio se nenhuma ferramenta foi
    usada."""
    counts: Counter[str] = Counter()
    for trace in traces:
        counts.update(trace.tools_used)
    return dict(counts)


def failure_counts_by_error_code(traces: list[ExecutionTrace]) -> dict[int, int]:
    """Quantas vezes cada código de erro (`docs/ERROR_CATALOG.md`)
    apareceu, somando `error_codes` de todas as execuções. Dicionário
    vazio hoje na prática, já que nada ainda chama
    `ExecutionTrace.record_error` (ver docstring do módulo) — a função
    já está correta para quando isso for conectado."""
    counts: Counter[int] = Counter()
    for trace in traces:
        counts.update(trace.error_codes)
    return dict(counts)


def request_count_by_status(records: list[UsageRecord]) -> dict[str, int]:
    """Quantas requisições (`UsageRecord`, TASK-073) terminaram em cada
    `status` (`COMPLETED`/`FAILED`/`CANCELLED`) — a parcela de "consumo"
    que já tem dado real hoje (número de requisições; tokens/volume são
    o sistema de cotas completo, TASK-108 a TASK-114)."""
    counts: Counter[str] = Counter()
    for record in records:
        counts[record.status] += 1
    return dict(counts)
