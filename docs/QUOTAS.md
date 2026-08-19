# Cotas e consumo

Fonte: seção 28 da especificação mestre. Ver também `docs/ORCHESTRATOR.md` (seção
"Complexidade e limitação do chat", que usa a mesma cota como orçamento do chat).

A V1 tem controle de cota **por usuário e por API key**, configurável pelo `ADMIN`.

## O que é medido

- tokens/processamento
- número de requisições
- volume de dados processados/retornados

## Ciclo e avisos

- Ciclo inicial: **diário**, mas o `ADMIN` pode alterar pelo painel.
- O usuário visualiza consumo em percentual.
- Avisos em **80%** e **95%**; bloqueio em **100%**.
- Aplicações não recebem alertas intermediários — apenas erro JSON ao atingir a cota
  (ver `ERROR_CATALOG.md`).

## Perfis especiais

`DEV`/`ADMIN` pode ter limites maiores ou especiais. Usuários pagos ficam preparados
para evolução futura (planos pagos completos ficam fora da V1 — ver
`OUT_OF_SCOPE.md`).

## TASKs relacionadas

TASK-108 a TASK-114: sistema de cotas, medição de tokens/requisições/volume,
renovação diária, alertas 80/95%, bloqueio 100%.

**Implementação (TASK-073):** antes do sistema de cotas completo existir,
`POST /v1/executions` já grava o registro mínimo de que uma requisição
aconteceu — `app.usage.usage_model.record_usage(application_id,
execution_id, status)`, tabela `usage_records`
(`backend/app/db/migrations/0015_usage_records.sql`). Cobre só "número de
requisições" (via `COUNT(*)`); medição de tokens/volume, ciclo de
renovação, avisos 80%/95% e bloqueio em 100% continuam TASK-108 a
TASK-114, não implementados aqui. Ver `backend/app/usage/README.md`.
