# Painel

Fonte: seções 37 e 38 da especificação mestre.

## Painel inicial (somente leitura)

Antes do painel administrativo completo, existe um painel web somente leitura para
acompanhar aplicações e execuções:

- fila
- execução atual
- status
- logs recentes
- erros
- consumo básico
- resultados das execuções

## Painel administrativo completo

- status geral
- logs
- erros
- métricas
- cotas
- usuários
- API keys
- providers
- ordem dos providers
- modelo ativo
- configurações
- manutenção
- reinício
- backups
- restores
- atualizações
- blacklist
- auditoria de reputação de fontes
- métricas de qualidade

## Regras de acesso e segurança

- Ações críticas exigem confirmação explícita, senha do `ADMIN` e registro no banco.
- A sessão administrativa tem logout automático por inatividade com tempo fixo na V1.
- O `ADMIN` pode visualizar a reputação e histórico das fontes, mas **não** editar a
  reputação manualmente (a reputação é calculada dinamicamente — ver
  `TRUST_GUARDRAILS.md`).

## TASKs relacionadas

- Painel read-only: TASK-081 a TASK-083.
- Painel administrativo completo: TASK-115 a TASK-122 (evolução para ADMIN, gestão de
  usuários/API keys/providers/cotas/configurações, reautenticação para ações
  críticas, logout por inatividade).
