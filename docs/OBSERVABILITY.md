# Observabilidade

Fonte: seções 35 e 44 da especificação mestre.

## Logs

- Níveis: `DEBUG / INFO / WARNING / ERROR`. `DEBUG` desativado por padrão.
- Logs são gravados em **arquivo local e PostgreSQL**. Arquivos usam rotação
  automática; banco usa retenção cíclica.

### Logging local em arquivo (TASK-005)

Implementado em `backend/app/observability/logging_config.py`:
`configure_logging()` configura o logger raiz `claudiao` (nível via
`CLAUDIAO_LOG_LEVEL`, padrão `INFO` — `DEBUG` só se definido explicitamente);
`get_logger(nome)` retorna um logger filho. Rotação por tamanho: 10 MB por arquivo,
5 backups (`RotatingFileHandler`), diretório configurável via `CLAUDIAO_LOG_DIR`
(padrão `logs/`, criado automaticamente se não existir). Sem escrita no PostgreSQL
ainda — isso fica para a TASK-006.

## Execution Trace

Cada execução tem um Execution Trace com: `execution_id`, origem, usuário/aplicação,
horário, duração, intenção, plano, etapas, ferramentas, erros, códigos, consumo,
número de passos, resultado, versão do prompt e versão das regras do orquestrador.

## Métricas

- taxa de sucesso
- uso correto/incorreto de ferramentas
- falhas por ferramenta/provider
- respostas bloqueadas por baixa confiança
- falhas de validação
- replanejamentos
- tempo médio
- número de passos
- consumo
- erros por provider

As métricas aparecem no painel administrativo (ver `PANEL.md`).

## TASKs relacionadas

TASK-078 a TASK-083: Execution Trace, registro de ferramentas/passos/tempos, métricas
básicas, painel web read-only e sua exibição de execuções/erros/logs/consumo.
TASK-005/TASK-006: logging local e logging estruturado no PostgreSQL. TASK-145:
métricas finais de qualidade.
