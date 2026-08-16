# Observabilidade

Fonte: seções 35 e 44 da especificação mestre.

## Logs

- Níveis: `DEBUG / INFO / WARNING / ERROR`. `DEBUG` desativado por padrão.
- Logs são gravados em **arquivo local e PostgreSQL**. Arquivos usam rotação
  automática; banco usa retenção cíclica.

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
