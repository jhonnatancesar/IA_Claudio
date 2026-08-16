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
(padrão `logs/`, criado automaticamente se não existir).

### Logging estruturado no PostgreSQL (TASK-006)

Implementado em `backend/app/observability/postgres_log_handler.py`
(`PostgresLogHandler`) e gravado na tabela `logs`
(`backend/app/db/migrations/0002_logs.sql`: `timestamp`, `level`, `logger`,
`message`, `context jsonb`). `configure_logging()` anexa esse handler
automaticamente quando `CLAUDIAO_POSTGRES_*` está disponível no ambiente
(`build_dsn_from_env()`); sem essas variáveis, o logging segue normalmente só em
arquivo — nunca é um requisito rígido. Uma conexão nova é aberta por mensagem
(sem pool — otimização futura, se o volume exigir); falhas de escrita no banco não
derrubam a aplicação nem o arquivo local.

**Lacuna conhecida:** a especificação (seção 35) descreve retenção cíclica para os
logs em banco, mas não há TASK numerada dedicada a essa limpeza no backlog — não
implementada ainda. Registrado aqui para não ser esquecida quando uma TASK futura
tratar de retenção/limpeza de dados operacionais.

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
