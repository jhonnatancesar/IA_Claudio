# Catálogo de erros

Fonte: seção 36 da especificação mestre.

Erros têm dois níveis: **HTTP padrão** + **código interno do Claudião** no JSON.

## Faixas de código interno

| Faixa | Domínio |
|---|---|
| 1000–1999 | validação |
| 2000–2999 | autenticação/autorização |
| 3000–3999 | ferramentas/providers |
| 4000–4999 | modelo/orquestrador |
| 5000–5999 | memória/conhecimento |
| 6000–6999 | banco/persistência |
| 7000–7999 | cotas/processamento |
| 8000–8999 | integrações/aplicações |
| 9000–9999 | interno/genérico |

## Catálogo interno (TASK-007)

Implementado em `backend/app/errors/catalog.py`: `ErrorDomain` (as 9 faixas
acima), `ErrorDefinition` (código + HTTP + mensagem), `register_error()` (valida
faixa e unicidade do código), `get_error()`, `domain_for_code()`. O catálogo
nasce pequeno — só os erros que a própria fundação já precisa:

| Código | HTTP | Mensagem |
|---|---|---|
| 1001 | 400 | Campo obrigatório ausente |
| 1002 | 400 | Valor de campo inválido |
| 9000 | 500 | Erro interno desconhecido |

Cada TASK futura registra os códigos específicos que precisar quando chegar sua
vez (ex.: TASK-011 pode registrar códigos 2xxx para API key inválida) — não
inventados antecipadamente aqui. O formato de resposta JSON que usa esse
catálogo é escopo da TASK-008, não implementado nesta TASK.

## Formato padrão de erro

```json
{
  "success": false,
  "error": {
    "http_status": 400,
    "code": 1001,
    "message": "Campo obrigatório ausente",
    "details": {
      "field": "query"
    }
  }
}
```

## TASKs relacionadas

TASK-007 e TASK-008. Consumido por `API.md` (erro de timeout, campo obrigatório
ausente), `QUOTAS.md` (erro ao atingir cota) e `OPERATIONS.md` (erro estruturado em
modo de manutenção).
