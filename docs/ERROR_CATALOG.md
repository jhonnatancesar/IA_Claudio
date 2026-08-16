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

Códigos específicos dentro de cada faixa serão definidos durante a implementação das
TASKs TASK-007 (catálogo interno de erros) e TASK-008 (resposta padrão de erro JSON) —
não inventados antecipadamente nesta organização.

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
